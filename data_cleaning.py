"""
Cleaning helpers for the Our World in Data electricity generation dataset.

Run as a script to regenerate the Power BI source file from the raw CSV:

    python data_cleaning.py
"""

import pandas as pd


RAW_FILE = 'electricity_generation.csv'
POWERBI_FILE = 'electricity_generation_countries.xlsx'
VALUE_COL = 'Electricity generation - TWh'

# Countries/territories that Our World in Data codes with an OWID_ prefix instead of
# an ISO 3166-1 alpha-3 code. Every other OWID_ code is an aggregate (e.g. OWID_WRL = World).
OWID_COUNTRY_CODES = {'OWID_KOS'}  # Kosovo

# ISO 3166-1 alpha-3 codes of the African countries and territories
# (same definition as the "Africa" region of Our World in Data).
AFRICAN_COUNTRY_CODES = {
    'DZA', 'AGO', 'BEN', 'BWA', 'BFA', 'BDI', 'CMR', 'CPV', 'CAF', 'TCD',
    'COM', 'COG', 'COD', 'CIV', 'DJI', 'EGY', 'GNQ', 'ERI', 'SWZ', 'ETH',
    'GAB', 'GMB', 'GHA', 'GIN', 'GNB', 'KEN', 'LSO', 'LBR', 'LBY', 'MDG',
    'MWI', 'MLI', 'MRT', 'MUS', 'MAR', 'MOZ', 'NAM', 'NER', 'NGA', 'RWA',
    'STP', 'SEN', 'SYC', 'SLE', 'SOM', 'ZAF', 'SSD', 'SDN', 'TZA', 'TGO',
    'TUN', 'UGA', 'ZMB', 'ZWE', 'ESH', 'REU', 'MYT', 'SHN',
}


def is_country_code(code):
    """
    Return a boolean Series telling which codes identify a country or territory.

    Aggregates (continents, income groups, G20, OECD, ...) have no code or an
    OWID_ code, while countries have an ISO 3166-1 alpha-3 code.

    Parameters
    ----------
    code : pd.Series
        The 'Code' column of an Our World in Data dataset.
    """
    code = code.fillna('')
    return code.str.fullmatch('[A-Z]{3}') | code.isin(OWID_COUNTRY_CODES)


def filter_countries(df):
    """
    Keep only the rows describing countries, based on the 'Code' column.

    This is more reliable than a hand-written list of regions, which easily misses
    aggregates such as 'G20 (Ember)', 'OECD (EI)' or 'High-income countries'.
    """
    return df[is_country_code(df['Code'])].copy()


def prepare_powerbi_dataset(df):
    """
    Build the dataset used by the Power BI report (Dataviz.pbix).

    The schema (Entity, Year as a date, 'Electricity generation - TWh') is kept
    identical to the original export so that the report can simply be refreshed.
    """
    countries = filter_countries(df).drop(columns=['Code'])
    countries['Year'] = pd.to_datetime(countries['Year'], format='%Y')
    return countries.reset_index(drop=True)


def country_coverage(df):
    """
    Number of countries with data for each year.

    The first and last years are covered by fewer countries (the Energy Institute
    series start in 1985, the Ember series in 2000, and the latest years are not
    yet published for every country): totals over these years are not comparable.
    """
    years = df['Year'].dt.year if pd.api.types.is_datetime64_any_dtype(df['Year']) else df['Year']
    return df.groupby(years)['Entity'].nunique()


def reference_year(df, min_share=0.99):
    """
    Latest year for which at least `min_share` of the countries have data.
    """
    coverage = country_coverage(df)
    complete = coverage[coverage >= min_share * df['Entity'].nunique()]
    return int(complete.index.max())


def categorize_production(value, low=10, high=100):
    """
    Classify an annual electricity production (in TWh).

    The default thresholds follow a logarithmic scale (10 and 100 TWh per year)
    because the distribution of production across countries is extremely skewed.
    """
    if value == 0:
        return 'No Production'
    elif value < low:
        return 'Low Production'
    elif value < high:
        return 'Medium Production'
    else:
        return 'High Production'


def main():
    raw = pd.read_csv(RAW_FILE)
    countries = prepare_powerbi_dataset(raw)
    countries.to_excel(POWERBI_FILE, index=False)
    print(f'Saved {POWERBI_FILE}: {countries.shape[0]} rows, {countries["Entity"].nunique()} countries')


if __name__ == '__main__':
    main()
