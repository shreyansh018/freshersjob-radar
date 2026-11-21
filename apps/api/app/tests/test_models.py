from app.models import SavedJob


def test_saved_job_exposes_job_relationship():
    """The saved-jobs endpoint eager-loads SavedJob.job; keep the mapper intact."""
    assert hasattr(SavedJob, "job")
