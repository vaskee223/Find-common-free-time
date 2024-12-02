#Nikola Vasiljevic

MINUTES_PER_SEGMENT = 15
SEGMENTS_PER_HOUR = 4 #int(60/MINUTES_PER_SEGMENT)
SEGMENTS_PER_DAY = SEGMENTS_PER_HOUR * 24
#START_HOUR = 8
#END_HOUR = 16
#MIN_FREE_SEGMENTS = 8

class User:
    def __init__(self, name="TEST USER"):
        self.name = name
        self.setup_worktime()
        
        
    def setup_worktime(self):
        self.segmented_timeline = [0] * SEGMENTS_PER_DAY #[0]*int(self.end_hour-self.start_hour)*SEGMENTS_PER_HOUR
        self.add_free_time()
        
    def add_free_time(self):
        print("Enter the time that you will be available in format HH:MM-HH:MM")
        entered = input()
        begin = int(int(entered[0:2])*SEGMENTS_PER_HOUR + int(entered[3:5])/MINUTES_PER_SEGMENT)
        end = int(int(entered[6:8])*SEGMENTS_PER_HOUR + int(entered[9:11])/MINUTES_PER_SEGMENT)
        #print(begin, end)
        for i in range(begin, end):
            self.segmented_timeline[i] = 1
            
    def add_busy_time(self):
        print("Enter the time that you will not be available in format HH:MM-HH:MM")
        entered = input()
        begin = int(int(entered[0:2])*SEGMENTS_PER_HOUR + int(entered[3:5])/MINUTES_PER_SEGMENT)
        end = int(int(entered[6:8])*SEGMENTS_PER_HOUR + int(entered[9:11])/MINUTES_PER_SEGMENT)
        for i in range(begin, end):
            self.segmented_timeline[i] = 0
            
            
    def __DEBUG__(self):
        print(self.segmented_timeline)
        
def translate_to_real_time(bitarray):
    start = 0
    end = 0
    for i in range(0, len(bitarray)):
        if(bitarray[i]==1 and start == 0):
            start = i
            end = i
        elif(bitarray[i]==1 and start !=0):
            end = i
        elif(bitarray[i]==0 and start != 0):
            end = i
            handle_translation(start, end)
            start = 0
            end = 0

def handle_translation(start, end):
    start_hrs = start//SEGMENTS_PER_HOUR
    if ((start//SEGMENTS_PER_HOUR)!=0):
        start_mins = start%(start//SEGMENTS_PER_HOUR)*MINUTES_PER_SEGMENT
    if(start_mins == 0 or start_mins == None):
        start_mins = "00"
    end_hrs = end//SEGMENTS_PER_HOUR
    if((end//SEGMENTS_PER_HOUR)!=0):
        end_mins = end%(end//SEGMENTS_PER_HOUR)*MINUTES_PER_SEGMENT
    if(end_mins == 0 or end_mins == None):
        end_mins = "00"
    print(f"Parallel unscheduled time for all colleagues: {start_hrs}:{start_mins}-{end_hrs}:{end_mins}")
        
        
def compare_time_schedules(comparison_array):
    if(len(comparison_array)==0):
        print("Invalid input")
    elif(len(comparison_array)==1):
        translate_to_real_time(comparison_array[0])
    else:
        default_comparison = comparison_array[0]
        for single_array in comparison_array[1::]:
            for i in range(len(single_array)):
                default_comparison[i] &= single_array[i]
        translate_to_real_time(default_comparison)
            
TEST_USER = User()
TEST_USER2 = User()
TEST_USER3 = User()
TEST_USER3.__DEBUG__()
print()
compare_time_schedules([TEST_USER.segmented_timeline, TEST_USER2.segmented_timeline, 
                        TEST_USER3.segmented_timeline
                        ])