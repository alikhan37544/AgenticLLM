import os
import pandas as pd
from langchain.llms import Ollama

# File paths for questions and answer keys
QUESTIONS_FILE = "questions.txt"
ANSWERS_FILE = "answers.txt"
# Folder containing student answers (one file per student, e.g., "Ali.txt", "Bob.txt")
STUDENT_ANSWERS_FOLDER = "student_answers"

def load_text_file(file_path):
    """Load a text file and return a list of non-empty, stripped lines."""
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def evaluate_answer(llm, question, answer_key, student_answer):
    """
    Constructs a prompt for deepseek‑r1 with the provided context and uses the
    LangChain Ollama LLM to evaluate the student's answer.
    
    Expected model response format:
    "Score: X, Reasoning: Y"
    """
    prompt = (
        f"Question: {question}\n"
        f"Answer Key: {answer_key}\n"
        f"Student Answer: {student_answer}\n\n"
        "Please evaluate the student's answer in detail. Provide a score out of 100 for correctness "
        "and completeness, and explain briefly why you gave that score."
    )
    result = llm(prompt)
    
    # Initialize default values in case parsing fails
    score = "Error"
    reasoning = f"Invalid response: {result}"
    
    if "Score:" in result and "Reasoning:" in result:
        try:
            score_part = result.split("Score:")[1].split("Reasoning:")[0].strip().rstrip(',')
            reasoning = result.split("Reasoning:")[1].strip()
            score = int(score_part) if score_part.isdigit() else score_part
        except Exception:
            score = "Error"
            reasoning = "Error parsing result."
    
    return score, reasoning

def main():
    # Load questions and answer keys
    questions = load_text_file(QUESTIONS_FILE)
    answers = load_text_file(ANSWERS_FILE)
    
    if len(questions) != len(answers):
        print("Mismatch: The number of questions and answers do not match!")
        return

    evaluations = []

    # List all student answer files in the folder
    student_files = [f for f in os.listdir(STUDENT_ANSWERS_FOLDER) if f.endswith(".txt")]
    if not student_files:
        print("No student answer files found in the folder.")
        return

    # Initialize the LangChain Ollama LLM for deepseek‑r1.
    # Adjust the model name or base_url if necessary.
    llm = Ollama(model="deepseek-r1", base_url="http://127.0.0.1:11434")
    
    for student_file in student_files:
        student_name, _ = os.path.splitext(student_file)
        student_file_path = os.path.join(STUDENT_ANSWERS_FOLDER, student_file)
        student_answers = load_text_file(student_file_path)
        
        if len(student_answers) < len(questions):
            print(f"Warning: {student_name} has fewer answers than questions. Missing answers will be marked as 'No answer provided.'")
        
        for i, (question, answer_key) in enumerate(zip(questions, answers), start=1):
            student_answer = student_answers[i-1] if i-1 < len(student_answers) else "No answer provided."
            print(f"Evaluating {student_name} - Question {i}...")
            score, reasoning = evaluate_answer(llm, question, answer_key, student_answer)
            
            evaluations.append({
                "Student Name": student_name,
                "Question": question,
                "Answer Key": answer_key,
                "Student Answer": student_answer,
                "Score": score,
                "Reasoning": reasoning
            })
    
    df = pd.DataFrame(evaluations)
    df.to_csv("evaluation_results.csv", index=False)
    print("Evaluation complete. Results saved to evaluation_results.csv")

if __name__ == "__main__":
    main()
