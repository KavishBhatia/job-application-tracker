import csv
import io

COLUMNS = ["id", "company", "role", "date_applied", "status", "job_post_url", "source_text"]


def to_csv(rows: list[dict]) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=COLUMNS)
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row.get(column, "") for column in COLUMNS})
    return output.getvalue()


def from_csv(file) -> list[dict]:
    content = file.read()
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    return [dict(row) for row in reader]
