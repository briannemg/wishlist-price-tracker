"""
Project configuration settings.

This module centralized reusable project constants such as file paths,
supported retailers, and future database or logging locations.
"""

from pathlib import Path

# Resolve the project root directory dynamically so scripts can be run
# from any location without breaking relative paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Directory containing raw input data files
DATA_DIR = BASE_DIR / "data"

# Source CSV containing product URLs submitted by the user.
INPUT_CSV = DATA_DIR / "product_links.csv"

# Mapping used to identify supported retailers from URL domains.
# Additional stores can be added here as scraper support expands.
SUPPORTED_STORES = {
    "amazon": "Amazon",
    "target": "Target",
    "walmart": "Walmart",
    "scheels": "Scheels",
}