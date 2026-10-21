import os

import pandas as pd

import data_cleaning as dc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_raw():
    return pd.DataFrame({
        'Entity': ['Morocco', 'Kosovo', 'World', 'Africa', 'G20 (Ember)', 'Niue'],
        'Code': ['MAR', 'OWID_KOS', 'OWID_WRL', None, None, 'NIU'],
        'Year': [2022] * 6,
        dc.VALUE_COL: [41.5, 6.1, 28926.9, 923.4, 24000.0, 0.0],
    })


def test_filter_countries_removes_aggregates():
    countries = dc.filter_countries(make_raw())
    assert countries['Entity'].tolist() == ['Morocco', 'Kosovo', 'Niue']


def test_prepare_powerbi_dataset_keeps_original_schema():
    out = dc.prepare_powerbi_dataset(make_raw())
    assert list(out.columns) == ['Entity', 'Year', dc.VALUE_COL]
    assert pd.api.types.is_datetime64_any_dtype(out['Year'])
    assert out['Year'].dt.year.tolist() == [2022, 2022, 2022]


def test_reference_year_is_last_year_with_full_coverage():
    df = pd.DataFrame({
        'Entity': ['A', 'B', 'A', 'B', 'A'],
        'Year': [2021, 2021, 2022, 2022, 2023],
        dc.VALUE_COL: [1, 2, 3, 4, 5],
    })
    assert dc.reference_year(df) == 2022
    assert dc.country_coverage(df).to_dict() == {2021: 2, 2022: 2, 2023: 1}


def test_categorize_production():
    assert dc.categorize_production(0) == 'No Production'
    assert dc.categorize_production(0.5) == 'Low Production'
    assert dc.categorize_production(10) == 'Medium Production'
    assert dc.categorize_production(99.9) == 'Medium Production'
    assert dc.categorize_production(100) == 'High Production'


def test_african_codes_are_country_codes():
    assert dc.is_country_code(pd.Series(sorted(dc.AFRICAN_COUNTRY_CODES))).all()


def test_powerbi_file_is_in_sync_with_raw_data():
    raw = pd.read_csv(os.path.join(ROOT, dc.RAW_FILE))
    xlsx = pd.read_excel(os.path.join(ROOT, dc.POWERBI_FILE))
    expected = dc.prepare_powerbi_dataset(raw)
    assert list(xlsx.columns) == list(expected.columns)
    assert sorted(xlsx['Entity'].unique()) == sorted(expected['Entity'].unique())
    assert len(xlsx) == len(expected)
