import time
from bitarray import bitarray
import re

MINUTES_PER_SEGMENT = 15
SEGMENTS_PER_HOUR = 4
TIME_PATTERN = r"\d{2}"
#TIMES_PATTERN = r"(\d{2}\D*\d{2}\D*\d{2}\D*\d{2})"

#Extract integers from previously extracted list using regex. Helper function
def parse_times(match):
    start_hour = int(match[0])
    start_minute = round_minute(int(match[1]))
    end_hour = int(match[2])
    end_minute = round_minute(int(match[3]))
    return start_hour, start_minute, end_hour, end_minute

#Checks if extracted times are valid. Helper function
def validate_times(match):
    start_hour = int(match[0])
    start_minute = int(match[1])
    end_hour = int(match[2])
    end_minute = int(match[3])
    if not (0<=start_hour and 0<=start_minute<=59 and end_hour<=24 and (end_hour>start_hour or (start_hour==end_hour and round_minute(end_minute)>round_minute(start_minute)))):
        return False
    else:
        return True
    
#Rounds minutes to closest 15 minute segment
def round_minute(minute:int):
    modulus = minute%MINUTES_PER_SEGMENT
    if modulus==0:
        return minute
    elif modulus>7:
        return minute+15-modulus
    else:
        return minute-modulus
    
#Converts a given real time to a schedule-usable index and indents it. Helper function
def time_to_index(hour:int, minute:int, start:int):
    index = (hour-start)*SEGMENTS_PER_HOUR + minute/15
    return int(index)

#Converts a schedule-usable index to real time. Helper function
def index_to_time(index: int, start: int):
    hour = int(index / SEGMENTS_PER_HOUR) + start
    minute = (index % SEGMENTS_PER_HOUR) * MINUTES_PER_SEGMENT
    return f"{hour:02}:{minute:02}"

#Trim timeline to fit criteria. Helper function for optimizing comparisons
def normalize_timeline(timeline, start, end):
    start_index = (start - timeline.start) * SEGMENTS_PER_HOUR
    end_index = (end - timeline.start) * SEGMENTS_PER_HOUR
    start_index = max(0, start_index)
    end_index = min(len(timeline.schedule), end_index)
    return timeline.schedule[start_index:end_index]

#Returns all free time blocks from a list of timeline objects
def compare_timelines(timelines: list):
    if not timelines:
        print("List of timelines for comparison is empty!")
        return
    if len(timelines) == 1:
        print(find_free_times(timelines[0].schedule, timelines[0].start))
        return
    start = max(timeline.start for timeline in timelines)
    end = min(timeline.end for timeline in timelines)
    if start >= end:
        print("No overlapping time ranges found.")
        return
    aligned = normalize_timeline(timelines[0], start, end)
    for timeline in timelines[1:]:
        aligned &= normalize_timeline(timeline, start, end)
    return find_free_times(aligned, start)

#Returns list of free time blocks from timeline methods. Helper function
def find_free_times(schedule, schedule_start):
    start = None
    end = None
    found = []
    for i in range(0, len(schedule)):
        if(schedule[i]==1 and start is None):
            start = i
            end = i
        elif(schedule[i]==1 and start is not None):
            end = i
        if((schedule[i]==0 or i==len(schedule)-1) and start is not None):
            find = index_to_time(start, schedule_start) + "-" + index_to_time(end + 1, schedule_start)
            print(find)
            found.append(find)
            start = None
            end = None
    return found
class Timeline:
    #Bitarray schedule, start and end used for converting schedule-usable time<==>real time
    def __init__(self, start:int=0, end:int=24):
        if(end-start<=0 or start<0 or start>23 or end>24 or end < 1):
            print("Invalid timeline")
            __del__(self)
        self.start = start
        self.end = end
        self.schedule = bitarray('0' * (self.end-self.start) * SEGMENTS_PER_HOUR)
        
    #Extend or trim with start as reference
    def adjust_start(self, new_start:int):
        if(new_start<0 or new_start>23 or new_start>=self.end or new_start==self.start):
            print("Invalid start hour")
            return
        start = self.start
        change = start-new_start
        if change>0:
            new_schedule = bitarray('0' * change * SEGMENTS_PER_HOUR) + self.schedule
            self.schedule = new_schedule
            self.start = new_start
        else:
            new_schedule = self.schedule[abs(change) * SEGMENTS_PER_HOUR:]
            self.schedule = new_schedule
            self.start = new_start
        #print("New start time set")
            
    #Extend or trim with end as reference
    def adjust_end(self, new_end:int):
        if(new_end<1 or new_end>24 or new_end<=self.start or new_end==self.end):
             print("Invalid end hour")
             return
        end = self.end
        change = end-new_end
        if change>0:
            new_schedule = self.schedule[:1 + change * SEGMENTS_PER_HOUR]
            self.schedule = new_schedule
            self.end = new_end
        else:
            new_schedule = self.schedule + ('0' * abs(change) * SEGMENTS_PER_HOUR)
            self.schedule = new_schedule
            self.end = new_end
        #print("New end time set")
            
    #Set schedule to busy (default) while keeping start and end constraints
    def clear_schedule(self):
        length = self.end - self.start
        self.schedule = bitarray('0' * length * SEGMENTS_PER_HOUR)
        #print("Schedule reset")
        
    #Mark a time period as busy. String of 4x2-digit numbers as input in any format. Regex
    def set_busy_time(self, user_input:str):
        match = re.findall(TIME_PATTERN, user_input)
        if match is None or not validate_times(match):
            print("Invalid start and end times")
            return
        start_hour, start_minute, end_hour, end_minute = parse_times(match)
        start_minute = round_minute(start_minute)
        end_minute = round_minute(end_minute)
        start_index = time_to_index(start_hour, start_minute, self.start)
        end_index = time_to_index(end_hour, end_minute, self.start)
        change_length = end_index - start_index
        self.schedule[start_index:end_index] = bitarray('0' * change_length)
        #print("Free time set")
        
    ############# ------------------------- ##############
    #Mark a time period as available. String of 4x2-digit numbers as input in any format. Regex
    def set_free_time(self, user_input:str):
        match = re.findall(TIME_PATTERN, user_input)
        if match is None or len(match)!=4 or not validate_times(match):
            print("Invalid start and end times")
            return
        start_hour, start_minute, end_hour, end_minute = parse_times(match)
        start_minute = round_minute(start_minute)
        end_minute = round_minute(end_minute)
        start_index = time_to_index(start_hour, start_minute, self.start)
        end_index = time_to_index(end_hour, end_minute, self.start)
        change_length = end_index - start_index
        self.schedule[start_index:end_index] = bitarray('1' * change_length)
        #print("Free time set")
        
    #Debug function. Displays timeline class methods
    def display(self):
        print(f"Start time: {self.start}")
        print(f"End time: {self.end}")
        print(f"Schedule: {self.schedule}")
"""
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
"""




t1 = Timeline(6, 16)
t1.schedule = bitarray('1' * 40)
t2 = Timeline(8, 18)
t2.schedule = bitarray('1' * 40)
t3 = Timeline(11,13)
t3.schedule = bitarray('1' * 8)
#t1.set_free_time("from 00 00 to 0300")
#t1.set_busy_time("0900 0930")
t1.display()
#t1.set_busy_time("start at 0830 end at 0915")
#t1.display()
print(compare_timelines([t1,t2,t3]))
#print(compare_timelines([t1]))
