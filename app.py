from flask import Flask, render_template, request, send_file
from langchain_community.llms import HuggingFacePipeline
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from datetime import datetime
from weasyprint import HTML
import os
import json

app = Flask(__name__)

# Teamwork.com API credentials
TEAMWORK_API_TOKEN = os.getenv("TEAMWORK_API_TOKEN", "your_teamwork_api_token")
TEAMWORK_URL = "https://yourcompany.teamwork.com"  # Replace with your Teamwork.com domain

# Set up requests session with retry logic
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))

# Llama 3.1 8B setup
model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    load_in_4bit=True,
    device_map="auto",
    torch_dtype=torch.float16
)
hf_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=200,
    temperature=0.7,
    top_p=0.9,
    return_full_text=False
)
llm = HuggingFacePipeline(pipeline=hf_pipeline)
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)

def fetch_teamwork_data(project_id):
    """Fetch tasks from Teamwork.com with caching."""
    cache_file = f"cache_{project_id}.json"
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return json.load(f)
    url = f"{TEAMWORK_URL}/projects/{project_id}/tasks.json"
    response = session.get(url, headers={"Authorization": f"Bearer {TEAMWORK_API_TOKEN}"})
    response.raise_for_status()
    data = response.json().get("todo-items", [])
    with open(cache_file, "w") as f:
        json.dump(data, f)
    return data

def generate_report_data(project_data):
    """Generate report with overdue task tracking."""
    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_tasks": len(project_data),
        "overdue_tasks": 0,
        "status_summary": {},
        "tasks": []
    }
    today = datetime.now().strftime("%Y%m%d")
    for task in project_data:
        status = task["status"]
        due_date = task["due-date"]
        report["status_summary"][status] = report["status_summary"].get(status, 0) + 1
        if due_date and due_date < today and status != "completed":
            report["overdue_tasks"] += 1
        report["tasks"].append({
            "name": task["content"],
            "status": status,
            "due_date": due_date if due_date else "No due date",
            "assignees": ", ".join([user["name"] for user in task.get("responsible-parties", [])]) if task.get("responsible-parties") else "Unassigned"
        })
    summary_prompt = f"Summarize the following project data in 2-3 sentences:\nStatus: {report['status_summary']}\nOverdue tasks: {report['overdue_tasks']}\nTasks: {report['tasks']}"
    report["summary"] = conversation.predict(input=summary_prompt)
    return report

@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_input = request.form["user_input"]
        project_id = request.form.get("project_id", "")
        try:
            if not project_id:
                raise ValueError("Project ID is required.")
            if "report" in user_input.lower():
                project_data = fetch_teamwork_data(project_id)
                report = generate_report_data(project_data)
                return render_template(
                    "report.html",
                    report=report,
                    project_id=project_id,
                    chat_history=memory.buffer
                )
            else:
                response = conversation.predict(input=user_input)
                return render_template(
                    "chat.html",
                    user_input=user_input,
                    bot_response=response,
                    chat_history=memory.buffer
                )
        except Exception as e:
            return render_template(
                "chat.html",
                error=f"Error: {str(e)}",
                chat_history=memory.buffer
            )
    return render_template("chat.html", chat_history="")

@app.route("/download_pdf/<project_id>")
def download_pdf(project_id):
    try:
        project_data = fetch_teamwork_data(project_id)
        report = generate_report_data(project_data)
        html = render_template("report.html", report=report, project_id=project_id)
        pdf_file = f"project_report_{project_id}.pdf"
        HTML(string=html).write_pdf(pdf_file)
        return send_file(pdf_file, as_attachment=True)
    except Exception as e:
        return f"Error generating PDF: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)