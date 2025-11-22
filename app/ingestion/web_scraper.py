# app/ingestion/web_scraper.py
import requests
from bs4 import BeautifulSoup



class WebScraper:

    def scrape_url(url: str) -> dict:
        """Scrape a webpage and return title + clean text."""
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "Untitled"
        
        # remove unwanted elements
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        
        text = " ".join(soup.stripped_strings)
        return {"title": title, "url": url, "content": text}
    
    def extract_metadata(url: str, soup: BeautifulSoup) -> dict:
        """Extract metadata from the webpage."""
        metadata = {}
        meta_tags = soup.find_all("meta")
        for tag in meta_tags:
            if tag.get("name") and tag.get("content"):
                metadata[tag["name"].lower()] = tag["content"]
            elif tag.get("property") and tag.get("content"):
                metadata[tag["property"].lower()] = tag["content"]
        metadata["url"] = url
        return metadata
    
    def clea_data(text: str) -> str:
        """Clean extracted text by removing extra whitespace."""
        return ' '.join(text.split())
    
    def send_to_api(data: dict, api_url: str) -> None:
        """Send scraped data to an external API."""
        response = requests.post(api_url, json=data)
        response.raise_for_status()

    def scrape_url(self, url: str) -> None:
        """End-to-end scraping pipeline."""
        html = self.fetch_page(url)
        soup = self.parse_html(html)
        text = self.extract_text(soup)
        metadata = self.extract_metadata(soup)
        cleaned = self.clean_text(text)

        # Save locally
        file_name = url.replace("https://", "").replace("/", "_")[:50]
        self.save_text(cleaned, str(self.output_dir / f"{file_name}.txt"))

        # Send to API if configured
        if self.api_url:
            self.send_to_api(cleaned, metadata)

        print(f"Scraped and processed: {url}")

    

