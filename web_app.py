import subprocess
from pathlib import Path
from flask import Flask, render_template_string, Response, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph

BASE_DIR = Path(__file__).resolve().parent
REPORT_MD = BASE_DIR / "final_investment_report.md"
REPORT_PDF = BASE_DIR / "final_investment_report.pdf"

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Intelligent Financial Agent Platform</title>
    <style>
        body {
            background: #0f172a;          /* тёмно-синий */
            color: #f1f5f9;               /* светлый текст */
            font-family: monospace;
            padding: 20px;
        }
        pre {
            background: #020617;
            padding: 20px;
            border-radius: 12px;
            white-space: pre-wrap;
            font-size: 13px;
            height: 600px;
            overflow-y: scroll;
            border: 2px solid #22c55e;    /* зелёный акцент */
        }
        h1 {
            color: #22c55e;               /* зелёный заголовок */
        }
        .buttons {
            margin-bottom: 20px;
        }
        button, a {
            background: #22c55e;          /* зелёные кнопки */
            color: #020617;               /* тёмный текст */
            border: none;
            padding: 10px 22px;
            margin-right: 12px;
            text-decoration: none;
            border-radius: 10px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.2s;
        }
        button:hover, a:hover {
            background: #16a34a;          /* тёмно-зелёный hover */
        }
    </style>
</head>
<body>

    <h1>Intelligent Financial Multi-Agent Dashboard</h1>

    <div class="buttons">
        <button onclick="location.reload()">Restart Pipeline</button>
        <a href="/download_md" target="_blank">Download Markdown</a>
        <a href="/download_pdf" target="_blank">Download PDF</a>
    </div>

    <pre id="output"></pre>

    <script>
        const evtSource = new EventSource("/stream");
        evtSource.onmessage = function(event) {
            document.getElementById("output").textContent += event.data + "\\n";
        };
    </script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

def run_script():
    process = subprocess.Popen(
        ["python", "-m", "Final_Project.main"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    for line in process.stdout:
        yield f"data:{line}\n\n"

@app.route("/stream")
def stream():
    return Response(run_script(), mimetype="text/event-stream")

@app.route("/download_md")
def download_md():
    return send_file(REPORT_MD, as_attachment=True)

@app.route("/download_pdf")
def download_pdf():
    create_pdf_from_md()
    return send_file(REPORT_PDF, as_attachment=True)

def create_pdf_from_md():
    if not REPORT_MD.exists():
        return

    styles = getSampleStyleSheet()
    story = []

    with open(REPORT_MD, "r", encoding="utf-8") as f:
        for line in f:
            story.append(Paragraph(line.replace("&", "&amp;"), styles["Normal"]))

    pdf = SimpleDocTemplate(str(REPORT_PDF), pagesize=A4)
    pdf.build(story)

if __name__ == "__main__":
    app.run(debug=True, port=8000)