from enum import Enum


class StrEnum(str, Enum):
    @classmethod
    def values(cls) -> list[str]:
        return [member.value for member in cls]


class JobStatus(StrEnum):
    ACTIVE = "active"
    STALE = "stale"
    EXPIRED = "expired"
    REMOVED = "removed"
    UNKNOWN = "unknown"


class RoleCategory(StrEnum):
    SOFTWARE_ENGINEERING = "Software Engineering"
    FRONTEND_DEVELOPMENT = "Frontend Development"
    BACKEND_DEVELOPMENT = "Backend Development"
    FULL_STACK_DEVELOPMENT = "Full Stack Development"
    MOBILE_DEVELOPMENT = "Mobile Development"
    DATA_ANALYTICS = "Data Analytics"
    DATA_SCIENCE = "Data Science"
    MACHINE_LEARNING = "Machine Learning"
    ARTIFICIAL_INTELLIGENCE = "Artificial Intelligence"
    DEVOPS = "DevOps"
    CLOUD = "Cloud"
    CYBERSECURITY = "Cybersecurity"
    QA_TESTING = "QA and Testing"
    PRODUCT_MANAGEMENT = "Product Management"
    PRODUCT_DESIGN = "Product Design"
    UI_UX = "UI/UX"
    BUSINESS = "Business"
    FINANCE = "Finance"
    MARKETING = "Marketing"
    SALES = "Sales"
    OPERATIONS = "Operations"
    HR = "HR"
    CUSTOMER_SUPPORT = "Customer Support"
    RESEARCH = "Research"
    HARDWARE = "Hardware"
    OTHER = "Other"


class ExperienceLevel(StrEnum):
    INTERNSHIP = "Internship"
    FRESHER = "Fresher"
    GRADUATE = "Graduate"
    ENTRY_LEVEL = "Entry Level"
    EARLY_CAREER = "Early Career"
    EXPERIENCED = "Experienced"
    UNKNOWN = "Unknown"


class EmploymentType(StrEnum):
    FULL_TIME = "Full-time"
    INTERNSHIP = "Internship"
    PART_TIME = "Part-time"
    CONTRACT = "Contract"
    TEMPORARY = "Temporary"
    APPRENTICESHIP = "Apprenticeship"
    OTHER = "Other"
    UNKNOWN = "Unknown"


class WorkplaceType(StrEnum):
    ONSITE = "On-site"
    HYBRID = "Hybrid"
    REMOTE = "Remote"
    UNKNOWN = "Unknown"


class RemoteScope(StrEnum):
    INDIA = "india"
    WORLDWIDE = "worldwide"
    NONE = "none"
    UNKNOWN = "unknown"


class RelevanceState(StrEnum):
    STRONG = "strong"
    POSSIBLE = "possible"
    EXPERIENCED = "experienced"
    UNCERTAIN = "uncertain"


class SourceHealth(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    DISABLED = "disabled"
    UNKNOWN = "unknown"
