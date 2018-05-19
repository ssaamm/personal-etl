class Duration(object):
    MINUTES_PER_HOUR = 60
    SECONDS_PER_MINUTE = 60

    def __init__(self, hours, minutes, seconds):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

        if self.seconds >= Duration.SECONDS_PER_MINUTE:
            num_minutes = self.seconds / Duration.SECONDS_PER_MINUTE
            self.minutes += num_minutes
            self.seconds -= num_minutes * Duration.SECONDS_PER_MINUTE

        if self.minutes >= Duration.MINUTES_PER_HOUR:
            num_hours = self.minutes / Duration.MINUTES_PER_HOUR
            self.hours += num_hours
            self.minutes -= num_hours * Duration.MINUTES_PER_HOUR

    def __add__(self, other):
        return Duration(self.hours + other.hours, self.minutes + other.minutes, self.seconds + other.seconds)

    def __radd__(self, other):
        if other == 0:
            return Duration(self.hours, self.minutes, self.seconds)
        else:
            return self + other

    def __eq__(self, other):
        return self.hours == other.hours and self.minutes == other.minutes and self.seconds == other.seconds

    def __repr__(self):
        return '{h}:{m:0>2}:{s:0>2}'.format(h=self.hours, m=self.minutes, s=self.seconds)

    @staticmethod
    def from_string(duration_str):
        hours, minutes, seconds = [int(s) for s in duration_str.split(':')]
        return Duration(hours, minutes, seconds)
