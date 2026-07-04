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


def test_csv_round_trip_includes_rounds_and_feedback():
    rows = [
        {
            "id": 1,
            "company": "Acme",
            "role": "Engineer",
            "date_applied": "2026-01-01",
            "status": "Applied",
            "job_post_url": "",
            "source_text": "",
            "total_rounds": 4,
            "current_round": 1,
            "feedback": "Went well",
        }
    ]
    csv_text = to_csv(rows)
    assert "total_rounds" in csv_text
    assert "current_round" in csv_text
    assert "feedback" in csv_text
    parsed = from_csv(io.StringIO(csv_text))
    assert parsed[0]["total_rounds"] == "4"
    assert parsed[0]["current_round"] == "1"
    assert parsed[0]["feedback"] == "Went well"


def test_from_csv_missing_new_optional_columns():
    csv_text = "company,role\nAcme,Engineer\n"
    parsed = from_csv(io.StringIO(csv_text))
    assert "total_rounds" not in parsed[0]
    assert "current_round" not in parsed[0]
    assert "feedback" not in parsed[0]
