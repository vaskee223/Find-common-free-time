**Class hierarchy:**
Team:
     name
     members:
          User:
              id
              name
              surname
              days:
	key -> day
	value -> Timeline:
	           start
	           end
	           schedule -> bitarray

**mainv2.py** <= main script

**Functions:**
Create a **team** class:
team_name = Team(name_as_string)
Add user to team:
team_name.add_member(user_class)
Remove user from team:
team_name.remove_member(user_id)
Create a **user** class:
user_name = User(name_as_string, last_name_as_string)
Set schedule for a single day:
user_name.set_day(day_as_string, start_int, end_int)
day_as_string => Monday/Tuesday/etc.
start_int, end_int => start and end of work day, changable afterward
user_name.populate_days_default()
creates a default 9-17 schedule for mon-fri
Alter user's **schedule**:
user_name.days[day_as_string]  ======>  schedule (for demo purposes)
schedule.adjust_start(start_as_int)
schedule.adjust_end(end_as_int)
parameters resembling integer whole hours eg. 7, 12, 15, 22..
schedule.set_free_time(from_to_string)
schedule.set_busy_time(from_to_string)
parameters resembling 4x2-digit numbers interpreted as HH:MM-HH:MM with regex
eg. "12:07-14:53", "12 30 14 00", "12 .. 00;14 -- 00"...
schedule.clear_schedule()
sets schedule to be fully busy(default)
