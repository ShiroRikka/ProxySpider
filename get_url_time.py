from datetime import datetime, timedelta



def get_url_time():
    current_time = datetime.now()
    print(current_time)
    noon_time = current_time.replace(hour=12, minute=0, second=0, microsecond=0)

    if current_time > noon_time:
        # 如果当前时间超过12点，使用当前日期
        return current_time.strftime("%Y-%m-%d")
    else:
        # 如果当前时间未超过12点，使用前一天日期
        yesterday = current_time - timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d")

