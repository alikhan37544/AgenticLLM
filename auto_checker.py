import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import os, time, threading, requests

# Global file path variables
question_file_path = ""
answer_file_path = ""
csv_file_path = ""
output_folder_path = ""

# Global variables to hold questions, answers, and processed student names
questions = []
answers = []
processed_students = set()

def load_files():
    """
    Load the questions and answers from the selected files.
    Also, ensure the CSV file exists – if not, create it with appropriate headers.
    """
    global questions, answers
    if not question_file_path or not answer_file_path or not csv_file_path:
        messagebox.showerror("Error", "Please select all required files/folder.")
        return

    # Read the question file (assumed to be one question per line)
    with open(question_file_path, "r") as f:
        questions = [line.strip() for line in f if line.strip()]

    # Read the answer file (assumed to be one answer per line corresponding to each question)
    with open(answer_file_path, "r") as f:
        answers = [line.strip() for line in f if line.strip()]

    # If the CSV does not exist, create one with headers: Student Name and one column per question.
    if not os.path.exists(csv_file_path):
        cols = ["Student Name"] + [f"Q{i+1}" for i in range(len(questions))]
        df = pd.DataFrame(columns=cols)
        df.to_csv(csv_file_path, index=False)
    messagebox.showinfo("Info", "Files loaded successfully.")

def update_csv_headers():
    """
    Ensure that the CSV file includes additional columns for scores and feedback per question.
    (Columns: Score_Q1, Feedback_Q1, Score_Q2, Feedback_Q2, etc.)
    """
    df = pd.read_csv(csv_file_path)
    for i in range(len(questions)):
        score_col = f"Score_Q{i+1}"
        feedback_col = f"Feedback_Q{i+1}"
        if score_col not in df.columns:
            df[score_col] = ""
        if feedback_col not in df.columns:
            df[feedback_col] = ""
    df.to_csv(csv_file_path, index=False)

def call_deepseek(prompt):
    """
    Calls the deepseek‑r1 model’s API.
    Adjust the URL, endpoint, and payload format as needed.
    """
    url = "http://127.0.0.1:11434/generate"  # assumed endpoint; change if needed
    payload = {"prompt": prompt, "max_tokens": 150}
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            result = response.json()
            # We assume the API returns a JSON with a key "text" containing the output.
            return result.get("text", "")
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Exception: {str(e)}"

def fetch_submission_content(link):
    """
    Fetch the content from the student's submission link.
    (For now, we assume the link is a public Google Docs or similar text-based page.)
    """
    try:
        r = requests.get(link)
        if r.status_code == 200:
            return r.text
        else:
            return f"Error fetching submission: {r.status_code}"
    except Exception as e:
        return f"Exception fetching submission: {str(e)}"

def evaluate_student_submission(student_row):
    """
    For a given student's row (with a name and one submission link per question),
    iterate over each question and build a prompt combining:
      - The question text
      - The teacher’s answer (answer key)
      - The fetched student answer from the link.
    Then, call deepseek‑r1 to get an evaluation (score and explanation).
    Finally, save a report file for that student.
    """
    student_name = student_row["Student Name"]
    scores = []
    feedbacks = []

    # Loop through each question
    for i in range(len(questions)):
        q_text = questions[i]
        answer_key = answers[i] if i < len(answers) else ""
        link = student_row.get(f"Q{i+1}", "")
        if not link:
            scores.append("N/A")
            feedbacks.append("No submission provided.")
            continue

        student_answer = fetch_submission_content(link)
        # Build the prompt – you can customize this prompt as needed.
        prompt = (
            f"Question: {q_text}\n"
            f"Answer Key: {answer_key}\n"
            f"Student's Answer: {student_answer}\n"
            "Please evaluate the student's answer. Provide a score out of 10 and a brief explanation."
        )
        result = call_deepseek(prompt)

        # For demonstration, we assume the response is in the form:
        # "Score: X, Explanation: Y"
        if "Score:" in result and "Explanation:" in result:
            try:
                parts = result.split("Explanation:")
                score_part = parts[0].split("Score:")[1].strip()
                explanation = parts[1].strip()
                scores.append(score_part)
                feedbacks.append(explanation)
            except Exception:
                scores.append("Error")
                feedbacks.append("Error parsing result.")
        else:
            scores.append("Error")
            feedbacks.append("Invalid response from deepseek.")

    # Save a personalized evaluation report as a text file.
    report_file = os.path.join(output_folder_path, f"{student_name.replace(' ', '_')}_evaluation.txt")
    with open(report_file, "w") as f:
        f.write(f"Evaluation Report for {student_name}\n")
        for i in range(len(questions)):
            f.write(f"\nQuestion {i+1}: {questions[i]}\n")
            f.write(f"Score: {scores[i]}\n")
            f.write(f"Feedback: {feedbacks[i]}\n")
    return scores, feedbacks

