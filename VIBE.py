# Yanisha Simpson
# CIS261
# VIBE Coding

import os
import sys

DATA_FILE = "student_grades.txt"
GRADE_THRESHOLDS = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
]


def display_message(message: str) -> None:
    print(f"{message}")


def calculate_average(test1: float, test2: float, test3: float) -> float:
    return (test1 + test2 + test3) / 3.0


def calculate_grade(average: float) -> str:
    for threshold, grade in GRADE_THRESHOLDS:
        if average >= threshold:
            return grade
    return "F"


def create_student_record(name: str, student_id: str, test1: float, test2: float, test3: float) -> dict:
    average = round(calculate_average(test1, test2, test3), 2)
    return {
        "name": name,
        "id": student_id,
        "test1": round(test1, 2),
        "test2": round(test2, 2),
        "test3": round(test3, 2),
        "average": average,
        "grade": calculate_grade(average),
    }


def prompt_for_student_record() -> dict:
    display_message("Enter new student information:")
    student_id = input("  Student ID: ").strip()
    if student_id == "\x1b":
        raise KeyboardInterrupt
    if not student_id:
        raise ValueError("Student ID cannot be empty.")

    name = input("  Student name: ").strip()
    if name == "\x1b":
        raise KeyboardInterrupt
    if not name:
        raise ValueError("Student name cannot be empty.")

    test1 = get_float_input("  Test 1 score (0-100): ")
    test2 = get_float_input("  Test 2 score (0-100): ")
    test3 = get_float_input("  Test 3 score (0-100): ")

    return create_student_record(name, student_id, test1, test2, test3)


class StudentManager:
    def __init__(self) -> None:
        self.records: list[dict] = []

    def add_student(self, record: dict) -> bool:
        if self.find_by_id(record["id"]) is not None:
            return False
        self.records.append(record)
        return True

    def find_by_id(self, student_id: str) -> dict | None:
        return next((record for record in self.records if record["id"] == student_id), None)

    def remove_student(self, student_id: str) -> bool:
        record = self.find_by_id(student_id)
        if record is None:
            return False
        self.records.remove(record)
        return True

    def search_by_name(self, query: str) -> list[dict]:
        lower_query = query.lower()
        return [record for record in self.records if lower_query in record["name"].lower()]

    def highest_average(self) -> dict | None:
        if not self.records:
            return None
        return max(self.records, key=lambda record: record["average"])

    def lowest_average(self) -> dict | None:
        if not self.records:
            return None
        return min(self.records, key=lambda record: record["average"])

    def class_average(self) -> float:
        if not self.records:
            return 0.0
        return sum(record["average"] for record in self.records) / len(self.records)

    def load_from_file(self, file_path: str) -> None:
        if not os.path.exists(file_path):
            display_message(f"No existing record file found at {file_path}. Starting with an empty list.")
            return
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split("|")
                    if len(parts) != 7:
                        display_message(f"Skipping invalid record line: {line}")
                        continue
                    name, student_id, test1, test2, test3, average, grade = parts
                    try:
                        record = {
                            "name": name,
                            "id": student_id,
                            "test1": float(test1),
                            "test2": float(test2),
                            "test3": float(test3),
                            "average": float(average),
                            "grade": grade,
                        }
                    except ValueError:
                        display_message(f"Skipping malformed record line: {line}")
                        continue
                    if self._validate_record(record):
                        self.records.append(record)
        except (IOError, OSError) as error:
            display_message(f"Error loading student records from {file_path}: {error}")

    def save_to_file(self, file_path: str) -> bool:
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                for record in self.records:
                    file.write(
                        f"{record['name']}|{record['id']}|{record['test1']:.2f}|{record['test2']:.2f}|"
                        f"{record['test3']:.2f}|{record['average']:.2f}|{record['grade']}\n"
                    )
            return True
        except (IOError, OSError) as error:
            display_message(f"Error saving student records to {file_path}: {error}")
            return False

    @staticmethod
    def _validate_record(record: object) -> bool:
        if not isinstance(record, dict):
            return False
        required_keys = {"name", "id", "test1", "test2", "test3", "average", "grade"}
        if set(record.keys()) != required_keys:
            return False
        try:
            float(record["test1"])
            float(record["test2"])
            float(record["test3"])
            float(record["average"])
            str(record["name"])
            str(record["id"])
            str(record["grade"])
        except (ValueError, TypeError, KeyError):
            return False
        return True


def read_single_character() -> str:
    if sys.platform.startswith("win"):
        try:
            import msvcrt
            ch = msvcrt.getwch()
            return ch
        except ImportError:
            pass
    else:
        try:
            import termios
            import tty
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            pass
    return input().strip()[:1]


