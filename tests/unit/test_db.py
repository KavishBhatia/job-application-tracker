import datetime

from src import db


def test_list_applications_empty(temp_db):
    assert db.list_applications() == []


def test_create_and_list_application(temp_db):
    app_id = db.create_application(
        company="Acme", role="Engineer", source_text="Applied at Acme for Engineer"
    )
    apps = db.list_applications()
    assert len(apps) == 1
    assert apps[0]["id"] == app_id
    assert apps[0]["company"] == "Acme"
    assert apps[0]["role"] == "Engineer"
    assert apps[0]["status"] == "Applied"
    assert apps[0]["date_applied"] == datetime.date.today().isoformat()


def test_create_application_multiple_ordered_by_id(temp_db):
    id1 = db.create_application(company="A", role="R1")
    id2 = db.create_application(company="B", role="R2")
    apps = db.list_applications()
    assert [a["id"] for a in apps] == [id1, id2]


def test_create_application_with_job_post_url(temp_db):
    db.create_application(company="Acme", role="Engineer", job_post_url="https://example.com/job")
    apps = db.list_applications()
    assert apps[0]["job_post_url"] == "https://example.com/job"


def test_application_exists_matches_case_and_whitespace_insensitively(temp_db):
    db.create_application(company="Acme", role="Engineer")
    date_applied = db.list_applications()[0]["date_applied"]
    assert db.application_exists("acme", "engineer", date_applied) is True
    assert db.application_exists(" Acme ", " Engineer ", date_applied) is True


def test_application_exists_no_match(temp_db):
    db.create_application(company="Acme", role="Engineer")
    assert db.application_exists("Other Co", "Other Role", "2000-01-01") is False


def test_insert_imported_row_uses_given_date(temp_db):
    db.insert_imported_row(
        company="Acme", role="Engineer", date_applied="2020-05-05", status="Interviewing"
    )
    row = db.list_applications()[0]
    assert row["date_applied"] == "2020-05-05"
    assert row["status"] == "Interviewing"
