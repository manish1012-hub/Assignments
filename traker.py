
# Author: Manishpal Singh
# Date: 03-Nov-2025
# Project Title: Daily Calorie Tracker CLI

import datetime

print("======================================")
print("     Welcome to Daily Calorie Tracker  ")
print("======================================")
print("This tool helps you track your daily meals and calorie intake.\n")

# ----------------------------
# Task 2: Input & Data Collection
# ----------------------------
meals = []
calories = []

num_meals = int(input("How many meals did you have today? "))

for i in range(num_meals):
    meal_name = input(f"\nEnter meal {i+1} name: ")
    meal_calories = float(input(f"Enter calories for {meal_name}: "))
    meals.append(meal_name)
    calories.append(meal_calories)

# ----------------------------
# Task 3: Calorie Calculations
# ----------------------------
total_calories = sum(calories)
average_calories = total_calories / len(calories)

daily_limit = float(input("\nEnter your daily calorie limit: "))

# ----------------------------
# Task 4: Exceed Limit Warning System
# ----------------------------
if total_calories > daily_limit:
    status_message = "⚠️ Warning: You have exceeded your daily calorie limit!"
else:
    status_message = "✅ Great! You are within your daily calorie limit."

# ----------------------------
# Task 5: Neatly Formatted Output
# ----------------------------
print("\n======================================")
print("          CALORIE SUMMARY REPORT       ")
print("======================================")
print("Meal Name\tCalories")
print("--------------------------------------")

for meal, cal in zip(meals, calories):
    print(f"{meal:<12}\t{cal}")

print("--------------------------------------")
print(f"Total Calories:\t{total_calories}")
print(f"Average per Meal:\t{average_calories:.2f}")
print(status_message)
print("======================================\n")

# ----------------------------
# Task 6 (Bonus): Save Session Log to File
# ----------------------------
save = input("Do you want to save this session log? (yes/no): ").strip().lower()

if save == "yes":
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = "calorie_log.txt"
    with open(filename, "a") as f:
        f.write("======================================\n")
        f.write(f"Calorie Tracker Session: {timestamp}\n")
        f.write("--------------------------------------\n")
        for meal, cal in zip(meals, calories):
            f.write(f"{meal:<12}\t{cal}\n")
        f.write("--------------------------------------\n")
        f.write(f"Total Calories: {total_calories}\n")
        f.write(f"Average per Meal: {average_calories:.2f}\n")
        f.write(f"Daily Limit: {daily_limit}\n")
        f.write(f"Status: {status_message}\n")
        f.write("======================================\n\n")
    print(f"✅ Session saved successfully in {filename}!")

print("\nThank you for using the Daily Calorie Tracker! Stay fit and healthy 💪")
