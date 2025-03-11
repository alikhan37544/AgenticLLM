import os
import subprocess
import threading
from flask import Flask, render_template, jsonify, request, send_file

app = Flask(__name__, template_folder='templates', static_folder='static')

# Global variable to track evaluation status
evaluation_status = {
    "running": False,
    "complete": False,
    "progress": 0,
    "message": "",
    "error": None
}

def run_auto_checker():
    """Run the auto_checker_v3.py script in a separate thread"""
    global evaluation_status
    
    evaluation_status["running"] = True
    evaluation_status["complete"] = False
    evaluation_status["progress"] = 0
    evaluation_status["message"] = "Starting evaluation..."
    evaluation_status["error"] = None
    
    try:
        # Run the auto_checker_v3.py script
        result = subprocess.run(["python", "auto_checker_v3.py"], 
                               capture_output=True, text=True, check=True)
        
        if os.path.exists("evaluation_results.html"):
            evaluation_status["complete"] = True
            evaluation_status["message"] = "Evaluation completed successfully!"
        else:
            evaluation_status["error"] = "Evaluation completed but results file not found."
    except subprocess.CalledProcessError as e:
        evaluation_status["error"] = f"Error running evaluation: {e.stderr}"
    except Exception as e:
        evaluation_status["error"] = f"Unexpected error: {str(e)}"
    
    evaluation_status["running"] = False

@app.route('/')
def index():
    """Display the main page"""
    return render_template('index.html')

@app.route('/start_evaluation', methods=['POST'])
def start_evaluation():
    """Start the evaluation process"""
    global evaluation_status
    
    # Don't start if already running
    if evaluation_status["running"]:
        return jsonify({"status": "error", "message": "Evaluation already in progress"})
    
    # Reset status
    evaluation_status["complete"] = False
    evaluation_status["progress"] = 0
    evaluation_status["message"] = ""
    evaluation_status["error"] = None
    
    # Start evaluation in a separate thread
    thread = threading.Thread(target=run_auto_checker)
    thread.daemon = True
    thread.start()
    
    return jsonify({"status": "started"})

@app.route('/status')
def check_status():
    """Check the status of the evaluation process"""
    return jsonify(evaluation_status)

@app.route('/results')
def view_results():
    """Display the evaluation results"""
    if not os.path.exists("evaluation_results.html"):
        return render_template('error.html', message="No evaluation results found.")
    
    # Read the HTML content
    with open("evaluation_results.html", "r", encoding="utf-8") as file:
        results_html = file.read()
        
    return render_template('results.html', results_content=results_html)

@app.route('/download_results')
def download_results():
    """Download the results file"""
    if os.path.exists("evaluation_results.html"):
        return send_file("evaluation_results.html", as_attachment=True)
    else:
        return jsonify({"status": "error", "message": "Results file not found"})

if __name__ == '__main__':
    app.run(debug=True)