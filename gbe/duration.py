from datetime import (
    date,
    datetime,
    time,
    timedelta,
)


def timedelta_to_duration(td):
    return Duration(seconds=td.total_seconds())


class Duration(timedelta):
    '''Wraps a timedelta to produce a more useful representation of an
    extent of time.  Will probably get rid of the timedelta presently
    Can be initialized in two ways: either using timdelta syntax, in
    days and seconds, or using keyword args hours, minutes, and
    seconds. If the latter sum to a positive value in seconds, that
    value is what we'll use. (we do not currently represent negative
    durations)
    Note that set_format specifies the default (__str__)
    representation of this duration. By default, it's hh:mm:ss, but
    this format string can also access the days and total seconds
    as positional arguments 0 and 4 of the output tuple to format.
    Durations are precise to seconds, not to finer-grained units. Sorry.
    '''
    def __init__(self, days=0, hours=0, minutes=0, seconds=0):
        self.total_secs = (days *
                           24 * 3600 +
                           hours * 3600 +
                           minutes * 60 +
                           seconds)
        if hours * 3600 + minutes * 60 + seconds > 0:
            total_seconds = hours*3600 + minutes * 60 * seconds
            timedelta.__init__(total_seconds)
        else:
            super(timedelta, self)
        self.format_str = format_str = "{1:0>2}:{2:0>2}:{3:0>2}"

    def set_format(self, format_str="{1:0>2}:{2:0>2}:{3:0>2}"):
        self.format_str = format_str
        return self

    def minutes(self):
        return int((self.total_seconds()/60) % 60)

    def total_minutes(self):
        return int(self.total_seconds()/60)

    def hours(self):
        return int(self.total_seconds()/3600)

    def __div__(self, other):
        '''
        Behavior depends on the divisor. If dividing a duration by an int,
        return a duration, if dividing by a duration, return an int (the
        ratio of the two durations)
        Note that all division operations on Durations are calculated in
        terms of seconds. This can lead to unexpected results, for example
        Duration (70) % 60 => 0 (not 10!).
        '''
        if isinstance(other, int) or isinstance(other, long):
            return Duration(seconds=int(self.total_seconds()/other))
        elif isinstance(other, timedelta):
            return self.total_seconds()/other.total_seconds()
        else:
            raise TypeError("Unsupported operation: can only divide Duration" +
                            "by int or duration/timedelta")

    def __floordiv__(self, other):
        '''
        Behavior depends on the divisor. If dividing a duration by an int,
        return a duration, if dividing by a duration (including a timedelta),
        return an int (the ratio of the two durations)
        Note that all division operations on Durations are calculated in terms
        of seconds. This can lead to unexpected results, for example Duration
        (70) % 60 => 0 (not 10!).
        '''
        if isinstance(other, int) or isinstance(other, long):
            return Duration(seconds=long(self.total_seconds()//other))
        elif isinstance(other, timedelta):
            return int(self.total_seconds()//other.total_seconds())
        else:
            raise TypeError("Unsupported operation: can only divide Duration" +
                            "by int or duration/timedelta")

    def __mod__(self, other):
        '''
        Mod IS NOT LIKE DIV here. Mod should always return a duration.
        (if we take 130 minutes mod 60 minutes, we have a proportion of 2
        and a remainder of ten minutes: 60 minutes * 2 + 10 minutes = 130
        minutes. On the other hand if we take 130 minutes mod 2, we get 60
        minutes + 10 minutes, since 60 minutes * 2 + 10 minutes = 130 minutes)
        Note that all division operations on Durations are calculated in terms
        of seconds. This can lead to unexpected results, for example Duration
        (70) % 60 => 0 (not 10!).
        '''
        if isinstance(other, int) or isinstance(other, long):
            return Duration(seconds=(long(self.total_seconds() % other)))
        elif isinstance(other, timedelta):
            return Duration(seconds=long(self.total_seconds() %
                            other.total_seconds()))
        else:
            raise TypeError("Unsupported operation: can only take mod of " +
                            "Duration by int and Duration or timedelta")

    def __divmod__(self, other):
        '''
        Just returns the tuple (self div other, self mod other)
        Note that all division operations on Durations are calculated in
        terms of seconds. This can lead to unexpected results, for example
        Duration (70) % 60 => 0 (not 10!).
        '''
        try:
            return (self//other, self % other)
        except TypeError:
            return TypeError("Unsupported operation, " +
                             "cannot divide Duration by one of those")

    def __str__(self):
        '''
        Default representation is hh:mm:ss
        Use set_format to change representation
        '''
        return self.format_str.format(self.days,
                                      self.hours() % 24,
                                      self.minutes(),
                                      self.seconds % 60,
                                      self.total_seconds())


class DateTimeRange:
    '''
    Represents a range of absolute time specified by any two of three
    possible parameters. Parameters are tried in order: if both
    starttime and endtime are specified, duration is ignored. Duration
    is represented by a timedelta, or by a gbe Duration (which is a
    timedelta under the hood)
    '''
    def __init__(self, starttime=None, endtime=None, duration=None):
        if len(filter(lambda i: i, [starttime, endtime, duration])) < 2:
            raise Exception('Not enough arguments to create DateTimeRange')
        self.starttime = starttime
        self.endtime = endtime
        self.duration = duration
        if starttime and endtime:
            self.duration = endtime-starttime
        elif starttime and duration:
            self.endtime = starttime+duration
        else:
            self.starttime = endtime - duration

    def __contains__(self, t):
        '''
        Returns true if time t falls within the range represented here
        t can be a datetime, a date, or a DateTimeRange. t must be completely
        within this range to get a True.
        '''

        if isinstance(t, datetime):
            return self.starttime < t < self.endtime
        elif isinstance(t, date):
            return (self.starttime < datetime.combine(t, time.min) and
                    datetime.combine(t, time.max) < self.endtime)
        elif isinstance(t, DateTimeRange):
            return self.starttime < t.starttime and t.endtime < self.endtime
