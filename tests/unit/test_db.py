import datetime
import sqlite3

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


def test_init_db_migrates_old_table_without_data_loss(tmp_path, monkeypatch):
    db_path = tmp_path / "old.db"
    monkeypatch.setattr(db, "DB_PATH", db_path)

    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            role TEXT NOT NULL,
            date_applied TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Applied',
            job_post_url TEXT,
            source_text TEXT
        );
        """
    )
    conn.execute(
        "INSERT INTO applications (company, role, date_applied, status) VALUES (?, ?, ?, ?)",
        ("Sephora", "HRBP", "2026-01-01", "Rejected"),
    )
    conn.commit()
    conn.close()

    db.init_db()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(applications)")}
    assert {"total_rounds", "current_round", "feedback"} <= columns

    row = conn.execute("SELECT * FROM applications").fetchone()
    conn.close()

    assert row["company"] == "Sephora"
    assert row["role"] == "HRBP"
    assert row["status"] == "Rejected"
    assert row["total_rounds"] is None
    assert row["current_round"] is None
    assert row["feedback"] is None


def test_init_db_is_idempotent_when_columns_already_exist(temp_db):
    db.init_db()
    db.init_db()
    columns = [row["name"] for row in db.get_connection().execute("PRAGMA table_info(applications)")]
    assert columns.count("total_rounds") == 1


def test_create_application_with_rounds_and_feedback(temp_db):
    db.create_application(
        company="Acme",
        role="Engineer",
        total_rounds=4,
        current_round=1,
        feedback="Went well, waiting to hear back",
    )
    row = db.list_applications()[0]
    assert row["total_rounds"] == 4
    assert row["current_round"] == 1
    assert row["feedback"] == "Went well, waiting to hear back"


def test_create_application_defaults_rounds_and_feedback_to_none(temp_db):
    db.create_application(company="Acme", role="Engineer")
    row = db.list_applications()[0]
    assert row["total_rounds"] is None
    assert row["current_round"] is None
    assert row["feedback"] is None


def test_insert_imported_row_with_rounds_and_feedback(temp_db):
    db.insert_imported_row(
        company="Acme",
        role="Engineer",
        date_applied="2020-05-05",
        total_rounds=3,
        current_round=2,
        feedback="Solid feedback",
    )
    row = db.list_applications()[0]
    assert row["total_rounds"] == 3
    assert row["current_round"] == 2
    assert row["feedback"] == "Solid feedback"


def test_update_details_updates_only_those_fields(temp_db):
    app_id = db.create_application(company="Acme", role="Engineer", status="Interviewing")
    original = db.list_applications()[0]

    db.update_details(app_id, total_rounds=4, current_round=2, feedback="Doing okay")

    row = db.list_applications()[0]
    assert row["total_rounds"] == 4
    assert row["current_round"] == 2
    assert row["feedback"] == "Doing okay"
    assert row["company"] == original["company"]
    assert row["role"] == original["role"]
    assert row["status"] == original["status"]
    assert row["date_applied"] == original["date_applied"]
