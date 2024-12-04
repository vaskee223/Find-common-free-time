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
    elif end_hour<start_hour or (end_hour==start_hour and (round_minute(end_minute)-round_minute(start_minute))<=0):
        return False
    return True

def round_minute(minute:int):
    modulus = minute%MINUTES_PER_SEGMENT
    if modulus==0:
        return minute
    elif modulus>7:
        return minute+15-modulus
    else:
        return minute-modulus

def time_to_index(hour:int, minute:int, start:int):
    index = (hour-start)*SEGMENTS_PER_HOUR + minute/15
    return int(index)

def index_to_time(index:int, start:int):
    hour = int(index/SEGMENTS_PER_HOUR)
    minute = int(index%SEGMENTS_PER_HOUR)*MINUTES_PER_SEGMENT
    if hour<10:
        hour = "0" + str(hour)
    if minute==0:
        minute = "00"
    return str(hour) + ":" + str(minute)

def normalize_timeline(timeline, start, end):
    start_index = timeline["start"] * SEGMENTS_PER_HOUR - start
    end_index = end - timeline["end"] * SEGMENTS_PER_HOUR
    return timeline["schedule"][start_index:end_index+1]

def compare_timelines(timelines:list):
    start = 100
    end = 0
    if(len(timelines)==0):
        print("List of timelines for comparison is empty!")
        return
    elif(len(timelines)==1):
        print(find_free_time(timelines[0]["schedule"]))
        return
    for timeline in timelines:
        if timeline["start"]<min:
            min = timeline["start"]
        if timeline["end"]>max:
            max = timeline["end"]
    alligned = normalize_timeline(timelines[0])
    for i in range(1, len(timelines)+1):
        alligned &= normalize_timeline(timelines[i])
    print("Free times found: ")
    print(find_free_times(alligned, start))

def find_free_times(schedule, schedule_start):
    start = 0
    end = 0
    found = []
    for i in range(0, len(schedule)):
        if(schedule[i]==1 and start == 0):
            start = i
            end = i
        elif(schedule[i]==1 and start !=0):
            end = i
        elif(schedule[i]==0 and start !=0):
            end = i
            find = index_to_time(start, schedule_start) + "-" + index_to_time(end, schedule_start)
            found.append(find)
            start = 0
            end = 0
    return found
    
class Timeline:
    def __init__(self, start:int=0, end:int=24):
        if(end-start<=0 or start<0 or start>23 or end>24 or end < 1):
            print("Invalid timeline")
            __del__(self)
        schedule = self.initialize_schedule(start, end)
        self.timeline = {"start":start, "end":end,"schedule":schedule}

    def initialize_schedule(self, start:int, end:int):
        return bitarray('0' * (end-start) * SEGMENTS_PER_HOUR)

    def adjust_start(self, new_start:int):
        if(new_start<0 or new_start>23 or new_start>=self.timeline["end"]):
            print("Invalid start hour")
            return
        start = self.timeline["start"]
        change = start-new_start
        if change<0:
            self.timeline["schedule"] = bitarray('0' * abs(change) * SEGMENTS_PER_HOUR) + self.timeline["schedule"]
            self.timeline["start"] = new_start
        else:
            self.timeline["schedule"] = self.timeline["schedule"][change * SEGMENTS_PER_HOUR:]
            self.timeline["start"] = new_start
        #print("New start time set")
    def adjust_end(self, new_end:int):
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
        #print("New end time set")

    def reset_schedule(self):
        length = self.timeline["end"] - self.timeline["start"]
        self.timeline["schedule"] = bitarray('0' * length * SEGMENTS_PER_HOUR)
        #print("Schedule reset")

    def set_busy_time(self, user_input:str):
        match = re.match(TIMES_PATTERN, user_input)
        if match is None or not validate_times(match):
            print("Invalid start and end times")
            return
        start_hour, start_minute, end_hour, end_minute = parse_times(match)
        start_minute = round_minute(start_minute)
        end_minute = round_minute(end_minute)
        start_index = time_to_index(start_hour, start_minute, self.timeline["start"])
        end_index = time_to_index(end_hour, end_minute, self.timeline["start"])
        change_length = end_index - start_index
        self.timeline["schedule"][start_index:end_index+1] = bitarray('0' * (change_length + 1))
        #print("Free time set")

    def set_free_time(self, user_input:str):
        match = re.match(TIMES_PATTERN, user_input)
        if match is None or not validate_times(match):
            print("Invalid start and end times")
            return
        start_hour, start_minute, end_hour, end_minute = parse_times(match)
        start_minute = round_minute(start_minute)
        end_minute = round_minute(end_minute)
        start_index = time_to_index(start_hour, start_minute, self.timeline["start"])
        end_index = time_to_index(end_hour, end_minute, self.timeline["start"])
        change_length = end_index - start_index
        self.timeline["schedule"][start_index:end_index+1] = bitarray('1' * (change_length + 1))
        #print("Free time set")

    def set_free_time(self):
        print("Enter start and end hours:")
        user_input = input()
        match = re.match(TIMES_PATTERN, user_input)
        if match is None or not validate_times(match):
            print("Invalid start and end times")
            return
        start_hour, start_minute, end_hour, end_minute = parse_times(match)
        start_minute = round_minute(start_minute)
        end_minute = round_minute(end_minute)
        start_index = time_to_index(start_hour, start_minute, self.timeline["start"])
        end_index = time_to_index(end_hour, end_minute, self.timeline["start"])
        change_length = end_index - start_index
        self.timeline["schedule"][start_index:end_index+1] = bitarray('1' * (change_length + 1))
        print("Free time set")


    def set_busy_time(self):
        print("Enter start and end hours:")
        user_input = input()
        match = re.match(TIMES_PATTERN, user_input)
        if match is None or not validate_times(match):
            print("Invalid start and end times")
            return
        start_hour, start_minute, end_hour, end_minute = parse_times(match)
        start_minute = round_minute(start_minute)
        end_minute = round_minute(end_minute)
        start_index = time_to_index(start_hour, start_minute, self.timeline["start"])
        end_index = time_to_index(end_hour, end_minute, self.timeline["start"])
        change_length = end_index - start_index
        self.timeline["schedule"][start_index:end_index+1] = bitarray('0' * (change_length + 1))
        print("Free time set")

    def show_timeline(self):
        for x in self.timeline.items():
            print(x)



t1 = Timeline()
t1.show_timeline()
t1.set_free_time()

            
