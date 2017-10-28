"""Guidelines

    * All datetimes should be converted to UTC before processing/storage.
    * ISO 8601 format should be used in storage with explicit timezone information ('Z' in case of UTC).
    * Datetime objects with no tzinfo (timezone unaware) should be considered as a "bug" in the application.

"""

from __future__ import absolute_import

import datetime

import pytz


class TimeZone:
    """ This class provides timezones """
    UTC = 'UTC'

    # US timezones
    CENTRAL = 'US/Central'
    EASTERN = 'US/Eastern'
    PACIFIC = 'US/Pacific'
    MOUNTAIN = 'US/Mountain'

    # ASIA timezones
    JAPAN = 'Asia/Tokyo'
    KOREA = 'Asia/Seoul'
    INDIA = 'Asia/Kolkata'
    CHINA = 'Asia/Shanghai'
    SINGAPORE = 'Asia/Singapore'


class Format:
    # 2015-11-01T03:36:49Z
    # 2015-11-01T03:36:49.578427Z
    ISO = '%Y-%m-%dT%H:%M:%SZ'
    ISO_PRECISE = '%Y-%m-%dT%H:%M:%S.%fZ'

    # 2015-11-01 03:36:49
    STANDARD = '%Y-%m-%d %H:%M:%S'

    # Nov 11 03:36 AM
    HUMAN_READABLE = '%b %d %-I:%M %p'


class Datetime(object):
    """Guidelines

        * All datetimes should be converted to UTC before processing/storage.
        * ISO 8601 format should be used in storage with explicit timezone information ('Z' in case of UTC).
        * Datetime objects with no tzinfo (timezone unaware) should be considered as a "bug" in the application.

        This class provides convenience methods for timezone and date-time format conversions.

        * Currently this class is not thread safe
        * The datetime objects which are not timezone aware are considered bugs
    """

    @classmethod
    def last_day_of_year(cls, dt_obj):
        last_month_of_the_year = dt_obj.replace(month=12)
        return cls.last_day_of_month(last_month_of_the_year)

    @classmethod
    def last_day_of_month(cls, dt_obj):
        next_month = dt_obj.replace(day=28) + datetime.timedelta(days=4)
        return next_month - datetime.timedelta(days=next_month.day)

    @classmethod
    def utc_now(cls):
        """ returns timezone aware datetime object in with current date and time in utc """
        return pytz.utc.localize(datetime.datetime.utcnow())

    @classmethod
    def utc_ts(cls):
        """ returns utc timestamp for current time """
        return datetime.datetime.utcnow().timestamp()

    @classmethod
    def datetime_to_str(cls, datetime_object, output_format=Format.ISO):
        """ converts datetime object to a datetime-string, defaults to ISO 8601 format """
        return datetime_object.strftime(output_format)

    @classmethod
    def seconds_since_epoch_to_datetime(cls, seconds_since_epoch):
        """ returns timezone aware datetime object in UTC """
        try:
            return pytz.utc.localize(datetime.datetime.utcfromtimestamp(seconds_since_epoch))
        except:
            return None

    @classmethod
    def seconds_since_epoch_to_datetime_str(cls, seconds_since_epoch, format=Format.STANDARD):
        """ returns timezone aware datetime object in UTC """
        try:
            datetime_obj = cls.seconds_since_epoch_to_datetime(seconds_since_epoch)
            return cls.datetime_to_str(datetime_object=datetime_obj, output_format=format)
        except:
            return None

    @classmethod
    def localize(cls, datetime_object, input_timezone):
        """ returns a timezone aware object """
        if datetime_object is None:
            raise ValueError("datetime_object is None")
        if input_timezone is None:
            raise ValueError("Please specify input timezone. For example: 'US/Pacific'\n \
                             You can use some common timezones from TimeZones class of datetime_utils module")
        return pytz.timezone(input_timezone).localize(datetime_object)

    @classmethod
    def str_to_datetime(cls, datetime_string, input_format=None, input_timezone=None):
        """ returns timezone aware datetime object from the supplied datetime-string and input_timezone """
        if datetime_string is None or datetime_string == '':
            return None
        if input_format is None:
            raise ValueError("Please specify input datetime format. For example: '%Y-%m-%d %H:%M:%S'\n \
                             You can use some common formats from DateFormats class of datetime_utils module")
        if input_timezone is None:
            raise ValueError("Please specify input timezone. For example: 'US/Pacific'\n \
                             You can use some common timezones from TimeZones class of datetime_utils module")
        datetime_object = datetime.datetime.strptime(
            datetime_string, input_format)
        return pytz.timezone(input_timezone).localize(datetime_object)

    @classmethod
    def convert_timezone(cls, datetime_object, target_timezone=None):
        """ converts timezone for a timezone-aware datetime object """
        if datetime_object is None:
            raise ValueError("datetime_object is None")
        if datetime_object.tzinfo is None:
            raise ValueError(
                "The datetime object supplied for this input is not timezone aware. Please supply "
                "timezone aware datetime object")
        if target_timezone is None:
            raise ValueError("Please specify target timezone. For example: 'US/Pacific' or 'UTC'\n \
                             You can use some common timezones from TimeZones class of datetime_utils module")
        return datetime_object.astimezone(pytz.timezone(target_timezone))
