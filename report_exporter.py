from pathlib import Path
from datetime import datetime


def save_markdown_report(text: str, filename: str = "final_investment_report.md") -> str:
    """
    Saves the final investment report as a Markdown file inside the project directory.
    Creates the file if it doesn't exist and overwrites previous content.

    :param text: Report text in Markdown format
    :param filename: Output file name (default: final_investment_report.md)
    :return: Full path to the file
    """
    # Determine path relative to current file
    base_dir = Path(__file__).resolve().parent
    output_path = base_dir / filename

    # Add automatic timestamp to the top of report
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_text = f"# Final Investment Report\n\nGenerated: {timestamp}\n\n{text}"

    # Write to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)

    return str(output_path)


def save_txt_report(text: str, filename: str = "final_investment_report.txt") -> str:
    """
    Alternative TXT saver (if Markdown is not needed).
    """
    base_dir = Path(__file__).resolve().parent
    output_path = base_dir / filename

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    return str(output_path)