def process_submissions():
    """
    Continuously poll the CSV file for new student submissions.
    When a new student row is detected (i.e. not already processed),
    evaluate the student's answers and update the CSV with scores and feedback.
    """
    while True:
        df = pd.read_csv(csv_file_path)
        updated = False
        for idx, row in df.iterrows():
            student_name = row["Student Name"]
            if student_name in processed_students:
                continue
            # Check if at least one submission link is filled in for this student.
            submissions = [row.get(f"Q{i+1}", "") for i in range(len(questions))]
            if any(submissions):
                scores, feedbacks = evaluate_student_submission(row)
                # Update the dataframe with the obtained results.
                for i in range(len(questions)):
                    df.loc[idx, f"Score_Q{i+1}"] = scores[i]
                    df.loc[idx, f"Feedback_Q{i+1}"] = feedbacks[i]
                processed_students.add(student_name)
                updated = True
                # Update the progress bar: Here we simply increment based on number of students.
                progress['value'] += 100 / max(1, len(df))
                root.update_idletasks()
        if updated:
            df.to_csv(csv_file_path, index=False)
        time.sleep(10)  # Poll every 10 seconds

def start_processing():
    """
    Update CSV headers (if needed) and start a background thread that
    continuously checks for new submissions.
    """
    update_csv_headers()
    threading.Thread(target=process_submissions, daemon=True).start()
    messagebox.showinfo("Info", "Started processing submissions. Please add student submission links to the CSV file.")

# GUI helper functions to select files/folder using Tkinter dialogs.
def select_question_file():
    global question_file_path
    question_file_path = filedialog.askopenfilename(title="Select Question File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    question_label.config(text=question_file_path)

def select_answer_file():
    global answer_file_path
    answer_file_path = filedialog.askopenfilename(title="Select Answer File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    answer_label.config(text=answer_file_path)

def select_csv_file():
    global csv_file_path
    csv_file_path = filedialog.askopenfilename(title="Select or Create CSV File", filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*")))
    csv_label.config(text=csv_file_path)

def select_output_folder():
    global output_folder_path
    output_folder_path = filedialog.askdirectory(title="Select Output Folder")
    output_label.config(text=output_folder_path)

# Set up the main Tkinter window and layout.
root = tk.Tk()
root.title("EduAssist - AI-powered Teaching Companion")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

tk.Button(frame, text="Select Question File", command=select_question_file).grid(row=0, column=0, padx=5, pady=5)
question_label = tk.Label(frame, text="No file selected")
question_label.grid(row=0, column=1, padx=5, pady=5)

tk.Button(frame, text="Select Answer File", command=select_answer_file).grid(row=1, column=0, padx=5, pady=5)
answer_label = tk.Label(frame, text="No file selected")
answer_label.grid(row=1, column=1, padx=5, pady=5)

tk.Button(frame, text="Select CSV File", command=select_csv_file).grid(row=2, column=0, padx=5, pady=5)
csv_label = tk.Label(frame, text="No file selected")
csv_label.grid(row=2, column=1, padx=5, pady=5)

tk.Button(frame, text="Select Output Folder", command=select_output_folder).grid(row=3, column=0, padx=5, pady=5)
output_label = tk.Label(frame, text="No folder selected")
output_label.grid(row=3, column=1, padx=5, pady=5)

tk.Button(frame, text="Load Files", command=load_files).grid(row=4, column=0, padx=5, pady=5)
tk.Button(frame, text="Start Processing", command=start_processing).grid(row=4, column=1, padx=5, pady=5)

# A simple progress bar to show processing progress.
progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress.pack(pady=10)

root.mainloop()



'''
How This Prototype Works

    File Selection & Setup:
    The GUI lets the teacher choose the question file, answer file, CSV file (for student details), and an output folder (for evaluation reports). When the "Load Files" button is pressed, the script reads the questions/answers and creates (or verifies) the CSV file’s structure.

    CSV Preparation:
    It updates the CSV file to include columns for storing scores and feedback for each question.

    Polling for Submissions:
    When you press "Start Processing," a background thread starts polling the CSV file every 10 seconds. When it finds a new student row (identified by a unique student name not processed before and with at least one submission link), it processes that row.

    Evaluation Process:
    For each question:
        The script retrieves the teacher’s answer key and fetches the student’s answer from the provided link.
        It builds a prompt (including question, answer key, and student answer) and sends it to the deepseek‑r1 model via a POST request.
        The returned response is parsed to extract a score and feedback.
        The script updates the CSV file with these details and saves a personalized evaluation report in the selected output folder.

    Progress Display:
    A progress bar in the GUI provides a visual cue as evaluations are processed.
n
Next Steps

You might need to:

    Adjust the file format assumptions (e.g., if you’re using Excel files or a different structure).
    Modify the API call details (endpoint URL, request format, error handling) depending on how deepseek‑r1 is implemented.
    Enhance error checking, logging, and possibly improve the user experience in the GUI.
'''