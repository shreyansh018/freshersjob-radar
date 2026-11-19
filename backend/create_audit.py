import sqlite3
import csv
import random

DB_PATH = "data/jobs.db"
OUTPUT = "data/manual_audit.csv"

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

rows = conn.execute("""
    SELECT
        title,
        company,
        location,
        url,
        is_fresher_friendly,
        classification_reasoning,
        role_category,
        experience_level
    FROM jobs
""").fetchall()

conn.close()

if len(rows) < 50:
    print(f"Only {len(rows)} jobs available.")
    sample = rows
else:
    random.seed(42)
    sample = random.sample(rows, 50)

with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)

    writer.writerow([
        "title",
        "company",
        "location",
        "url",
        "ai_decision",
        "ai_reasoning",
        "role_category",
        "experience_level",
        "manual_decision",
        "correct"
    ])

    for job in sample:
        writer.writerow([
            job["title"],
            job["company"],
            job["location"],
            job["url"],
            job["is_fresher_friendly"],
            job["classification_reasoning"],
            job["role_category"],
            job["experience_level"],
            "",
            ""
        ])

print(f"Exported {len(sample)} jobs to {OUTPUT}")