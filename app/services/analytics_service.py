import ipaddress
import logging
from time import monotonic

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from ..models.traffic_log import TrafficLog
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

RETENTION_DAYS = 90
_PURGE_INTERVAL_SECONDS = 24 * 60 * 60
# shortcut: purge runs per worker, at most daily, driven by traffic; upgrade to a scheduled job if traffic can be zero for days
_last_purge = float("-inf")


def anonymize_ip(ip: str | None) -> str | None:
    """Keep the network, drop the host: IPv4 -> /24, IPv6 -> /48 (KVKK data minimisation)."""
    if not ip:
        return None
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return None
    if isinstance(addr, ipaddress.IPv6Address) and addr.ipv4_mapped:
        addr = addr.ipv4_mapped
    if isinstance(addr, ipaddress.IPv4Address):
        return str(ipaddress.IPv4Address(int(addr) & 0xFFFFFF00))
    return str(ipaddress.IPv6Address(int(addr) & (((1 << 48) - 1) << 80)))


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def log_request(self, path: str, method: str, ip: str, user_agent: str):
        log = TrafficLog(
            path=path[:255],
            method=method,
            ip_address=anonymize_ip(ip),
            user_agent=user_agent,
        )
        self.db.add(log)
        self.db.commit()
        self._purge_if_due()

    def purge_old_logs(self, days: int = RETENTION_DAYS) -> int:
        cutoff = datetime.now() - timedelta(days=days)
        deleted = (
            self.db.query(TrafficLog)
            .filter(TrafficLog.timestamp < cutoff)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted

    def _purge_if_due(self):
        global _last_purge
        if monotonic() - _last_purge < _PURGE_INTERVAL_SECONDS:
            return
        _last_purge = monotonic()
        try:
            self.purge_old_logs()
        except Exception:
            self.db.rollback()
            logger.exception("Traffic log retention purge failed")

    def get_stats(self, days: int = 30):
        # Time range
        start_date = datetime.now() - timedelta(days=days)

        # Daily Traffic (for graph)
        daily_traffic = (
            self.db.query(
                func.date(TrafficLog.timestamp).label("date"),
                func.count(TrafficLog.id).label("count"),
            )
            .filter(TrafficLog.timestamp >= start_date)
            .group_by(func.date(TrafficLog.timestamp))
            .order_by(func.date(TrafficLog.timestamp))
            .all()
        )

        # Today's count
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_count = (
            self.db.query(TrafficLog)
            .filter(TrafficLog.timestamp >= today_start)
            .count()
        )

        # Total count
        total_count = self.db.query(TrafficLog).count()

        # Top Pages
        top_pages = (
            self.db.query(TrafficLog.path, func.count(TrafficLog.id).label("count"))
            .group_by(TrafficLog.path)
            .order_by(desc("count"))
            .limit(5)
            .all()
        )

        return {
            "daily_traffic": [
                {"date": str(d.date), "count": d.count} for d in daily_traffic
            ],
            "today_visitors": today_count,
            "total_visitors": total_count,
            "top_pages": [{"path": p.path, "count": p.count} for p in top_pages],
        }
