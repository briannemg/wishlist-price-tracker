"""
Process downloaded HTML files into structured product data.

This module loops through all saved HTML pages, extracts product
metadata, and combines the results into a structured dataframe
for downstream matching and price comparison.
"""

import pandas as pd

from src.config import HTML_DIR
from src.parse_product import load_html, parse_product_html


def extract_store_from_filename(filename: str) -> str:
    """Extract retailer name from saved HTML filename.
    
    Expected filename format:
    
        0_amazon_page.html
        3_target_page.html

    Args:
        filename (str): HTML filename.

    Returns:
        str: Parsed store name.
    """
    parts = filename.split("_")
    
    if len(parts) >= 2:
        return parts[1].capitalize()
    
    return "Unknown"


def process_html_files() -> pd.DataFrame:
    """Parse all saved HTML files and collect product metadata.

    Returns:
        pd.DataFrame: Dataframe containing parsed product information.
    """
    products = []
    
    html_files = HTML_DIR.glob("*.html")
    
    for file_path in html_files:
        print(f"Processing: {file_path.name}")
        
        store = extract_store_from_filename(file_path.name)
        
        try:
            html = load_html(file_path)
            product = parse_product_html(html, store=store)
            
            products.append(product)
            
        except Exception as error:
            print(f"Failed: {file_path.name}")
            print(error)
            
    df = pd.DataFrame(products)
    
    return df[
        [
            "store",
            "name",
            "brand",
            "price",
            "currency",
            "source"
        ]
    ]


if __name__ == "__main__":
    products_df = process_html_files()
    
    print("\nParsed Products:\n")
    print(products_df)