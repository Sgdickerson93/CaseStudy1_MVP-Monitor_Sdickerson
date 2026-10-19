# Fake data to test
from pathlib import Path

conversation_id = "test-123"

conversation = {
    "markdown": "# Test Report\nThis is fake AlphaSense research."
}

OUTPUT_FOLDER = Path("reports")
OUTPUT_FOLDER.mkdir(exist_ok=True)
result_file = "test_report"
OUTPUT_FILE = OUTPUT_FOLDER / f"{result_file}_{conversation_id}.md"
OUTPUT_FILE.write_text(conversation["markdown"], encoding="utf-8")