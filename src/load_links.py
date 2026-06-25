"""
Utilities for loading and preprocessing product URLs.

This module reads product URLs from a CSV file, performs basic URL
normalization, and identifies which retailer each link belongs to.
"""

from urllib.parse import urlparse, urlunparse

import pandas as pd

from config import INPUT_CSV, SUPPORTED_STORES


def clean_url(url: str) -> str:
    """Normalize a product URL.
    
    Removes URL fragments while preserving the core product path and
    query parameters. This creates a cleaner version of the URL for
    storage and future processing.

    Args:
        url (str): Raw product URL from the input CSV.

    Returns:
        str: Normalized product URL.
    """
    parsed = urlparse(url.strip())
    
    cleaned = urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            "",
            parsed.query,
            "",
        )
    )
    
    return cleaned


def detect_store(url: str) -> str:
    """Identify the retailer associated with a product URL.
    
    The function compares the domain name against the list of
    currently supported retailers defined in the configuration module.

    Args:
        url (str): Product URL.

    Returns:
        str: Standardized store name if recognized, otherwise 'Unknown'.
    """
    domain = urlparse(url).netloc.lower()
    
    for key, store_name in SUPPORTED_STORES.items():
        if key in domain:
            return store_name
        
    return "Unknown"


def load_product_links() -> pd.DataFrame:
    """Load product URLs from CSV and apply preprocessing steps.
    
    The function validates the input file structure, creates a cleaned
    version of each URL, and identifies the source retailer.

    Returns:
        pd.DataFrame: DataFrame containing original URL, cleaned URL,
                      and detected store.
                      
    Raises:
        ValueError: Raised if the input CSV does not contain a 'url' column.
    """
    df = pd.read_csv(INPUT_CSV)
    
    if "url" not in df.columns:
        raise ValueError("Input CSV must contain a 'url' column.")
    
    df["clean_url"] = df["url"].apply(clean_url)
    df["store"] = df["clean_url"].apply(detect_store)
    
    return df


if __name__ == "__main__":
    product_links = load_product_links()
    
    print("\nLoaded product links:\n")
    print(product_links[["store", "clean_url"]])