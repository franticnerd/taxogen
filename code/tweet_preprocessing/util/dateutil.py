from datetime import datetime


class DateUtil:
    @staticmethod
    def date_parser(date, date_format='%a %b %d %H:%M:%S %Z %Y'):
        return datetime.strptime(date, date_format)

    @staticmethod
    def timedelta_to_hour(date1, date2):
        timedelta = date1 - date2
        return abs(timedelta.days * 24 + timedelta.seconds * 0.000277778 + timedelta.microseconds * 2.77778e-10)
