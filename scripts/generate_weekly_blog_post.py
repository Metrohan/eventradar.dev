#!/usr/bin/env python3
"""Generate the next weekly event roundup. Safe to run repeatedly."""

import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
sys.path.insert(0, project_root)

from app.core.database import SessionLocal
from app.services.weekly_content_service import WeeklyContentService


def main() -> None:
    db = SessionLocal()
    try:
        post = WeeklyContentService(db).generate()
        print(f"Haftalık blog yazısı hazır: {post.slug}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
