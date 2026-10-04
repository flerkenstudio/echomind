from ingest.simulator import load_simulated_day
from ingest.store import LocalStore, get_store


def test_round_trip():
    store = LocalStore()
    date = store.store_day(load_simulated_day())
    rec = store.get_day_record(date)
    assert rec["segment_count"] == 7
    assert rec["day"]["segments"][1]["speaker"] == "doctor_chen"


def test_missing_day_returns_none():
    assert LocalStore().get_day_record("1999-01-01") is None


def test_factory_local():
    assert isinstance(get_store(), LocalStore)
