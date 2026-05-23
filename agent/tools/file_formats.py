"""File format support - PDF, CSV, Excel, JSON, YAML."""

import csv
import json
import os
from typing import Optional

from rich.console import Console

console = Console()


def read_json(file_path: str) -> str:
    """Read and parse a JSON file."""
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"JSON error: {e}"


def write_json(file_path: str, data: str) -> str:
    """Write data to a JSON file."""
    try:
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(json.loads(data), f, indent=2, ensure_ascii=False)
        return f"Written to {file_path}"
    except Exception as e:
        return f"JSON error: {e}"


def read_yaml(file_path: str) -> str:
    """Read and parse a YAML file."""
    try:
        import yaml
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)
    except ImportError:
        return "Error: pyyaml not installed"
    except Exception as e:
        return f"YAML error: {e}"


def write_yaml(file_path: str, data: str) -> str:
    """Write data to a YAML file."""
    try:
        import yaml
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else ".", exist_ok=True)
        with open(file_path, "w") as f:
            yaml.dump(json.loads(data), f, default_flow_style=False, allow_unicode=True)
        return f"Written to {file_path}"
    except ImportError:
        return "Error: pyyaml not installed"
    except Exception as e:
        return f"YAML error: {e}"


def read_csv(file_path: str, limit: int = 100) -> str:
    """Read a CSV file and return as JSON."""
    try:
        rows = []
        with open(file_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= limit:
                    break
                rows.append(dict(row))
        return json.dumps(rows, indent=2, ensure_ascii=False)
    except Exception as e:
        return f"CSV error: {e}"


def read_pdf(file_path: str, pages: Optional[str] = None) -> str:
    """Extract text from a PDF file."""
    try:
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        text_parts = []

        if pages:
            # Parse page range (e.g., "1-5" or "1,3,5")
            page_nums = []
            for part in pages.split(","):
                if "-" in part:
                    start, end = part.split("-")
                    page_nums.extend(range(int(start) - 1, int(end)))
                else:
                    page_nums.append(int(part) - 1)
        else:
            page_nums = range(min(len(doc), 50))  # Limit to 50 pages

        for page_num in page_nums:
            if page_num < len(doc):
                page = doc[page_num]
                text_parts.append(f"--- Page {page_num + 1} ---\n{page.get_text()}")

        doc.close()
        return "\n\n".join(text_parts) if text_parts else "No text extracted"

    except ImportError:
        return "Error: PyMuPDF not installed. Run: pip install PyMuPDF"
    except Exception as e:
        return f"PDF error: {e}"


def read_excel(file_path: str, sheet: Optional[str] = None, limit: int = 100) -> str:
    """Read an Excel file and return as JSON."""
    try:
        import pandas as pd

        if sheet:
            df = pd.read_excel(file_path, sheet_name=sheet)
        else:
            df = pd.read_excel(file_path)

        df = df.head(limit)
        return df.to_json(orient="records", indent=2, force_ascii=False)

    except ImportError:
        return "Error: pandas not installed. Run: pip install pandas openpyxl"
    except Exception as e:
        return f"Excel error: {e}"


FILE_FORMAT_TOOLS = {
    "read_json": {
        "func": read_json,
        "schema": {
            "type": "function",
            "function": {
                "name": "read_json",
                "description": "Read and parse a JSON file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to JSON file"},
                    },
                    "required": ["file_path"],
                },
            },
        },
    },
    "write_json": {
        "func": write_json,
        "schema": {
            "type": "function",
            "function": {
                "name": "write_json",
                "description": "Write data to a JSON file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to JSON file"},
                        "data": {"type": "string", "description": "JSON data string to write"},
                    },
                    "required": ["file_path", "data"],
                },
            },
        },
    },
    "read_csv": {
        "func": read_csv,
        "schema": {
            "type": "function",
            "function": {
                "name": "read_csv",
                "description": "Read a CSV file and return as JSON array.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to CSV file"},
                        "limit": {"type": "integer", "description": "Max rows to read (default: 100)"},
                    },
                    "required": ["file_path"],
                },
            },
        },
    },
    "read_pdf": {
        "func": read_pdf,
        "schema": {
            "type": "function",
            "function": {
                "name": "read_pdf",
                "description": "Extract text from a PDF file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to PDF file"},
                        "pages": {"type": "string", "description": "Page range (e.g., '1-5' or '1,3,5')"},
                    },
                    "required": ["file_path"],
                },
            },
        },
    },
    "read_excel": {
        "func": read_excel,
        "schema": {
            "type": "function",
            "function": {
                "name": "read_excel",
                "description": "Read an Excel file and return as JSON.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "Path to Excel file"},
                        "sheet": {"type": "string", "description": "Sheet name (optional)"},
                        "limit": {"type": "integer", "description": "Max rows to read (default: 100)"},
                    },
                    "required": ["file_path"],
                },
            },
        },
    },
}
