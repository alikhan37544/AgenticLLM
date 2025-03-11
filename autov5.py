import os
import csv
import pandas as pd
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

QUESTIONS_FILE = "questions.txt"
ANSWERS_FILE = "answers.txt"
STUDENT_ANSWERS_FOLDER = "student_answers"

GENAI_API_KEY = os.getenv("GEMINI_API_KEY")  # Set this in your environment
genai.configure(api_key=GENAI_API_KEY)

def load_text_file(file_path):
    """Load a text file and return a list of non-empty, stripped lines."""
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def evaluate_answer(question, answer_key, student_answer):
    """
    Calls Gemini Flash 2.0 with web search enabled to evaluate answers.
    Returns a tuple: (score, reasoning, model_thoughts)
    """
    model = genai.GenerativeModel('gemini-2.0-flash-thinking-exp')
    
    prompt = (
        f"Evaluate this student answer against the answer key. Follow these steps:\n"
        f"1. Analyze the question's requirements\n"
        f"2. Compare with the answer key\n"
        f"3. Assess knowledge accuracy\n"
        f"4. Consider clarity and completeness\n"
        f"5. Assign score (0-100)\n\n"
        f"Question: {question}\n"
        f"Answer Key: {answer_key}\n"
        f"Student Answer: {student_answer}\n\n"
        "Format your response exactly like this:\n"
        "<think>\n[Your detailed analysis here]\n</think>\n"
        "Score: [number 0-100]\n"
        "Reasoning: [Evaluation summary]"
    )
    
    response = model.generate_content(
        prompt,
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE
        },
        generation_config={"temperature": 0.2}
    )
    
    # Extract response text
    full_response = response.text
    
    # Parse response
    model_thoughts = ""
    score = "Error"
    reasoning = ""
    
    try:
        if "<think>" in full_response and "</think>" in full_response:
            model_thoughts = full_response.split("<think>")[1].split("</think>")[0].strip()
            remaining = full_response.split("</think>")[1].strip()
        else:
            remaining = full_response
        
        if "Score:" in remaining:
            score_part = remaining.split("Score:")[1].split("Reasoning:")[0].strip()
            score = int(score_part) if score_part.isdigit() else score_part
            reasoning = remaining.split("Reasoning:")[1].strip() if "Reasoning:" in remaining else ""
    except Exception as e:
        reasoning = f"Error parsing response: {str(e)}"
    
    return score, reasoning, model_thoughts

def main():
    # Load questions and answer keys
    questions = load_text_file(QUESTIONS_FILE)
    answers = load_text_file(ANSWERS_FILE)
    
    if len(questions) != len(answers):
        print("Error: The number of questions and answers do not match!")
        return

    evaluations = []
    student_files = [f for f in os.listdir(STUDENT_ANSWERS_FOLDER) if f.endswith(".txt")]
    
    if not student_files:
        print("Error: No student answer files found.")
        return

    for student_file in student_files:
        student_name = os.path.splitext(student_file)[0]
        student_answers = load_text_file(os.path.join(STUDENT_ANSWERS_FOLDER, student_file))
        
        if len(student_answers) < len(questions):
            print(f"Warning: {student_name} has fewer answers than questions.")
        
        for i, (question, answer_key) in enumerate(zip(questions, answers), start=1):
            student_answer = student_answers[i-1] if i-1 < len(student_answers) else "No answer provided."
            print(f"Evaluating {student_name} - Question {i}...")
            score, reasoning, model_thoughts = evaluate_answer(question, answer_key, student_answer)
            
            evaluations.append({
                "Student Name": student_name,
                "Question": question,
                "Answer Key": answer_key,
                "Student Answer": student_answer,
                "Score": score,
                "Reasoning": reasoning,
                "Model_Thoughts": model_thoughts
            })
    
    df = pd.DataFrame(evaluations)
    df.to_html("evaluation_results.html", index=False, border=1)
    print("Evaluation complete. Results saved to evaluation_results.html")

if __name__ == "__main__":
    main()
