import pandas as pd

from scraper_utils import parse_html_table


def test_table_with_thead():
    html = """
    <table>
      <thead><tr><th>Country</th><th>2024</th></tr></thead>
      <tbody>
        <tr><td>Morocco</td><td>43 TWh</td></tr>
        <tr><td>Senegal</td><td>7 TWh</td></tr>
      </tbody>
    </table>
    """
    df = parse_html_table(html)
    assert list(df.columns) == ['Country', '2024']
    assert df.values.tolist() == [['Morocco', '43 TWh'], ['Senegal', '7 TWh']]


def test_table_without_thead_does_not_repeat_header_row():
    html = """
    <table>
      <tr><td>Consommation</td><td>2 790 MWh</td></tr>
      <tr><td>Production</td><td>3 000 MWh</td></tr>
    </table>
    """
    df = parse_html_table(html)
    assert list(df.columns) == ['Consommation', '2 790 MWh']
    assert df.values.tolist() == [['Production', '3 000 MWh']]


def test_thead_without_tbody_does_not_repeat_header_row():
    html = """
    <table>
      <thead><tr><th>A</th><th>B</th></tr></thead>
      <tr><td>1</td><td>2</td></tr>
    </table>
    """
    df = parse_html_table(html)
    assert df.values.tolist() == [['1', '2']]


def test_data_row_identical_to_header_is_kept():
    html = """
    <table>
      <tr><td>A</td><td>B</td></tr>
      <tr><td>A</td><td>B</td></tr>
    </table>
    """
    assert parse_html_table(html).values.tolist() == [['A', 'B']]


def test_ragged_rows_are_padded_or_truncated():
    html = """
    <table>
      <thead><tr><th>A</th><th>B</th><th>C</th></tr></thead>
      <tbody>
        <tr><td>1</td></tr>
        <tr><td>1</td><td>2</td><td>3</td><td>4</td></tr>
      </tbody>
    </table>
    """
    df = parse_html_table(html)
    assert df.shape == (2, 3)
    assert df.iloc[0, 0] == '1' and df.iloc[0, 1:].isna().all()
    assert df.iloc[1].tolist() == ['1', '2', '3']


def test_empty_rows_are_skipped():
    html = """
    <table>
      <thead><tr><th>A</th></tr></thead>
      <tbody><tr><td></td></tr><tr><td>x</td></tr></tbody>
    </table>
    """
    assert parse_html_table(html).values.tolist() == [['x']]


def test_table_index_selects_table():
    html = """
    <table><tr><th>first</th></tr><tr><td>1</td></tr></table>
    <table><tr><th>second</th></tr><tr><td>2</td></tr></table>
    """
    df = parse_html_table(html, table_index=1)
    assert list(df.columns) == ['second']


def test_no_table_returns_empty_dataframe():
    df = parse_html_table('<p>no table here</p>')
    assert isinstance(df, pd.DataFrame)
    assert df.empty
