# gradebook.py
# Author: Manishpal Singh
# Date: 03-Nov-2025
# Project Title: GradeBook Analyzer CLI

import csv
import statistics

# ----------------------------
# Task 1: Project Setup & Menu
# ----------------------------
def display_menu():
    print("\n========================================")
    print("         GRADEBOOK ANALYZER CLI         ")
    print("========================================")
    print("1. Enter student data manually")
    print("2. Load data from CSV file")
    print("3. Exit")
    print("========================================")

# ----------------------------
# Task 2: Data Input or CSV Import
# ----------------------------
def manual_input():
    marks = {}
    n = int(input("How many students do you want to enter? "))
    for i in range(n):
        name = input(f"Enter name of student {i+1}: ")
        score = float(input(f"Enter marks for {name}: "))
        marks[name] = score
    return marks

def load_from_csv():
    marks = {}
    file_name = input("Enter CSV filename (e.g., students.csv): ")
    try:
        with open(file_name, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row['Name']
                score = float(row['Marks'])
                marks[name] = score
        print("✅ CSV file loaded successfully.")
    except FileNotFoundError:
        print("❌ File not found. Please check the filename.")
    return marks

# ----------------------------
# Task 3: Statistical Functions
# ----------------------------
def calculate_average(marks_dict):
    return sum(marks_dict.values()) / len(marks_dict)

def calculate_median(marks_dict):
    return statistics.median(marks_dict.values())

def find_max_score(marks_dict):
    return max(marks_dict.values())

def find_min_score(marks_dict):
    return min(marks_dict.values())

# ----------------------------
# Task 4: Grade Assignment
# ----------------------------
def assign_grades(marks_dict):
    grades = {}
    for name, score in marks_dict.items():
        if score >= 90:
            grades[name] = "A"
        elif score >= 80:
            grades[name] = "B"
        elif score >= 70:
            grades[name] = "C"
        elif score >= 60:
            grades[name] = "D"
        else:
            grades[name] = "F"
    return grades

def grade_distribution(grades_dict):
    counts = {"A":0, "B":0, "C":0, "D":0, "F":0}
    for grade in grades_dict.values():
        counts[grade] += 1
    return counts

# ----------------------------
# Task 5: Pass/Fail Filter
# ----------------------------
def pass_fail_lists(marks_dict):
    passed_students = [name for name, score in marks_dict.items() if score >= 40]
    failed_students = [name for name, score in marks_dict.items() if score < 40]
    return passed_students, failed_students

# ----------------------------
# Task 6: Display Results
# ----------------------------
def display_results(marks_dict, grades_dict):
    print("\n========================================")
    print("              GRADE REPORT              ")
    print("========================================")
    print(f"{'Name':<15}{'Marks':<10}{'Grade':<5}")
    print("----------------------------------------")
    for name in marks_dict:
        print(f"{name:<15}{marks_dict[name]:<10}{grades_dict[name]:<5}")
    print("----------------------------------------")

    avg = calculate_average(marks_dict)
    med = calculate_median(marks_dict)
    mx = find_max_score(marks_dict)
    mn = find_min_score(marks_dict)
    print(f"Average Marks: {avg:.2f}")
    print(f"Median Marks: {med}")
    print(f"Highest Marks: {mx}")
    print(f"Lowest Marks: {mn}\n")

    grade_dist = grade_distribution(grades_dict)
    print("Grade Distribution:")
    for grade, count in grade_dist.items():
        print(f"{grade}: {count} students")

    passed, failed = pass_fail_lists(marks_dict)
    print(f"\n✅ Passed ({len(passed)}): {', '.join(passed)}")
    print(f"❌ Failed ({len(failed)}): {', '.join(failed)}\n")

# ----------------------------
# Bonus: Save to CSV
# ----------------------------
def save_to_csv(marks_dict, grades_dict):
    file_name = "gradebook_output.csv"
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Marks", "Grade"])
        for name in marks_dict:
            writer.writerow([name, marks_dict[name], grades_dict[name]])
    print(f"✅ Results saved to {file_name}")

# ----------------------------
# Main Program Loop
# ----------------------------
def main():
    while True:
        display_menu()
        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            marks = manual_input()
        elif choice == '2':
            marks = load_from_csv()
            if not marks:
                continue
        elif choice == '3':
            print("Exiting GradeBook Analyzer. Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
            continue

        grades = assign_grades(marks)
        display_results(marks, grades)

        save = input("Do you want to save results to CSV? (yes/no): ").lower()
        if save == 'yes':
            save_to_csv(marks, grades)

        again = input("\nDo you want to analyze another dataset? (yes/no): ").lower()
        if again != 'yes':
            print("Thank you for using GradeBook Analyzer! 📊")
            break

# ----------------------------
# Run Program
# ----------------------------
if __name__ == "__main__":
    main()
    