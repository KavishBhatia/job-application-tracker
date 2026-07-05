from src import db


def test_import_export_page_shows_controls_only(client):
    response = client.get("/import-export")
    assert response.status_code == 200
    assert "Export as CSV" in response.text
    assert 'id="file"' in response.text
    assert 'id="text"' not in response.text
    assert "<table" not in response.text


def test_export_csv_and_reimport_skips_duplicates(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    export_resp = client.get("/export.csv")
    assert export_resp.status_code == 200
    csv_content = export_resp.content

    import_resp = client.post(
        "/import",
        files={"file": ("applications.csv", csv_content, "text/csv")},
        follow_redirects=True,
    )
    assert import_resp.status_code == 200
    assert "Imported: 0" in import_resp.text
    assert "Skipped as duplicates: 1" in import_resp.text
    assert len(db.list_applications()) == 1


def test_export_excel_and_reimport_skips_duplicates(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    export_resp = client.get("/export.xlsx")
    assert export_resp.status_code == 200
    xlsx_content = export_resp.content

    import_resp = client.post(
        "/import",
        files={
            "file": (
                "applications.xlsx",
                xlsx_content,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        follow_redirects=True,
    )
    assert import_resp.status_code == 200
    assert "Imported: 0" in import_resp.text
    assert "Skipped as duplicates: 1" in import_resp.text
    assert len(db.list_applications()) == 1


def test_import_mixed_new_and_invalid_rows(client):
    csv_content = (
        "id,company,role,date_applied,status,job_post_url,source_text\n"
        ",NewCo,New Role,2026-01-01,Applied,,\n"
        ",,MissingCompanyRole,2026-01-01,Applied,,\n"
    ).encode("utf-8")

    response = client.post(
        "/import",
        files={"file": ("applications.csv", csv_content, "text/csv")},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Imported: 1" in response.text
    assert "Rejected: 1" in response.text

    apps = db.list_applications()
    assert len(apps) == 1
    assert apps[0]["company"] == "NewCo"
    assert apps[0]["date_applied"] == "2026-01-01"


def test_import_row_with_missing_status_defaults_to_applied(client):
    csv_content = (
        "company,role,date_applied\n"
        "NewCo,New Role,2026-01-01\n"
    ).encode("utf-8")

    response = client.post(
        "/import",
        files={"file": ("applications.csv", csv_content, "text/csv")},
        follow_redirects=True,
    )
    assert response.status_code == 200
    apps = db.list_applications()
    assert apps[0]["status"] == "Applied"


def test_import_row_with_invalid_status_rejected(client):
    csv_content = (
        "company,role,date_applied,status\n"
        "NewCo,New Role,2026-01-01,NotAStatus\n"
    ).encode("utf-8")

    response = client.post(
        "/import",
        files={"file": ("applications.csv", csv_content, "text/csv")},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Rejected: 1" in response.text
    assert db.list_applications() == []


def test_import_row_with_non_numeric_round_value_is_not_rejected(client):
    csv_content = (
        "company,role,date_applied,total_rounds,current_round,feedback\n"
        "NewCo,New Role,2026-01-01,N/A,2,Went okay\n"
    ).encode("utf-8")

    response = client.post(
        "/import",
        files={"file": ("applications.csv", csv_content, "text/csv")},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Imported: 1" in response.text
    apps = db.list_applications()
    assert len(apps) == 1
    assert apps[0]["total_rounds"] is None
    assert apps[0]["current_round"] == 2
    assert apps[0]["feedback"] == "Went okay"


def test_export_then_import_round_trip_preserves_rounds_and_feedback(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    app_id = db.list_applications()[0]["id"]
    client.post(
        f"/applications/{app_id}/details",
        data={"total_rounds": "4", "current_round": "2", "feedback": "Good progress"},
        follow_redirects=True,
    )

    export_resp = client.get("/export.csv")
    assert "4" in export_resp.text
    assert "Good progress" in export_resp.text

    import_resp = client.post(
        "/import",
        files={"file": ("applications.csv", export_resp.content, "text/csv")},
        follow_redirects=True,
    )
    assert "Skipped as duplicates: 1" in import_resp.text
    apps = db.list_applications()
    assert len(apps) == 1
    assert apps[0]["total_rounds"] == 4
    assert apps[0]["current_round"] == 2
    assert apps[0]["feedback"] == "Good progress"
