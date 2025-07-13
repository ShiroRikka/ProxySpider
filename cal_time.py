from datetime import datetime, timedelta


def today():
    time = datetime.now()
    return time.strftime("%Y-%m-%d")


def yesterday():
    time = datetime.now()
    day_1 = time - timedelta(1)
    return day_1.strftime("%Y-%m-%d")


def tomo():
    time = datetime.now()
    day_1 = time + timedelta(1)
    return day_1.strftime("%Y-%m-%d")
