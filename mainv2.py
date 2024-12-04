import time
from bitarray import bitarray
import re
MINUTES_PER_SEGMENT = 15
SEGMENTS_PER_HOUR = 4
TIME_PATTERN = r"(\d{2}\D*\d{2})"
TIMES_PATTERN = r"(\d{2}\D*\d{2}\D*\d{2}\D*\d{2})"

def parse_times(match):
    start_hour = int(match.group(1))
    start_minute = rount_minute(int(match.group(2)))
    end_hour = int(match.group(3))
    end_minute = round_minute(int(match.group(4)))
    return start_hour, start_minute, end_hour, end_minute

def validate_times(match):
    start_hour = int(match.group(1))
    start_minute = int(match.group(2))
    end_hour = int(match.group(3))
    end_minute = int(match.group(4))

    if not (0 <= start_hour <= 23 and 0 <= start_minute <= 59):
        return False
    elif not (0 <= end_hour <= 23 and 0 <= end_minute <= 59):
        return False
    elif end_hour<start_hour or (end_hour==start_hour and (round_minute(end_minute)-round_minute(start_minute))==0):
        return False
    return True

def round_minute(minute:int):
    modulus = minute%MINUTES_PER_SEGMENT
    if modulus>7:
        return minute+15-modulus
    else:
        return minute-modulus
    
class Timeline:
    def __init__(self, start:int=0, end:int=24):
        if(end-start<=0 or start<0 or start>23 or end>24 or end < 1):
            print("Invalid timeline")
            __del__(self)
        schedule = initialize_schedule(start, end)
        self.timeline = {"start":start, "end":end,"schedule":schedule}

    def initialize_schedule(self, start:int, end:int):
        schedule = bitarray('0' * (end-start) * SEGMENTS_PER_HOUR)

    def adjust_start(self, new_start:int):
        if(new_start<0 or new_start>23 or new_start>=self.timeline["end"]):
            print("Invalid start hour")
            return
        start = self.timeline["start"]
        change = start-new_start
        elif change<0:
            self.timeline["schedule"] = bitarray('0' * abs(change) * SEGMENTS_PER_HOUR) + self.timeline["schedule"]
            self.timeline["start"] = new_start
        else:
            self.timeline["schedule"] = self.timeline["schedule"][change * SEGMENTS_PER_HOUR:]
            self.timeline["start"] = new_start

        def adjust_end(self, new_end:int):
            change
            if(new_end<1 or new_end>24 or new_end<=self.timeline["start"]):
                print("Invalid end hour")
                return
            end = self.timeline["end"]
            change = end-new_end
            if change<0:
                self.timeline["schedule"] = self.timeline["schedule"][:1 + (abs(change) * SEGMENTS_PER_HOUR)]
                self.timeline["end"] = new_end
            else:
                self.timeline["schedule"] = self.timeline["schedule"] + bitarray('0' * change * SEGMENTS_PER_HOUR)
                self.timeline["end"] = new_end

        def reset_schedule(self):
            length = self.timeline["end"] - self.timeline["start"]
            self.timeline["schedule"] = bitarray('0' * length * SEGMENTS_PER_HOUR)

        def set_free_time(self):
            print("Enter start and end hours:")
            user_input = input()
            match = re.match(TIMES_PATTERN, user_input)
            if match is None or not validate_times(match):
                print("Invalid start and end times")
                return
            start_hour, start_minute, end_hour, end_minute = parse_times(match)
