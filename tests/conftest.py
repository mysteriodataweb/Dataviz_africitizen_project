import os
import sys

# Make the project modules (scraper_utils, data_cleaning) importable from the tests
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
