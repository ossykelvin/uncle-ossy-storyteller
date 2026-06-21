"""Story Bible editor helper tests (UI-D).

Covers the data-shape detection and DataFrame<->records conversions that back
the spreadsheet editor. The Streamlit widgets themselves aren't exercised here.
"""
import pandas as pd

from ui.story_bible_ui import _is_scalar_list, _is_flat_dict_list, _records_from_df


def test_scalar_list_detection():
    assert _is_scalar_list(["betrayal", "redemption"]) is True
    assert _is_scalar_list([]) is False
    assert _is_scalar_list([{"name": "Ada"}]) is False


def test_flat_dict_list_detection():
    assert _is_flat_dict_list([{"name": "Ada", "role": "keeper"}]) is True
    assert _is_flat_dict_list([{"name": "Ada", "aka": ["A"]}]) is False  # nested -> not flat
    assert _is_flat_dict_list(["just a string"]) is False


def test_records_from_df_drops_empty_rows_and_nan():
    df = pd.DataFrame([
        {"name": "Ada", "notes": "keeper"},
        {"name": None, "notes": None},        # fully empty -> dropped
        {"name": "Mara", "notes": ""},
    ])
    records = _records_from_df(df)
    assert records == [
        {"name": "Ada", "notes": "keeper"},
        {"name": "Mara", "notes": ""},
    ]


def test_records_from_df_converts_none_to_empty_string():
    df = pd.DataFrame([{"name": "Ada", "role": None}])
    assert _records_from_df(df) == [{"name": "Ada", "role": ""}]
