"""
Data & Storage Tools for AgentSpring
Includes file operations, database, PDF, OCR, CSV, and JSON tools
"""
import os
import shutil
import tempfile
import csv
import json
import sqlite3
from typing import List, Optional
from pathlib import Path
from . import tool

# Try to import optional dependencies
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

# File operations
def _safe_open(file_path, mode, encoding=None):
    if encoding:
        return open(file_path, mode, encoding=encoding)
    return open(file_path, mode)

@tool("read_file", "Read contents of a file with encoding detection", permissions=[])
def read_file(file_path: str, encoding: str = "utf-8"):
    with _safe_open(file_path, "r", encoding=encoding) as f:
        return {"content": f.read(), "file_path": file_path}

@tool("write_file", "Write content to a file with backup", permissions=[])
def write_file(file_path: str, content: str, backup: bool = True):
    if backup and os.path.exists(file_path):
        shutil.copy2(file_path, file_path + ".bak")
    with _safe_open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    return {"success": True, "file_path": file_path}

@tool("list_files", "List files in a directory with detailed information", permissions=[])
def list_files(directory: str = ".", pattern: str = "*", include_hidden: bool = False):
    files = []
    for entry in os.scandir(directory):
        if not include_hidden and entry.name.startswith('.'):
            continue
        files.append({
            "name": entry.name,
            "is_file": entry.is_file(),
            "is_dir": entry.is_dir(),
            "size": entry.stat().st_size,
            "path": entry.path
        })
    return {"files": files, "directory": directory}

@tool("delete_file", "Delete a file or directory safely", permissions=[])
def delete_file(file_path: str, recursive: bool = False):
    if os.path.isdir(file_path) and recursive:
        shutil.rmtree(file_path)
    elif os.path.isdir(file_path):
        os.rmdir(file_path)
    else:
        os.remove(file_path)
    return {"success": True, "file_path": file_path}

@tool("copy_file", "Copy a file or directory", permissions=[])
def copy_file(source: str, destination: str, overwrite: bool = False):
    if os.path.isdir(source):
        if overwrite and os.path.exists(destination):
            shutil.rmtree(destination)
        shutil.copytree(source, destination)
    else:
        if overwrite and os.path.exists(destination):
            os.remove(destination)
        shutil.copy2(source, destination)
    return {"success": True, "source": source, "destination": destination}

@tool("move_file", "Move a file or directory", permissions=[])
def move_file(source: str, destination: str, overwrite: bool = False):
    if overwrite and os.path.exists(destination):
        if os.path.isdir(destination):
            shutil.rmtree(destination)
        else:
            os.remove(destination)
    shutil.move(source, destination)
    return {"success": True, "source": source, "destination": destination}

@tool("create_directory", "Create a directory and parent directories", permissions=[])
def create_directory(directory: str, parents: bool = True):
    if parents:
        os.makedirs(directory, exist_ok=True)
    else:
        os.mkdir(directory)
    return {"success": True, "directory": directory}

@tool("get_file_info", "Get detailed information about a file", permissions=[])
def get_file_info(file_path: str):
    stat = os.stat(file_path)
    return {
        "file_path": file_path,
        "size": stat.st_size,
        "created": stat.st_ctime,
        "modified": stat.st_mtime,
        "is_file": os.path.isfile(file_path),
        "is_dir": os.path.isdir(file_path)
    }

@tool("compress_file", "Compress files into ZIP or TAR archive", permissions=[])
def compress_file(source_paths: list, output_path: str, format: str = "zip"):
    import zipfile, tarfile
    if format == "zip":
        with zipfile.ZipFile(output_path, 'w') as zf:
            for path in source_paths:
                zf.write(path, os.path.basename(path))
    elif format == "tar":
        with tarfile.open(output_path, 'w') as tf:
            for path in source_paths:
                tf.add(path, arcname=os.path.basename(path))
    else:
        raise Exception("Unsupported format")
    return {"success": True, "output_path": output_path}

@tool("extract_archive", "Extract ZIP or TAR archive", permissions=[])
def extract_archive(archive_path: str, extract_to: str = ""):
    import zipfile, tarfile
    if not extract_to:
        extract_to = os.path.splitext(archive_path)[0] + "_extracted"
    if archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path, 'r') as zf:
            zf.extractall(extract_to)
    elif archive_path.endswith(".tar") or archive_path.endswith(".tar.gz"):
        with tarfile.open(archive_path, 'r') as tf:
            tf.extractall(extract_to)
    else:
        raise Exception("Unsupported archive format")
    return {"success": True, "extract_to": extract_to}

@tool("read_csv", "Read CSV file and return as JSON", permissions=[])
def read_csv(file_path: str, delimiter: str = ",", has_header: bool = True):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter)
        rows = list(reader)
        if has_header:
            header = rows[0]
            data = [dict(zip(header, row)) for row in rows[1:]]
            return {"header": header, "data": data}
        else:
            return {"data": rows}

@tool("write_csv", "Write data to CSV file", permissions=[])
def write_csv(file_path: str, data: list, headers: Optional[List[str]] = None):
    with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if headers:
            writer.writerow(headers)
        writer.writerows(data)
    return {"success": True, "file_path": file_path}

@tool("read_json", "Read JSON file", permissions=[])
def read_json(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

@tool("write_json", "Write data to JSON file", permissions=[])
def write_json(file_path: str, data: dict, indent: int = 2):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent)
    return {"success": True, "file_path": file_path}

# PDF and OCR tools
@tool("read_pdf", "Read text content from a PDF file", permissions=[])
def read_pdf(file_path: str):
    if not PDF_AVAILABLE:
        raise Exception("PyPDF2 not installed")
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        text = "\n".join(page.extract_text() or '' for page in reader.pages)
    return {"text": text, "file_path": file_path}

@tool("extract_text", "Extract text from a document using textract or fallback", permissions=[])
def extract_text(file_path: str):
    try:
        import textract
        text = textract.process(file_path).decode('utf-8')
        return {"text": text, "file_path": file_path}
    except ImportError:
        if file_path.lower().endswith('.pdf') and PDF_AVAILABLE:
            return read_pdf(file_path)
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')) and OCR_AVAILABLE:
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            return {"text": text, "file_path": file_path}
        else:
            raise Exception("No suitable text extraction backend available")

# Database tools (example: SQLite)
@tool("create_contact", "Create a CRM contact (SQLite)", permissions=[])
def create_contact(name: str, email: str, phone: str = ""):
    conn = sqlite3.connect('crm.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, name TEXT, email TEXT, phone TEXT)''')
    c.execute('INSERT INTO contacts (name, email, phone) VALUES (?, ?, ?)', (name, email, phone))
    conn.commit()
    contact_id = c.lastrowid
    conn.close()
    return {"success": True, "contact_id": contact_id}

@tool("update_lead", "Update a CRM lead (SQLite)", permissions=[])
def update_lead(lead_id: str, updates: dict):
    conn = sqlite3.connect('crm.db')
    c = conn.cursor()
    for key, value in updates.items():
        c.execute(f'UPDATE leads SET {key} = ? WHERE id = ?', (value, lead_id))
    conn.commit()
    conn.close()
    return {"success": True, "lead_id": lead_id} 