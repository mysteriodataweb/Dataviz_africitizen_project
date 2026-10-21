"""
Utility functions for web scraping with Selenium/Helium and BeautifulSoup.

Helium/Selenium are imported lazily, so the parsing and download helpers can be
used (and tested) without a browser installed.
"""

from io import StringIO

from bs4 import BeautifulSoup
import pandas as pd
import requests


def parse_html_table(html, table_index=0):
    """
    Parse the n-th <table> element of an HTML document into a pandas DataFrame.

    Parameters
    ----------
    html : str
        HTML source containing the table.
    table_index : int, optional
        Index of the table to parse when the page contains several (default: 0).

    Returns
    -------
    pd.DataFrame
        The parsed table. Returns an empty DataFrame if no table is found.

    Examples
    --------
    >>> html = '<table><tr><th>A</th></tr><tr><td>1</td></tr></table>'
    >>> parse_html_table(html)
       A
    0  1
    """
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')

    if len(tables) <= table_index:
        print('No <table> found in page source. The table may be rendered differently or inside an iframe.')
        return pd.DataFrame()
    tbl = tables[table_index]

    # Extract headers (if present) and keep track of the rows used as headers
    header_rows = []
    thead = tbl.find('thead')
    if thead:
        header_rows = thead.find_all('tr')
        headers = [th.get_text(strip=True) for th in thead.find_all('th')]
    else:
        # Fallback: try first row as header
        first_row = tbl.find('tr')
        header_rows = [first_row] if first_row else []
        headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])] if first_row else []

    # Header rows must not be duplicated as data rows (compared by identity:
    # BeautifulSoup tags with the same content are considered equal)
    header_ids = {id(tr) for tr in header_rows}
    tbody = tbl.find('tbody') or tbl
    rows = []
    for tr in tbody.find_all('tr'):
        if id(tr) in header_ids:
            continue
        cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
        # Skip empty rows
        if any(c != '' for c in cells):
            rows.append(cells)

    # Normalize row length to headers (pad with None)
    if headers:
        max_cols = len(headers)
        normalized = [
            r + [None] * (max_cols - len(r)) if len(r) < max_cols else r[:max_cols]
            for r in rows
        ]
        return pd.DataFrame(normalized, columns=headers)
    return pd.DataFrame(rows)


def scrape_table_from_url(url, headless=True, timeout_secs=30, chrome_options=None, table_index=0):
    """
    Scrape a <table> element from a URL using Selenium/Helium and parse it into a pandas DataFrame.

    Parameters
    ----------
    url : str
        The target URL containing the table to scrape.
    headless : bool, optional
        Whether to run Chrome in headless mode (default: True).
    timeout_secs : int, optional
        Maximum time (in seconds) to wait for the table to appear (default: 30).
    chrome_options : selenium.webdriver.chrome.options.Options, optional
        Custom Chrome options. If None, default safe options are used.
    table_index : int, optional
        Index of the table to parse when the page contains several (default: 0).

    Returns
    -------
    pd.DataFrame
        A pandas DataFrame containing the scraped table data.
        Returns an empty DataFrame if no table is found.

    Examples
    --------
    >>> from scraper_utils import scrape_table_from_url
    >>> url = 'https://ourworldindata.org/grapher/electricity-generation?tab=table'
    >>> df = scrape_table_from_url(url)
    >>> print(df.head())
    """
    from helium import start_chrome, wait_until, get_driver, kill_browser
    from selenium.webdriver.chrome.options import Options

    # Set default Chrome options if not provided
    if chrome_options is None:
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')

    # Ensure no leftover browser instances
    try:
        kill_browser()
    except Exception:
        pass

    # Start Chrome and navigate to the page
    start_chrome(url, headless=headless, options=chrome_options)

    # Wait until enough <table> elements appear on the page
    try:
        wait_until(
            lambda: len(get_driver().find_elements('tag name', 'table')) > table_index,
            timeout_secs=timeout_secs
        )
    except Exception as e:
        print(f'Table not found within {timeout_secs} seconds:', e)
        return pd.DataFrame()

    # Parse the rendered page source
    df = parse_html_table(get_driver().page_source, table_index=table_index)

    # Display basic info
    print(f'Extracted DataFrame shape: {df.shape}')

    return df


def download_csv(url, out_file=None, timeout_secs=60):
    """
    Download a CSV file (e.g. an Our World in Data grapher export) into a DataFrame.

    This is faster and more reliable than scraping the rendered table, which only
    shows a summary of the data.

    Parameters
    ----------
    url : str
        URL of the CSV file, e.g. 'https://ourworldindata.org/grapher/electricity-generation.csv'.
    out_file : str, optional
        If given, the raw file is also saved to this path.
    timeout_secs : int, optional
        Maximum time (in seconds) to wait for the server (default: 60).

    Returns
    -------
    pd.DataFrame
        The downloaded data.

    Raises
    ------
    requests.HTTPError
        If the server answers with an error status.
    """
    r = requests.get(url, timeout=timeout_secs)
    r.raise_for_status()

    if out_file:
        with open(out_file, 'wb') as f:
            f.write(r.content)
        print('Saved', out_file)

    return pd.read_csv(StringIO(r.content.decode('utf-8')))


def close_browser():
    """
    Close any open browser instances to free resources.

    Examples
    --------
    >>> from scraper_utils import close_browser
    >>> close_browser()
    """
    from helium import kill_browser

    try:
        kill_browser()
        print('Browser closed successfully.')
    except Exception as e:
        print('kill_browser() failed or browser already closed:', e)
