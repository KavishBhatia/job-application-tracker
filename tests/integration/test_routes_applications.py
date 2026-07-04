from src import db
from src.llm.gemini_client import LLMApiError
from src.models import ParsedApplication
from src.routes import applications as applications_routes


def test_get_index_empty(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Job Application Tracker" in response.text


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


def test_status_dropdown_offers_exactly_five_options(client):
    client.post("/applications", data={"company": "Acme", "role": "Engineer"}, follow_redirects=True)
    response = client.get("/")
    for status in ["Applied", "Interviewing", "Offer", "Rejected", "Withdrawn"]:
        assert status in response.text


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