def get_menu_choice() -> str:
    print("\nChoose an option or press ESC to exit:")
    print("1. Add new student record")
    print("2. View all student records")
    print("3. Search student by name")
    print("4. Display class statistics")
    print("5. Remove a student record")
    print("6. Save records now")
    print("7. Exit")
    print("Enter choice:", end=" ", flush=True)
    choice = read_single_character()
    if choice == "\x1b":
        print("ESC")
        return "ESC"
    print(choice)
    return choice


def get_float_input(prompt: str) -> float:
    while True:
        value = input(prompt).strip()
        if value == "\x1b":
            raise KeyboardInterrupt
        try:
            score = float(value)
            if score < 0 or score > 100:
                print("Please enter a score between 0 and 100.")
                continue
            return score
        except ValueError:
            print("Invalid number. Try again.")


def handle_add_student(manager: StudentManager) -> None:
    try:
        record = prompt_for_student_record()
    except ValueError as error:
        display_message(f"Error: {error}")
        return
    except KeyboardInterrupt:
        display_message("Entry cancelled.")
        return

    if manager.find_by_id(record["id"]) is not None:
        display_message(f"Student ID {record['id']} already exists.")
        return

    if manager.add_student(record):
        display_message(f"Added student {record['name']} ({record['id']}).")
    else:
        display_message(f"Could not add student {record['name']} ({record['id']}).")


def display_all_students(manager: StudentManager) -> None:
    if not manager.records:
        print("No student records available.")
        return
    header = f"{'Name':<20} {'ID':<12} {'Test1':>7} {'Test2':>7} {'Test3':>7} {'Average':>8} {'Grade':>6}"
    print(header)
    print("-" * len(header))
    for record in manager.records:
        print(
            f"{record['name']:<20} {record['id']:<12} "
            f"{record['test1']:7.2f} {record['test2']:7.2f} {record['test3']:7.2f} "
            f"{record['average']:8.2f} {record['grade']:>6}"
        )


def handle_search_student(manager: StudentManager) -> None:
    query = input("Enter name to search: ").strip()
    if not query or query == "\x1b":
        raise KeyboardInterrupt
    matches = manager.search_by_name(query)
    if not matches:
        print("No students found matching that name.")
        return
    for record in matches:
        print(
            f"Name: {record['name']} | ID: {record['id']} | "
            f"Test1: {record['test1']:.2f} Test2: {record['test2']:.2f} Test3: {record['test3']:.2f} | "
            f"Average: {record['average']:.2f} | Grade: {record['grade']}"
        )


def display_statistics(manager: StudentManager) -> None:
    if not manager.records:
        print("No student records available to calculate statistics.")
        return
    highest = manager.highest_average()
    lowest = manager.lowest_average()
    class_avg = manager.class_average()
    print(f"Class average: {class_avg:.2f}")
    if highest:
        print(f"Highest average: {highest['average']:.2f} ({highest['name']}, {highest['id']})")
    if lowest:
        print(f"Lowest average: {lowest['average']:.2f} ({lowest['name']}, {lowest['id']})")


def main() -> None:
    manager = StudentManager()
    manager.load_from_file(DATA_FILE)
    print(f"Loaded {len(manager.records)} student record(s) from {DATA_FILE}.")
    try:
        while True:
            choice = get_menu_choice()
            if choice == "ESC" or choice == "7":
                break
            if choice == "1":
                handle_add_student(manager)
                if manager.save_to_file(DATA_FILE):
                    display_message(f"Student records saved to {DATA_FILE}.")
            elif choice == "2":
                display_all_students(manager)
            elif choice == "3":
                handle_search_student(manager)
            elif choice == "4":
                display_statistics(manager)
            elif choice == "5":
                student_id = input("Enter student ID to remove: ").strip()
                if student_id == "\x1b":
                    raise KeyboardInterrupt
                if manager.remove_student(student_id):
                    display_message(f"Removed student {student_id}.")
                    if manager.save_to_file(DATA_FILE):
                        display_message(f"Student records saved to {DATA_FILE}.")
                else:
                    display_message(f"No student found for ID {student_id}.")
            elif choice == "6":
                if manager.save_to_file(DATA_FILE):
                    display_message(f"Saved student records to {DATA_FILE}.")
            else:
                display_message("Invalid choice. Please choose a number between 1 and 7, or press ESC.")
    except KeyboardInterrupt:
        display_message("\nESC received. Exiting program.")
    finally:
        if manager.save_to_file(DATA_FILE):
            display_message(f"Student records saved to {DATA_FILE}.")


if __name__ == "__main__":
    main()
