"""
Parse product metadata from downloaded HTML files.

This module extracts product information from saved retailer webpages.
It starts with broadly reusable strategies, including JSON-LD structured
data and Open Graph/meta tags.
"""

import json
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


def load_html(file_path: Path) -> str:
    """Load HTML content from a local file.

    Args:
        file_path (Path): Path to the saved HTML file.

    Returns:
        str: Raw HTML content.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
    
    
def extract_json_ld(soup: BeautifulSoup) -> dict[str, Any] | None:
    """Extract product data from JSON-LD structured data.
    
    JSON-LD is often the cleanest source of product metadata because
    retailers use it to describe products for search engines.

    Args:
        soup (BeautifulSoup): Parsed HTML document.

    Returns:
        dict[str, Any] | None: Product JSON-LD data if found, otherwise None.
    """
    scripts = soup.find_all("script", type="application/ld+json")
    
    for script in scripts:
        if not script.string:
            continue
        
        try:
            data = json.loads(script.string)
        except json.JSONDecodeError:
            continue
        
        if isinstance(data, dict) and data.get("@type") == "Product":
            return data
        
    return None


def extract_meta_content(soup: BeautifulSoup, property_name: str) -> str | None:
    """Extract content from a meta tag.

    Args:
        soup (BeautifulSoup): Parsed HTML document.
        property_name (str): Meta property or name value to search for.

    Returns:
        str | None: Meta tag content if found, otherwise None.
    """
    tag = soup.find("meta", property=property_name) or soup.find(
        "meta", attrs={"name": property_name}
    )
    
    if tag and tag.get("content"):
        content = tag.get("content")
        
        if isinstance(content, str):
            return content.strip()
    
    return None


def parse_product_html(html: str, store: str | None = None) -> dict[str, Any]:
    """Parse product metadata from HTML.
    
    The parser first tries JSON-LD structured data. If unavailable, it
    falls back to Open Graph/meta tags, which usually provide title,
    description, image, and canonical URL.

    Args:
        html (str): Raw HTML content.
        store (str | None, optional): Optional retailer name.

    Returns:
        dict[str, Any]: Parsed product metadata.
    """
    soup = BeautifulSoup(html, "lxml")
    
    product_data = {
        "store": store,
        "name": None,
        "brand": None,
        "price": None,
        "currency": None,
        "image_url": None,
        "product_url": None,
        "sku": None,
        "gtin": None,
        "availability": None,
        "source": None,
    }
    
    json_ld = extract_json_ld(soup)
    
    if json_ld:
        offers = json_ld.get("offers", {})
        brand = json_ld.get("brand", {})
        
        product_data.update(
            {
                "name": json_ld.get("name"),
                "brand": brand.get("name") if isinstance(brand, dict) else brand,
                "price": offers.get("price") if isinstance(offers, dict) else None,
                "currency": (
                    offers.get("priceCurrency") if isinstance(offers, dict) else None
                ),
                "image_url": _first_value(json_ld.get("image")),
                "product_url": (
                    offers.get("url")
                    if isinstance(offers, dict)
                    else json_ld.get("@id")
                ),
                "sku": json_ld.get("sku"),
                "gtin": json_ld.get("gtin"),
                "availability": (
                    offers.get("availability") if isinstance(offers, dict) else None
                ),
                "source": "json_ld",
            }
        )
        
        return product_data
    
    product_data.update(
        {
            "name": extract_meta_content(soup, "og:title") or _title_text(soup),
            "brand": None,
            "price": None,
            "currency": None,
            "image_url": extract_meta_content(soup, "og:image"),
            "product_url": extract_meta_content(soup, "og:url"),
            "source": "meta_tags",
        }
    )
    
    return product_data


def _first_value(value: Any) -> Any:
    """Return the first item from a list or the value itselt.

    Args:
        value (Any): Possible list or scalar value.

    Returns:
        Any: First list item or original value.
    """
    if isinstance(value, list):
        return value[0] if value else None
    
    return value


def _title_text(soup: BeautifulSoup) -> str | None:
    """Extract plain text from the HTML title tag.

    Args:
        soup (BeautifulSoup): Parsed HTML document.

    Returns:
        str | None: Page title text if available.
    """
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    
    return None


if __name__ == "__main__":
    test_file = Path("data/html/4_target_page.html")
    html_content = load_html(test_file)
    product = parse_product_html(html_content, store="Target")
    
    print(product)