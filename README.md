###### Soupy
![](https://github.com/is-leeroy-jenkins/Soupy/blob/master/resources/project_soupy.png)

Soupy is a simple, reusable Python framework for scraping web pages into Markdown files.
It separates responsibilities into small, testable classes: Fetcher, Parser, Writer, Scraper,
plus a high‑level Soupy facade.

## 🎯 Purpose

Provide an easy, dependency‑light way to convert a URL into a clean Markdown file while keeping the
codebase understandable and maintainable via Single Responsibility, Composition, and clear
interfaces.

## ⚙️ Installation (with virtual environment)
 
Linux/macOS:

```
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install requests beautifulsoup4
```

Windows (PowerShell):
```
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip
    pip install requests beautifulsoup4
```

## 🚀 Usage Examples

### 1) Basic scrape with facade


```
    from soupy import Soupy
    
    scraper = Soupy()
    path = scraper.save_as_markdown("https://www.example.com", "example")
    print("Saved:", path)
```


### 2) Save into a custom directory

```
    from soupy import Soupy
    
    app = Soupy()
    path = app.save_as_markdown("https://docs.python.org", "python_docs", output_dir="docs")
    print("File stored at:", path)
```
### 3) Batch scrape a list of URLs

from soupy import Soupy

```
    urls = [
    "https://www.example.com",
    "https://www.python.org",]
```

## 📝 License

Soupy is published under
the [MIT General Public License v3](https://github.com/is-leeroy-jenkins/Boo/blob/main/LICENSE).

