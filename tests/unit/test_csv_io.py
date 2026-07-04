import io

from src.io_formats.csv_io import from_csv, to_csv


def test_csv_round_trip():
    rows = [
        {
            "id": 1,
            "company": "Acme",
            "role": "Engineer",
            "date_applied": "2026-01-01",
            "status": "Applied",
            "job_post_url": "",
            "source_text": "Applied at Acme",
        }
    ]
    csv_text = to_csv(rows)
    parsed = from_csv(io.StringIO(csv_text))
    assert parsed[0]["company"] == "Acme"
    assert parsed[0]["role"] == "Engineer"
    assert parsed[0]["date_applied"] == "2026-01-01"
    assert parsed[0]["status"] == "Applied"


def test_from_csv_missing_optional_columns():
    csv_text = "company,role\nAcme,Engineer\n"
    parsed = from_csv(io.StringIO(csv_text))
    assert parsed[0]["company"] == "Acme"
    assert parsed[0]["role"] == "Engineer"
    assert "status" not in parsed[0]
