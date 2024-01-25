from datetime import date, datetime


def get_today(for_files: bool = False):
    """Return today's date."""
    if for_files:
        return date.today().strftime("%Y%m%d")
    return date.today().strftime("%Y-%m-%d")


def get_now(for_files: bool = False):
    """Return today's date.

    Args:
        for_files (bool): if True, return now's date for files (without - between them)

    """
    now = datetime.now()
    if for_files:
        return now.strftime("%Y%m%d__%H%M%S")
    return now.strftime("%Y-%m-%d %H:%M:%S")


def get_day(date_str: str, for_files: bool = False):
    """Return today's date.

    Args:
        for_files (bool): if True, return now's date for files (without - between them)

    """
    current_date = datetime.strptime(date_str, "%d/%m/%Y")
    if for_files:
        return current_date.strftime("%Y%m%d")
    return current_date.strftime("%Y-%m-%d")


def convert_eu_to_us(date_str: str):
    """Convert american date to european date."""
    if not date_str:
        return None
    return datetime.strptime(date_str, "%d/%m/%Y").strftime("%m/%d/%Y")


def convert_duration_to_number(duration_str: str):
    """Convert duration to number."""
    if not duration_str:
        return None

    (m, s) = duration_str.split(":")
    return float(m) * 60 + float(s)
