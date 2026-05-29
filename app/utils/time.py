from datetime import datetime


def send_current_time():
    now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M:%S")