import time
from bitarray import bitarray
import re

MINUTES_PER_SEGMENT = 15
SEGMENTS_PER_HOUR = 4
TIME_PATTERN = r"\d{2}"

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

#Returns all free time blocks from a list of timeline objects. Manual calls as print parameter only. Helper function
def compare_timelines(timelines: list):
    if not timelines:
        print("List of timelines for comparison is empty!")
        return
    if len(timelines) == 1:
        return find_free_times(timelines[0].schedule, timelines[0].start)
    start = max(timeline.start for timeline in timelines)
    end = min(timeline.end for timeline in timelines)
    if start >= end:
        print("No overlapping time ranges found.")
        return
    aligned = normalize_timeline(timelines[0], start, end)
    for timeline in timelines[1:]:
        aligned &= normalize_timeline(timeline, start, end)
    return find_free_times(aligned, start)
#Utilises compare_timelines to print a comparison of schedules within a list of users
def compare_users(users:list):
    if not users:
        print("List of users for comparison is empty!")
        return
    if len(users)==1:
        for x in users[0].days.items():
            print(f"{x[0]}: {compare_timelines([x[1]])}")
    else:
        days = users[0].days.keys()
        for day in days:
            time_list = []
            for user in users:
                time_list.append(user.days[day])
            print(f"{day}: {compare_timelines(time_list)}")
#Prints out a comparison of schedules from a list of teams
def compare_teams(teams: list):
    if not teams:
        print("List of teams for comparison is empty!")
        return
    if len(teams) == 1:
        team = teams[0]
        if not team.members:
            print("The single team has no members!")
            return
        days = team.members[0].days.keys()
        for day in days:
            timelines = [member.days[day] for member in team.members if day in member.days]
            print(f"{day}: {compare_timelines(timelines)}")
    else:
        days = teams[0].members[0].days.keys()
        for day in days:
            timelines = []
            for team in teams:
                for member in team.members:
                    if day in member.days:
                        timelines.append(member.days[day])
            print(f"{day}: {compare_timelines(timelines)}")

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

class User:
    def __init__(self, name="User", surname="User"):
        self.id = 0
        self.name = name
        self.surname = surname
        self.days = {}

    #Sets schedule for provided day to user
    def set_day(self, day, start, end):
        if day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            self.days[day] = Timeline(start, end)

    #Sets a default schedule to user for demo
    def populate_days_default(self):
        timeline = Timeline(8,20)
        timeline.set_free_time("09 00 17 00")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        for x in days:
            self.days[x] = timeline

    def display(self):
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        for x in days:
            print(f"{x}: {self.days[x].schedule}")
            print(f"{self.name} {self.surname}")

class Team:
    def __init__(self, name="Team"):
        self.name = name
        self.members = []
        
    def display(self):
        print(f"{self.name}")
        print("Members: ")
        for x in self.members:
            print(f"{x.id}. {x.name}, {x.surname}")

    #Adds user to this team
    def add_member(self, member):
        if isinstance(member, User):
            member.id = len(self.members)
            self.members.append(member)

    #Removes user with id from this team
    def remove_member(self, member_id):
        try:
            del self.members[member_id]
        except IndexError:
            print("Invalid member id!")
        else:
            print("Member removed")
            
#<------------------------------------------------------------------------->
#Test classes:


# Create Team A
team1 = Team("Team A")
for i in range(1, 6):
    user = User(f"User{i}", f"Surname{i}")
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        user.set_day(day, 8, 20)#<----- day to create schedule for; starting hour for timeline; end hour for timeline
        user.days[day].set_free_time("08 30 to 16 30")#<----- 4x2-digit in any format - interpreted as HH:MM-HH:MM
        user.days[day].set_busy_time("10 00 - 10 30")
        user.days[day].set_busy_time("15 00 - 15 30")
    team1.add_member(user)

# Create Team B
team2 = Team("Team B")
for i in range(6, 11):
    user = User(f"User{i}", f"Surname{i}")
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        user.set_day(day, 8, 20)
        user.days[day].set_free_time("08 30 to 16 30")
        user.days[day].set_busy_time("10 00 - 10 30")
        user.days[day].set_busy_time("15 00 - 15 30")
    team2.add_member(user)

# Create Team C
team3 = Team("Team C")
for i in range(11, 16):
    user = User(f"User{i}", f"Surname{i}")
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
        user.set_day(day, 8, 20)
        user.days[day].set_free_time("08 30 to 16 30")
        user.days[day].set_busy_time("10 00 - 10 30")
        user.days[day].set_busy_time("15 00 - 15 30")
    team3.add_member(user)

# Display teams
team1.display()
team2.display()
team3.display()

# Compare days, users, and teams
print("Compare 2 days:")
print(compare_timelines([team1.members[0].days["Monday"], team2.members[0].days["Monday"]]))
print("Compare 2 users:")
compare_users([team1.members[0], team2.members[0]])
print("Compare 3 teams:")
compare_teams([team1, team2, team3])
