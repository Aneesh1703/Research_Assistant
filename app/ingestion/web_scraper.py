# app/ingestion/web_scraper.py
import requests
from bs4 import BeautifulSoup


def scrape_url(url: str) -> dict:
    """
    Scrape a webpage and return title + clean text.
    
    Args:
        url: URL to scrape
        
    Returns:
        Dictionary with title, url, and content
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "Untitled"
        
        # Remove unwanted elements
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        
        text = " ".join(soup.stripped_strings)
        
        return {
            "title": title.strip(),
            "url": url,
            "content": text
        }
    except Exception as e:
        raise Exception(f"Failed to scrape URL: {str(e)}")


def extract_metadata(url: str, soup: BeautifulSoup) -> dict:
    """
    Extract metadata from the webpage.
    
    Args:
        url: URL of the webpage
        soup: BeautifulSoup object
        
    Returns:
        Dictionary containing metadata
    """
    metadata = {}
    meta_tags = soup.find_all("meta")
    for tag in meta_tags:
        if tag.get("name") and tag.get("content"):
            metadata[tag["name"].lower()] = tag["content"]
        elif tag.get("property") and tag.get("content"):
            metadata[tag["property"].lower()] = tag["content"]
    metadata["url"] = url
    return metadata
