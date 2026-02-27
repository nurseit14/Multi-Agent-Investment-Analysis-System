# Intelligent Financial Multi-Agent Dashboard

An intelligent platform leveraging multi-agent AI (CrewAI) and LangChain to perform comprehensive financial analysis, including technical, fundamental, and risk assessments for specific stock tickers. 

## Features
- **Multi-Agent Architecture**: Uses specialized AI agents (Data Collector, Technical Analyst, Fundamental Analyst, Risk Manager, Report Writer, Evaluator) for end-to-end analysis.
- **Automated Data Collection**: Fetches real-time market data alongside financial news.
- **RAG & Knowledge Graphs**: Integrates Vector Stores and Knowledge Graphs to supply agents with enriched contextual information.
- **Interactive Web Dashboard**: Built with Flask, offering real-time streaming of the agent pipeline execution and seamless download of Markdown/PDF reports.
- **Multimodal Data**: Processes not only textual data and stock tables but also charts and generated images to create enriched reports.
- **Model Context Protocol (MCP)**: Native integration support mapping to advanced backend resources.

## Project Structure
- `main.py`: Pipeline entry point taking a list of test tickers to orchestrate data collection and agent reporting synchronously or asynchronously.
- `crew_setup.py`: Core CrewAI implementation defining tasks, expected outcomes, and agent workflows (Sequential Process).
- `agents.py` & `chains.py` & `memory_system.py`: Definitions of custom LLM agents and memory components tailored to financial assessments.
- `web_app.py`: Flask dashboard frontend visualizing the analysis streamed in real-time.
- `rag_kg.py` & `data_prep.py`: Data ingestion, multimodal preparation, and retrieval-augmented generation modules vectorizing knowledge bases.
- `evaluation.py`: Automated grading subsystem acting on the final reports to maintain analytical quality.

## Notes 
- **Dataset / Inputs**: The dataset used to run comprehensive examples or train sub-systems is **not uploaded** to the repository due to data access limitations.
- **Screenshots**: UI screenshots of the Flask dashboard and final PDF reports have **not been uploaded** in this initial iteration.

## Installation & Setup
1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd <repository-folder>
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - Create a `.env` file in the root directory to store any necessary external API keys (e.g., `OPENAI_API_KEY`, etc).

## Running the Application
### CLI Mode
Run the multi-agent pipeline from the command line:
```bash
python main.py
```
This will process the data and build `final_investment_report.md` alongside `final_investment_report.pdf`.

### Web Dashboard
To visually track the task execution through an interactive UI:
```bash
python web_app.py
```
Navigate to `http://127.0.0.1:8000` in your web browser. You can trigger the agents, monitor status, and download localized reports via the frontend.

## Required Technologies
- Python 3.9+
- [LangChain Core / Community](https://github.com/langchain-ai/langchain)
- [CrewAI](https://github.com/joaomdmoura/crewAI)
- [Flask](https://flask.palletsprojects.com/)
- [YFinance](https://pypi.org/project/yfinance/)
- [ReportLab](https://pypi.org/project/reportlab/)
- PyPDF2, Qdrant / Chroma

## ⚖️ Disclaimer
*This project is built purely for educational and research purposes. The AI-generated final investment reports or analysis presented by the platform must not be considered professional financial advice.*
