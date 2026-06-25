"""
Download product webpages for later HTML parsing.

This module sends HTTP requests to product URLs and stores
raw HTML locally so page structure can be inspected before
building store-specific scrapers.
"""

import requests

from src.config import HTML_DIR
from src.load_links import load_product_links


# Many retail websites reject requests that do not look browser-like.
# This header helps our request resemble a normal browser visit.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/136.0 Safari/537.36"
    )
}


def fetch_page(url: str) -> str:
    """Download HTML content from a product webpage.

    Args:
        url (str): Product URL to request.

    Returns:
        str: Raw HTML response text.
        
    Raises:
        requests.HTTPError: Raised if the webpage returns an unsuccessful status code.
        requests.RequestException: Raised for network-related request failures.
    """
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()
    
    return response.text


def save_html(html: str, filename: str) -> None:
    """Save downloaded HTML content to the local debug directory.

    Args:
        html (str): Raw HTML content from the product page.
        filename (str): Name of the output HTML file.
    """
    HTML_DIR.mkdir(exist_ok=True)
    
    output_path = HTML_DIR / filename
    
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(html)
        
        
if __name__ == "__main__":
    links_df = load_product_links()
    
    for index, row in links_df.iterrows():
        store = row["store"]
        url = row["clean_url"]
        filename = f"{index}_{store.lower()}_page.html"
        
        print(f"Fetching {store}: {url}")
        
        try:
            html = fetch_page(url)
            save_html(html, filename)
            print(f"Saved {filename}")
        
        except requests.RequestException as error:
            print(f"Failed to fetch {url}")
            print(f"Error: {error}")