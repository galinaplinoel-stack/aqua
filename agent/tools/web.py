"""Web search and scraping tools."""

import json
import subprocess
from typing import Optional

import requests
from bs4 import BeautifulSoup
from rich.console import Console

console = Console()


def web_search(query: str, num_results: int = 5) -> str:
    """Search the web using DuckDuckGo (no API key needed)."""
    try:
        # Use DuckDuckGo HTML version
        url = f"https://html.duckduckgo.com/html/?q={query}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        results = []
        for i, result in enumerate(soup.select(".result")[:num_results]):
            title_elem = result.select_one(".result__title a")
            snippet_elem = result.select_one(".result__snippet")
            if title_elem:
                title = title_elem.get_text(strip=True)
                link = title_elem.get("href", "")
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                results.append({
                    "title": title,
                    "url": link,
                    "snippet": snippet,
                })

        if not results:
            return "No results found."

        output = []
        for i, r in enumerate(results, 1):
            output.append(f"{i}. **{r['title']}**")
            output.append(f"   {r['snippet']}")
            output.append(f"   {r['url']}")
            output.append("")

        return "\n".join(output)

    except Exception as e:
        return f"Search error: {e}"


def scrape_webpage(url: str, selector: Optional[str] = None) -> str:
    """Scrape content from a webpage."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script and style elements
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        if selector:
            elements = soup.select(selector)
            if not elements:
                return f"No elements found matching selector: {selector}"
            text = "\n\n".join(el.get_text(strip=True, separator="\n") for el in elements)
        else:
            # Get main content
            main = soup.select_one("main, article, .content, .post, #content")
            if main:
                text = main.get_text(strip=True, separator="\n")
            else:
                text = soup.get_text(strip=True, separator="\n")

        # Truncate if too long
        if len(text) > 10000:
            text = text[:10000] + "\n\n... (truncated)"

        return text or "No content found."

    except Exception as e:
        return f"Scraping error: {e}"


def extract_links(url: str) -> str:
    """Extract all links from a webpage."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        links = []
        for a in soup.select("a[href]"):
            href = a.get("href", "")
            text = a.get_text(strip=True)
            if href and not href.startswith("#") and not href.startswith("javascript:"):
                links.append({"text": text or "(no text)", "url": href})

        if not links:
            return "No links found."

        return json.dumps(links[:50], indent=2)

    except Exception as e:
        return f"Error: {e}"


def get_page_metadata(url: str) -> str:
    """Get metadata from a webpage (title, description, og tags)."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        metadata = {
            "url": url,
            "title": "",
            "description": "",
            "og_title": "",
            "og_description": "",
            "og_image": "",
            "keywords": "",
        }

        # Title
        title = soup.select_one("title")
        if title:
            metadata["title"] = title.get_text(strip=True)

        # Meta tags
        for meta in soup.select("meta"):
            name = meta.get("name", "").lower()
            prop = meta.get("property", "").lower()
            content = meta.get("content", "")

            if name == "description":
                metadata["description"] = content
            elif name == "keywords":
                metadata["keywords"] = content
            elif prop == "og:title":
                metadata["og_title"] = content
            elif prop == "og:description":
                metadata["og_description"] = content
            elif prop == "og:image":
                metadata["og_image"] = content

        return json.dumps(metadata, indent=2)

    except Exception as e:
        return f"Error: {e}"


WEB_SEARCH_TOOLS = {
    "web_search": {
        "func": web_search,
        "schema": {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web using DuckDuckGo. Returns titles, snippets, and URLs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "num_results": {"type": "integer", "description": "Number of results (default: 5)"},
                    },
                    "required": ["query"],
                },
            },
        },
    },
    "scrape_webpage": {
        "func": scrape_webpage,
        "schema": {
            "type": "function",
            "function": {
                "name": "scrape_webpage",
                "description": "Scrape text content from a webpage. Optionally filter by CSS selector.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to scrape"},
                        "selector": {"type": "string", "description": "Optional CSS selector to filter content"},
                    },
                    "required": ["url"],
                },
            },
        },
    },
    "extract_links": {
        "func": extract_links,
        "schema": {
            "type": "function",
            "function": {
                "name": "extract_links",
                "description": "Extract all links from a webpage.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to extract links from"},
                    },
                    "required": ["url"],
                },
            },
        },
    },
    "get_page_metadata": {
        "func": get_page_metadata,
        "schema": {
            "type": "function",
            "function": {
                "name": "get_page_metadata",
                "description": "Get metadata from a webpage (title, description, Open Graph tags).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "URL to get metadata from"},
                    },
                    "required": ["url"],
                },
            },
        },
    },
}
