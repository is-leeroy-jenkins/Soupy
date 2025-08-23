###### Soupy
![]()

Soupy is a SOLID, simple, reusable Python framework for scraping web pages into Markdown files.
It separates responsibilities into small, testable classes: Fetcher, Parser, Writer, Scraper,
plus a high‑level Soupy facade.

## 🎯 Purpose

Provide an easy, dependency‑light way to convert a URL into a clean Markdown file while keeping the
codebase understandable and maintainable via Single Responsibility, Composition, and clear
interfaces.

## ⚙️ Installation (with virtual environment)

Purpose:
Set up an isolated environment and install the minimal dependencies.

Linux/macOS:
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install requests beautifulsoup4

Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install requests beautifulsoup4

## 🚀 Usage Examples

### 1) Basic scrape with facade

Purpose:
Fetch a page, extract readable text, and save to a Markdown file using the simple facade.

from soupy import Soupy

scraper = Soupy()
path = scraper.save_as_markdown("https://www.example.com", "example")
print("Saved:", path)

Parameters:
url (str): Target website URL.
filename (str): Markdown filename without extension.
output_dir (str, default="output"): Directory to save the file.

Returns:
Optional[str]: Full path to the saved .md file, or None if the operation failed.

### 2) Save into a custom directory

Purpose:
Write output to a specific folder under the project root.

from soupy import Soupy

app = Soupy()
path = app.save_as_markdown("https://docs.python.org", "python_docs", output_dir="docs")
print("File stored at:", path)

### 3) Batch scrape a list of URLs

Purpose:
Loop through multiple pages and save outputs with auto‑derived filenames.

from soupy import Soupy

urls = [
"https://www.example.com",
"https://www.python.org",
]
MIT License. See LICENSE for details.