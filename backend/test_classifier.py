from app.pipeline.schemas import JobRecord
from app.pipeline.classifier import classify_job


def main():
    job = JobRecord(
        source="manual_test",
        source_id="test-001",
        title="Software Engineer Intern",
        company="Example Company",
        location="Bengaluru, India",
        description=(
            "We are hiring a Software Engineer Intern. "
            "Students pursuing a bachelor's degree are welcome. "
            "Experience with Python is preferred."
        ),
        url="https://example.com/job/test-001",
    )

    result = classify_job(job)

    print("\n========== AI CLASSIFICATION ==========")
    print(result.model_dump_json(indent=2))
    print("======================================")


if __name__ == "__main__":
    main()