from src import db
from src.llm.gemini_client import LLMApiError
from src.models import ParsedApplication
from src.routes import applications as applications_routes


def test_get_index_empty(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Job Application Tracker" in response.text


def test_nav_links_present_on_home_page(client):
    response = client.get("/")
    assert 'href="/"' in response.text
    assert 'href="/applications"' in response.text
    assert 'href="/import-export"' in response.text


def test_home_page_shows_add_form_only(client):
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="text"' in response.text
    assert "<table" not in response.text
    assert "Export as CSV" not in response.text


def test_applications_page_shows_table_only(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    response = client.get("/applications")
    assert response.status_code == 200
    assert "Acme" in response.text
    assert "Engineer" in response.text
    assert 'id="text"' not in response.text
    assert "Export as CSV" not in response.text


def test_parse_happy_path(client, monkeypatch):
    monkeypatch.setattr(
        applications_routes,
        "extract_application",
        lambda text: ParsedApplication(company="Acme", role="Backend Engineer"),
    )
    response = client.post(
        "/applications/parse", data={"text": "Applied at Acme for Backend Engineer role"}
    )
    assert response.status_code == 200
    assert "Acme" in response.text
    assert "Backend Engineer" in response.text


def test_parse_empty_text_rejected(client):
    response = client.post("/applications/parse", data={"text": "   "})
    assert response.status_code == 200
    assert "enter application details" in response.text.lower()


def test_parse_llm_failure_falls_back_to_manual(client, monkeypatch):
    def raise_error(text):
        raise LLMApiError("boom")

    monkeypatch.setattr(applications_routes, "extract_application", raise_error)
    response = client.post(
        "/applications/parse", data={"text": "Applied at XYZ for ABC role"}
    )
    assert response.status_code == 200
    assert "fill in manually" in response.text.lower()


def test_create_application_and_list(client):
    response = client.post(
        "/applications",
        data={"company": "Acme", "role": "Backend Engineer", "status": "Applied"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Acme" in response.text
    assert "Backend Engineer" in response.text


def test_create_application_with_rounds_and_feedback(client):
    response = client.post(
        "/applications",
        data={
            "company": "Acme",
            "role": "Backend Engineer",
            "status": "Applied",
            "total_rounds": "3",
            "current_round": "1",
            "feedback": "Referral said 3 rounds",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    row = db.list_applications()[0]
    assert row["total_rounds"] == 3
    assert row["current_round"] == 1
    assert row["feedback"] == "Referral said 3 rounds"


def test_create_application_redirects_to_applications_page(client):
    response = client.post(
        "/applications",
        data={"company": "Acme", "role": "Backend Engineer", "status": "Applied"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/applications"


def test_create_application_blank_rounds_and_feedback_default_to_none(client):
    response = client.post(
        "/applications",
        data={"company": "Acme", "role": "Backend Engineer", "status": "Applied"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    row = db.list_applications()[0]
    assert row["total_rounds"] is None
    assert row["current_round"] is None
    assert row["feedback"] is None


def test_create_application_with_custom_date_applied(client):
    response = client.post(
        "/applications",
        data={
            "company": "Acme",
            "role": "Backend Engineer",
            "status": "Applied",
            "date_applied": "2020-05-05",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    row = db.list_applications()[0]
    assert row["date_applied"] == "2020-05-05"


def test_create_application_blank_date_applied_defaults_to_today(client):
    import datetime

    response = client.post(
        "/applications",
        data={"company": "Acme", "role": "Backend Engineer", "status": "Applied"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    row = db.list_applications()[0]
    assert row["date_applied"] == datetime.date.today().isoformat()


def test_status_dropdown_offers_exactly_five_options(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    response = client.get("/applications")
    for status in ["Applied", "Interviewing", "Offer", "Rejected", "Withdrawn"]:
        assert status in response.text


def test_update_status_redirects_to_applications_page(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    app_id = db.list_applications()[0]["id"]

    response = client.post(
        f"/applications/{app_id}/status", data={"status": "Interviewing"}, follow_redirects=False
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/applications"


def test_update_details_redirects_to_applications_page(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    app_id = db.list_applications()[0]["id"]

    response = client.post(
        f"/applications/{app_id}/details",
        data={"total_rounds": "3", "current_round": "1", "feedback": ""},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/applications"


def test_update_status_valid_persists(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    app_id = db.list_applications()[0]["id"]

    response = client.post(
        f"/applications/{app_id}/status", data={"status": "Interviewing"}, follow_redirects=True
    )
    assert response.status_code == 200
    assert db.list_applications()[0]["status"] == "Interviewing"


def test_update_status_invalid_value_rejected(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    app_id = db.list_applications()[0]["id"]

    response = client.post(f"/applications/{app_id}/status", data={"status": "NotAStatus"})
    assert response.status_code == 422
    assert db.list_applications()[0]["status"] == "Applied"


def test_update_status_can_move_backwards(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    app_id = db.list_applications()[0]["id"]

    client.post(f"/applications/{app_id}/status", data={"status": "Interviewing"}, follow_redirects=True)
    assert db.list_applications()[0]["status"] == "Interviewing"

    client.post(f"/applications/{app_id}/status", data={"status": "Applied"}, follow_redirects=True)
    assert db.list_applications()[0]["status"] == "Applied"


def test_update_details_valid_persists(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    app_id = db.list_applications()[0]["id"]

    response = client.post(
        f"/applications/{app_id}/details",
        data={"total_rounds": "4", "current_round": "1", "feedback": "Went well"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    row = db.list_applications()[0]
    assert row["total_rounds"] == 4
    assert row["current_round"] == 1
    assert row["feedback"] == "Went well"


def test_update_details_partial_update_preserves_other_fields(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    app_id = db.list_applications()[0]["id"]

    client.post(
        f"/applications/{app_id}/details",
        data={"total_rounds": "4", "current_round": "1", "feedback": "Went well"},
        follow_redirects=True,
    )
    client.post(
        f"/applications/{app_id}/details",
        data={"total_rounds": "4", "current_round": "2", "feedback": "Went well"},
        follow_redirects=True,
    )
    row = db.list_applications()[0]
    assert row["total_rounds"] == 4
    assert row["current_round"] == 2
    assert row["feedback"] == "Went well"


def test_update_details_current_round_can_exceed_total_rounds(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    app_id = db.list_applications()[0]["id"]

    response = client.post(
        f"/applications/{app_id}/details",
        data={"total_rounds": "4", "current_round": "5", "feedback": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    row = db.list_applications()[0]
    assert row["total_rounds"] == 4
    assert row["current_round"] == 5


def test_update_details_non_numeric_round_stored_as_unset(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    app_id = db.list_applications()[0]["id"]

    response = client.post(
        f"/applications/{app_id}/details",
        data={"total_rounds": "N/A", "current_round": "", "feedback": ""},
        follow_redirects=True,
    )
    assert response.status_code == 200
    row = db.list_applications()[0]
    assert row["total_rounds"] is None
    assert row["current_round"] is None


def test_applications_page_collapsed_columns_only(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    response = client.get("/applications")
    thead = response.text.split("<thead>")[1].split("</thead>")[0]
    assert "Company" in thead
    assert "Role" in thead
    assert "Date Applied" in thead
    assert "Status" in thead
    assert "Job Posting" not in thead
    assert "Total Rounds" not in thead
    assert "Current Round" not in thead
    assert "Feedback" not in thead


def test_applications_page_row_detail_hidden_and_contains_full_fields(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    app_id = db.list_applications()[0]["id"]
    client.post(
        f"/applications/{app_id}/details",
        data={"total_rounds": "4", "current_round": "2", "feedback": "Went well"},
        follow_redirects=True,
    )

    response = client.get("/applications")
    assert 'class="app-detail"' in response.text
    assert "hidden" in response.text

    detail = response.text.split('class="app-detail"')[1]
    assert "4" in detail
    assert "2" in detail
    assert "Went well" in detail
