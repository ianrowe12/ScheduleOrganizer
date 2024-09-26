from datetime import datetime, timedelta
import csv

TIME_SLOTS = ["8:00", "8:30", "9:00", "9:30", "10:00", "10:30", "11:00", "11:30", "12:00", "12:30", "13:00", "13:30",
              "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30"]
FIRST_SHIFT = datetime.strptime("8:00", "%H:%M")
LAST_SHIFT = datetime.strptime("18:30", "%H:%M")
TIME_SLOTS = [datetime.strptime(time, "%H:%M") for time in TIME_SLOTS]
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

MIN_SLOTS = 8
INITIAL_MAX_SLOTS = 20


class ScheduleCreator:
    def __init__(self, student_schedules, output_path):
        self.student_schedules = student_schedules
        self.MAX_SLOTS = INITIAL_MAX_SLOTS if len(student_schedules) <= 5 else (55 // len(student_schedules)) * 2
        self.availability_map = self.create_av_map()

        self.student_order = self.find_student_priority(self.availability_map)  # List of Tuples composed of (Student name, available slots per week)
        self.slot_order = self.find_slot_priority(self.availability_map)  # Dictionary with each day of the week pointing to a time of the day and each time of the day pointing to a list of the students available for that time (sorted from most occupied to least occupied)

        self.possible_schedule = {day: {time_slot: '' for time_slot in TIME_SLOTS} for day in DAYS}

        # Empty Dictionary with all students pointing to 0
        self.hours_by_student = {student[0]: 0 for student in self.student_order}

        self.create_schedule(output_path)

    def create_av_map(self):
        av_map = {day: {time_slot: [] for time_slot in TIME_SLOTS} for day in DAYS}

        def add_student(student_schedule):
            student_unavailable = {}
            for day in student_schedule['Unavailable']:
                times = day[1].split(', ')
                unav_times = []
                for time in times:
                    if time == "":
                        continue
                    time = time.split(' - ')
                    time_format = "%I:%M %p"
                    start = datetime.strptime(time[0], time_format)
                    end = datetime.strptime(time[1], time_format)
                    time_pointer = start
                    while time_pointer <= end:
                        unav_times.append(time_pointer)
                        time_pointer += timedelta(minutes=30)
                student_unavailable[day[0]] = unav_times

            for day in DAYS:
                for time_slot in av_map[day]:
                    if time_slot not in student_unavailable[day]:
                        av_map[day][time_slot].append(student_schedule['Student'])
        for schedule in self.student_schedules:
            add_student(schedule)
        return av_map

    @staticmethod
    def find_student_priority(av_map):
        frequency_map = {}

        # Find priority order for students:
        for day in DAYS:
            for time_slot in av_map[day]:
                for student_name in av_map[day][time_slot]:
                    if student_name not in frequency_map:
                        frequency_map[student_name] = 1
                    else:
                        frequency_map[student_name] += 1
        order = sorted(frequency_map.items(), key=lambda x: x[1])  # x[1] because we want to sort by the value not the key
        return order

    @staticmethod
    def find_slot_priority(av_map):
        frequency_map_by_day = {}
        for day in DAYS:
            frequency_map_by_day[day] = sorted(av_map[day].items(), key=lambda x: x[1])
        list_total = [(day, frequency_map_by_day[day][time_slot][0], len(frequency_map_by_day[day][time_slot][1]))
                      for time_slot in range(len(TIME_SLOTS)) for day in DAYS]
        list_total.sort(key=lambda x: x[2])
        return list_total

    def slot_available(self, time_slot):
        day = time_slot[0]
        time = time_slot[1]
        # print(f"Checking slot {day} {time.strftime("%H:%M")}: {possible_schedule[day][time]}")
        if self.possible_schedule[day][time] == '':
            return True
        else:
            return False

    def av_4_slot(self, name, time_slot):
        day = time_slot[0]
        time = time_slot[1]
        if name in self.availability_map[day][time]:
            return True
        else:
            return False

    def fill_block(self, name, time_slot):
        day, starting_time = time_slot[0], time_slot[1]
        current_time = starting_time
        first_assignment = True

        while self.hours_by_student[name] < self.MAX_SLOTS and current_time >= FIRST_SHIFT:
            prev_slot = current_time - timedelta(minutes=30)
            if not self.slot_available((day, current_time)) or not self.av_4_slot(name, (day, current_time)):
                break
            if (prev_slot >= FIRST_SHIFT and (name, (day, current_time)) and self.slot_available((day, prev_slot))
                    and self.av_4_slot(name, (day, prev_slot))):
                self.possible_schedule[day][current_time] = name
                first_assignment = False
                self.hours_by_student[name] += 1
                current_time -= timedelta(minutes=30)
            elif self.av_4_slot(name, (day, current_time)) and not first_assignment:
                self.possible_schedule[day][current_time] = name
                self.hours_by_student[name] += 1
                break
            else:
                break

        current_time = starting_time  # Reset the variable to the original time
        if self.possible_schedule[day][current_time] != '':  # If the original space was occupied in previous while loop, we'll skip that slot
            current_time += timedelta(minutes=30)

        while self.hours_by_student[name] < self.MAX_SLOTS and current_time <= LAST_SHIFT:
            next_slot = current_time + timedelta(minutes=30)
            if not self.slot_available((day, current_time)) or not self.av_4_slot(name, (day, current_time)):
                break
            if (next_slot <= LAST_SHIFT and self.av_4_slot(name, (day, current_time))
                    and self.slot_available((day, next_slot)) and self.av_4_slot(name, (day, next_slot))):
                self.possible_schedule[day][current_time] = name
                first_assignment = False
                self.hours_by_student[name] += 1
                current_time += timedelta(minutes=30)
            elif self.av_4_slot(name, (day, current_time)) and not first_assignment:
                self.possible_schedule[day][current_time] = name
                self.hours_by_student[name] += 1
                break
            else:
                break

    def create_schedule(self, filename):
        for student in self.student_order:
            for slot in self.slot_order:
                if self.hours_by_student[student[0]] >= self.MAX_SLOTS:  # If the student is already working the max amount, skip it
                    break
                if slot[2] == 0:  # If the num of av students for that slot is 0, there's no point in checking
                    continue
                self.fill_block(student[0], slot)

        string_map = {day: {time_slot.strftime("%H:%M"): self.possible_schedule[day][time_slot]
                            for time_slot in TIME_SLOTS} for day in DAYS}

        time_slots = sorted(set(time for day_schedule in string_map.values() for time in day_schedule.keys()))

        # Open file to write CSV
        with open(f"{filename}.csv", mode='w', newline='') as file:
            writer = csv.writer(file)

            # Write header row (first cell empty, then days of the week)
            header = ["Time"] + list(string_map.keys())
            writer.writerow(header)

            # Write each time slot as the first column, then people for each day
            for time in time_slots:
                row = [time]  # First cell is the time slot
                for day in string_map:
                    row.append(string_map[day].get(time, "0"))  # Fill in person or "0" if no one assigned
                writer.writerow(row)




# print(df_display)
# print(availability_map['Tue'])
# print(student_order)
# print(hours_by_student)
# print(slot_order)
