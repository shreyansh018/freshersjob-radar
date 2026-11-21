import re

from app.ingestion.experience import ExperienceInfo
from app.ingestion.location import LocationInfo
from app.ingestion.relevance import RelevanceResult
from app.models.enums import EmploymentType, ExperienceLevel, RoleCategory, WorkplaceType

SENIOR_TITLE = re.compile(
    r"\b(senior|sr\.?|staff|principal|lead|manager|director|head of|architect|expert|iii|iv)\b",
    re.I,
)
# Word boundaries matter: "Internal Auditor" must not match "intern".
INTERN_TITLE = re.compile(r"\b(intern|internship|internships)\b", re.I)
# India-style fresher titles: "Software Engineer I", "SDE 1", "Graduate Engineer
# Trainee", "new grad", "campus hire", "0-1 years".
FRESHER_TITLE = re.compile(
    r"\b(?:sde|swe|engineer|developer|analyst)\s*[-/,]?\s*(?:i|1)\b"
    r"|\b(?:fresher|new\s+grad(?:uate)?|graduate|campus\s+(?:hire|program|grad))\b"
    r"|\b(?:trainee|apprentice|apprenticeship)\b"
    r"|\b0\s*[-–]\s*[12]\b",
    re.I,
)

ROLE_KEYWORDS: list[tuple[RoleCategory, tuple[str, ...]]] = [
    (RoleCategory.FRONTEND_DEVELOPMENT, ("frontend", "front end", "react", "angular", "vue", "ui engineer")),
    (RoleCategory.BACKEND_DEVELOPMENT, ("backend", "back end", "node", "python", "java", "django", "spring")),
    (RoleCategory.FULL_STACK_DEVELOPMENT, ("full stack", "fullstack", "full-stack")),
    (RoleCategory.MOBILE_DEVELOPMENT, ("android", "ios", "flutter", "react native", "mobile")),
    (RoleCategory.DATA_SCIENCE, ("data scientist", "data science")),
    (RoleCategory.MACHINE_LEARNING, ("machine learning", "ml engineer", "deep learning")),
    (RoleCategory.ARTIFICIAL_INTELLIGENCE, ("ai engineer", "generative ai", "llm")),
    (RoleCategory.DATA_ANALYTICS, ("data analyst", "analytics", "business intelligence", "sql analyst")),
    (RoleCategory.DEVOPS, ("devops", "sre", "site reliability", "kubernetes")),
    (RoleCategory.CLOUD, ("cloud engineer", "aws", "azure", "gcp")),
    (RoleCategory.CYBERSECURITY, ("security", "cyber", "penetration")),
    (RoleCategory.QA_TESTING, ("qa", "quality assurance", "test engineer", "sdet")),
    (RoleCategory.UI_UX, ("ux", "ui designer", "product designer", "designer")),
    (RoleCategory.PRODUCT_MANAGEMENT, ("product manager", "product management")),
    (RoleCategory.SALES, ("sales", "business development", "account executive", "account development", "account manager")),
    (RoleCategory.MARKETING, ("marketing", "growth", "seo")),
    (RoleCategory.FINANCE, ("finance", "accountant", "financial analyst", "fp&a", "ap & expenses", "payments", "treasury")),
    (RoleCategory.HR, ("hr", "human resource", "recruiter", "people operations", "benefits", "talent acquisition", "payroll")),
    (RoleCategory.OPERATIONS, ("operations", "business support", "program manager", "operations analyst")),
    (RoleCategory.CUSTOMER_SUPPORT, ("customer support", "customer success", "support executive", "support engineer", "support specialist", "technical support", "customer service")),
    (RoleCategory.SOFTWARE_ENGINEERING, ("software engineer", "software developer", "sde", "engineer", "developer")),
]


def infer_role(title: str) -> RoleCategory:
    lowered = title.lower()
    for category, keywords in ROLE_KEYWORDS:
        if any(keyword in lowered for keyword in keywords):
            return category
    return RoleCategory.OTHER


def infer_level(
    title: str, relevance: RelevanceResult, experience: ExperienceInfo | None = None
) -> ExperienceLevel:
    """Tag seniority for fresher-through-experienced browsing."""
    lowered = title.lower()
    if INTERN_TITLE.search(title):
        return ExperienceLevel.INTERNSHIP
    if FRESHER_TITLE.search(title) or "early career" in lowered:
        return ExperienceLevel.FRESHER
    min_years = (experience.min_years or 0) if experience and experience.explicit else 0
    if relevance.state.value == "experienced" or SENIOR_TITLE.search(title) or min_years >= 3:
        return ExperienceLevel.EXPERIENCED
    if any(word in lowered for word in ("graduate", "entry", "associate", "trainee", "junior")):
        return ExperienceLevel.ENTRY_LEVEL
    if relevance.state.value == "possible" or min_years >= 1:
        return ExperienceLevel.EARLY_CAREER
    return ExperienceLevel.UNKNOWN


def deterministic_fields(
    *, title: str, relevance: RelevanceResult, location: LocationInfo,
    employment_type_raw: str | None, experience: ExperienceInfo | None = None,
) -> dict:
    employment = EmploymentType.UNKNOWN
    if employment_type_raw:
        lowered = employment_type_raw.lower()
        for member in EmploymentType:
            if member.value.lower() in lowered or lowered in member.value.lower():
                employment = member
                break
    if INTERN_TITLE.search(title) or "intern" in (employment_type_raw or "").lower():
        employment = EmploymentType.INTERNSHIP

    workplace = WorkplaceType.ONSITE
    if location.workplace_type != WorkplaceType.ONSITE:
        workplace = location.workplace_type

    level = infer_level(title, relevance, experience)
    return {
        "role_category": infer_role(title),
        "experience_level": level,
        "fresher_friendly": level
        in {
            ExperienceLevel.INTERNSHIP,
            ExperienceLevel.FRESHER,
            ExperienceLevel.ENTRY_LEVEL,
        }
        or relevance.state.value in {"strong", "possible"},
        "employment_type": employment,
        "workplace_type": workplace,
        "city": location.city,
        "skills": [],
        "degree_requirements": [],
    }
