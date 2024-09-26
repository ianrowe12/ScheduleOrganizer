# from pandas import read_csv, ExcelWriter
import csv
from schedule_creator import ScheduleCreator


def clean_schedule(filenames):
    clean_schedules = []
    for filename in filenames:
        schedule = []

        with open(filename, mode='r') as file:
            csv_reader = csv.reader(file)
            header = next(csv_reader)  # Skipping the header

            for row in csv_reader:
                row = ["0" if cell == "" else cell for cell in row]  # Filling empty fields with "0"
                schedule.append(row)

        employee_unavailable = []
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri"]

        for day_index in range(1, len(days_of_week) + 1):
            first = True
            time = ""
            prev = ""

            for row in schedule:
                time_slot = row[0]  # The time of the day

                if row[day_index].lower() == "x":  # Checking if the student is unavailable at this time slot
                    prev = f" - {time_slot}, "
                    if first:
                        time += f"{time_slot}"
                        first = False
                elif not first:
                    first = True
                    time += prev

            if not first:
                time += prev

            # Collecting unavailable times for the day
            employee_unavailable.append((days_of_week[day_index - 1], time[:-2]))

        clean_schedules.append({
            "Student": filename.split("/")[-1][:-4],
            "Unavailable": employee_unavailable
        })
    return clean_schedules


names = ["Sade.csv", "Laura.csv", "DaVazjah.csv", "Makiya.csv", "Arly.csv"]


def generate_excel(filenames, worksheet_path):

    original_students = clean_schedule(filenames)

    ScheduleCreator(original_students, worksheet_path)

    return "Schedule generated at " + worksheet_path












