from datetime import datetime

def datetimeformat(value, format='%d.%m.%Y %H:%M'):
    try:
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        return value.strftime(format)
    except Exception:
        return value
