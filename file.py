import random

def generate_student_data(num_students):
    """
    Generate random student data for testing.
    """
    student_data = []
    for _ in range(num_students):
        grades = [random.randint(60, 100) for _ in range(5)]  # Generate 5 random grades
        study_hours = random.randint(10, 30)
        student_data.append({'grades': grades, 'study_hours': study_hours})
    return student_data

def calculate_average(grades):
    """
    Calculate the average of a list of grades.
    """
    total = sum(grades)
    average = total / len(grades)
    return average

def predict_grade(average, study_hours):
    """
    Predict the student's grade based on average and study hours.
    """
    if average >= 90:
        if study_hours >= 20:
            return 'A'
        else:
            return 'B'
    elif average >= 80:
        return 'B'
    elif average >= 70:
        return 'C'
    else:
        return 'D'

def analyze_student_data(student_data):
    """
    Analyze the performance of multiple students.
    """
    for student in student_data:
        average_grade = calculate_average(student['grades'])
        study_hours = student['study_hours']
        predicted_grade = predict_grade(average_grade, study_hours)

        print(f"Average Grade: {average_grade} | Study Hours: {study_hours} | Predicted Grade: {predicted_grade}")

def main():
    """
    Main function to demonstrate the functionality.
    """
    num_students = 5
    student_data = generate_student_data(num_students)
    analyze_student_data(student_data)

if __name__ == "__main__":
    main()
