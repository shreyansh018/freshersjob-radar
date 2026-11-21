beat_schedule = {
    "daily-ingestion": {
        "task": "ingestion.ingest_all",
        "schedule": 86400.0,
        "options": {"queue": "ingestion"},
    },
    "hourly-freshness": {
        "task": "maintenance.expire_unconfirmed",
        "schedule": 3600.0,
        "options": {"queue": "maintenance"},
    },
    "six-hour-source-health": {
        "task": "maintenance.source_health",
        "schedule": 21600.0,
        "options": {"queue": "maintenance"},
    },
}
