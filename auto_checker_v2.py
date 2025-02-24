import os
import subprocess
import pandas as pd

# File paths for the answer key
QUESTIONS_FILE = "questions.txt"
ANSWERS_FILE = "answers.txt"
# Folder containing student answers, with one file per student (e.g., "Alice.txt", "Bob.txt")
STUDENT_ANSWERS_FOLDER = "student_answers"

def load_text_file(file_path):
    """Load a text file and return a list of non-empty, stripped lines."""
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def call_deepseek(prompt):
    """
    Calls the deepseek‑r1 model via Ollama using a subprocess.
    Returns the output text from the model.
    """
    try:
        result = subprocess.run(
            ["ollama", "run", "deepseek-r1", "--prompt", prompt],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def evaluate_answer(question, answer_key, student_answer):
    """
    Build a prompt with context for the LLM, call deepseek‑r1 via Ollama, and parse its response.
    Expected response format: "Score: X, Reasoning: Y"
    Returns a tuple (score, reasoning).
    """
    prompt = (
        f"Question: {question}\n"
        f"Answer Key: {answer_key}\n"
        f"Student Answer: {student_answer}\n\n"
        "Please evaluate the student's answer in detail. Provide a score out of 100 for correctness and completeness, "
        "and explain briefly why you gave that score."
    )
    result = call_deepseek(prompt)
    
    # Initialize default values in case parsing fails
    score = "Error"
    reasoning = "Error parsing result."
    
    if "Score:" in result and "Reasoning:" in result:
        try:
            # Extract the part after "Score:" and before "Reasoning:"
            score_part = result.split("Score:")[1].split("Reasoning:")[0].strip().rstrip(',')
            # Extract reasoning after "Reasoning:"
            reasoning = result.split("Reasoning:")[1].strip()
            # Convert score to int if possible, otherwise leave as string
            score = int(score_part) if score_part.isdigit() else score_part
        except Exception:
            score = "Error"
            reasoning = "Error parsing result."
    else:
        score = "Error"
        reasoning = f"Invalid response from deepseek: {result}"
    
    return score, reasoning

def main():
    # Load the questions and answer keys
    questions = load_text_file(QUESTIONS_FILE)
    answers = load_text_file(ANSWERS_FILE)
    
    # Check that we have the same number of questions and answers
    if len(questions) != len(answers):
        print("Mismatch in number of questions and answers!")
        return

    evaluations = []

    # List all student answer files from the specified folder
    student_files = [f for f in os.listdir(STUDENT_ANSWERS_FOLDER) if f.endswith(".txt")]
    
    if not student_files:
        print("No student answer files found in the folder.")
        return

    # Process each student file
    for student_file in student_files:
        student_name, _ = os.path.splitext(student_file)
        student_file_path = os.path.join(STUDENT_ANSWERS_FOLDER, student_file)
        student_answers = load_text_file(student_file_path)
        
        # Ensure we have at least as many answers as there are questions
        if len(student_answers) < len(questions):
            print(f"Warning: {student_name} has fewer answers than questions. Missing answers will be marked as 'No answer provided.'")
        
        # Evaluate each answer
        for i, (question, answer_key) in enumerate(zip(questions, answers), start=1):
            # Get the student's answer for the question (if available)
            student_answer = student_answers[i-1] if i-1 < len(student_answers) else "No answer provided."
            print(f"Evaluating {student_name} - Question {i}...")
            score, reasoning = evaluate_answer(question, answer_key, student_answer)
            
            evaluations.append({
                "Student Name": student_name,
                "Question": question,
                "Answer Key": answer_key,
                "Student Answer": student_answer,
                "Score": score,
                "Reasoning": reasoning
            })
    
    # Create a DataFrame from the evaluations and save to a CSV file
    df = pd.DataFrame(evaluations)
    df.to_csv("evaluation_results.csv", index=False)
    print("Evaluation complete. Results saved to evaluation_results.csv")
    
if __name__ == "__main__":
    main()
