import io

from src.io_formats.excel_io import from_excel, to_excel


def test_excel_round_trip():
    rows = [
        {
            "id": 1,
            "company": "Acme",
            "role": "Engineer",
            "date_applied": "2026-01-01",
            "status": "Applied",
            "job_post_url": "",
            "source_text": "",
        }
    ]
    data = to_excel(rows)
    parsed = from_excel(io.BytesIO(data))
    assert parsed[0]["company"] == "Acme"
    assert parsed[0]["role"] == "Engineer"
    assert parsed[0]["date_applied"] == "2026-01-01"
    assert parsed[0]["status"] == "Applied"


def test_excel_from_excel_missing_optional_columns():
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.append(["company", "role"])
    ws.append(["Acme", "Engineer"])
    buffer = io.BytesIO()
    wb.save(buffer)

    parsed = from_excel(io.BytesIO(buffer.getvalue()))
    assert parsed[0]["company"] == "Acme"
    assert parsed[0]["role"] == "Engineer"
    assert "status" not in parsed[0]
