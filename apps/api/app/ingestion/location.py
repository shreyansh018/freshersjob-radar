import re
from dataclasses import dataclass

from app.models.enums import RemoteScope, WorkplaceType

# City -> aliases. Kept deliberately explicit so we do not guess locations.
INDIAN_CITIES: dict[str, list[str]] = {
    "Bengaluru": ["bengaluru", "bangalore", "bangaluru"],
    "Mumbai": ["mumbai", "bombay"],
    "Delhi": ["delhi", "new delhi", "ncr", "gurgaon", "gurugram", "noida", "ghaziabad"],
    "Hyderabad": ["hyderabad", "secunderabad"],
    "Chennai": ["chennai", "madras"],
    "Pune": ["pune", "pimpri"],
    "Kolkata": ["kolkata", "calcutta"],
    "Ahmedabad": ["ahmedabad"],
    "Jaipur": ["jaipur"],
    "Kochi": ["kochi", "cochin"],
    "Coimbatore": ["coimbatore"],
    "Indore": ["indore"],
    "Chandigarh": ["chandigarh"],
    "Nagpur": ["nagpur"],
    "Lucknow": ["lucknow"],
    "Bhopal": ["bhopal"],
    "Visakhapatnam": ["visakhapatnam", "vizag"],
    "Vadodara": ["vadodara", "baroda"],
    "Nashik": ["nashik"],
    "Thiruvananthapuram": ["thiruvananthapuram", "trivandrum"],
    "Mangaluru": ["mangaluru", "mangalore"],
    "Mysuru": ["mysuru", "mysore"],
    "Navi Mumbai": ["navi mumbai"],
    "Gandhinagar": ["gandhinagar"],
    "Guwahati": ["guwahati"],
    "Patna": ["patna"],
    "Bhubaneswar": ["bhubaneswar"],
    "Dehradun": ["dehradun"],
    "Rajkot": ["rajkot"],
    "Surat": ["surat"],
    "Varanasi": ["varanasi", "banaras"],
    "Amritsar": ["amritsar"],
    "Jodhpur": ["jodhpur"],
    "Madurai": ["madurai"],
    "Tiruchirappalli": ["tiruchirappalli", "trichy"],
    "Agra": ["agra"],
    "Meerut": ["meerut"],
    "Kanpur": ["kanpur"],
    "Jabalpur": ["jabalpur"],
    "Raipur": ["raipur"],
    "Ranchi": ["ranchi"],
    "Shimla": ["shimla"],
    "Srinagar": ["srinagar"],
    "Puducherry": ["puducherry", "pondicherry"],
    "Goa": ["goa", "panaji", "panjim"],
    "Gurugram": ["gurugram", "gurgaon"],
    "Noida": ["noida"],
}

INDIAN_STATES = [
    "maharashtra", "karnataka", "tamil nadu", "telangana", "delhi", "gujarat",
    "rajasthan", "west bengal", "uttar pradesh", "kerala", "punjab", "haryana",
    "madhya pradesh", "andhra pradesh", "odisha", "assam", "jharkhand", "chhattisgarh",
    "himachal pradesh", "uttarakhand", "goa", "bihar", "jammu and kashmir", "puducherry",
]

REMOTE_PATTERN = re.compile(r"\b(remote|work from home|wfh|anywhere|distributed team)\b", re.I)
HYBRID_PATTERN = re.compile(r"\b(hybrid|partially remote|3 days in office)\b", re.I)
INDIA_PATTERN = re.compile(r"\bindia\b|\bbharat\b|\bindian\b", re.I)
WORLDWIDE_PATTERN = re.compile(r"\bworldwide\b|\bglobal(ly)?\b|\banywhere in the world\b", re.I)
INR_PATTERN = re.compile(r"(₹|\binr\b|\blakhs?\b|\bcrore\b|\blpa\b)", re.I)

# Explicit foreign locations in the location field override incidental mentions
# of India in the description (e.g. "Pittsburgh, PA" + an India privacy notice).
FOREIGN_LOCATION_PATTERN = re.compile(
    r"\b(usa|u\.s\.|united states|uk|united kingdom|england|scotland|wales|"
    r"canada|australia|singapore|germany|france|netherlands|ireland|"
    r"switzerland|japan|china|brazil|mexico|new zealand|"
    r"new york|san francisco|los angeles|seattle|boston|chicago|london|"
    r"toronto|sydney|berlin|paris|amsterdam|dublin|zurich|tokyo|"
    r"ny|ca|tx|wa|ma|il|pa)\b",
    re.I,
)


@dataclass
class LocationInfo:
    country: str | None
    city: str | None
    state: str | None
    workplace_type: WorkplaceType
    remote_scope: RemoteScope
    india_eligible: bool
    normalized_location: str


def _find_city(text: str) -> str | None:
    for city, aliases in INDIAN_CITIES.items():
        for alias in aliases:
            if re.search(rf"\b{re.escape(alias)}\b", text, re.I):
                return city
    return None


def _find_state(text: str) -> str | None:
    for state in INDIAN_STATES:
        if re.search(rf"\b{re.escape(state)}\b", text, re.I):
            return state.title()
    return None


def parse_location(original_location: str | None, description: str | None = None) -> LocationInfo:
    location_text = original_location or ""
    description_text = description or ""
    combined = f"{location_text}\n{description_text[:3000]}"

    location_text = location_text.strip()
    negative_remote = bool(re.search(r"\b(not remote|no remote|remote not (allowed|available|possible))\b", combined, re.I))
    is_remote = bool(REMOTE_PATTERN.search(combined)) and not negative_remote
    is_hybrid = bool(HYBRID_PATTERN.search(combined)) and not negative_remote

    if is_remote:
        workplace = WorkplaceType.REMOTE
    elif is_hybrid:
        workplace = WorkplaceType.HYBRID
    else:
        workplace = WorkplaceType.ONSITE

    location_city = _find_city(location_text)
    location_state = _find_state(location_text)
    location_has_india = (
        bool(INDIA_PATTERN.search(location_text))
        or location_city is not None
        or location_state is not None
    )
    foreign_location = bool(FOREIGN_LOCATION_PATTERN.search(location_text))
    description_india = bool(INDIA_PATTERN.search(description_text[:2000]))
    inr_signal = bool(INR_PATTERN.search(description_text[:2000]))

    # A clearly foreign location wins over incidental India/INR mentions in the
    # description. Otherwise fall back to description signals for ambiguous
    # locations such as "In-Office" or for remote roles.
    if foreign_location and not location_has_india:
        has_india_signal = False
        city = None
    elif location_has_india:
        has_india_signal = True
        city = location_city
    else:
        has_india_signal = description_india or inr_signal
        city = location_city or _find_city(description_text[:2000])
    state = location_state

    explicit_worldwide = bool(WORLDWIDE_PATTERN.search(location_text))
    if is_remote:
        if explicit_worldwide:
            remote_scope = RemoteScope.WORLDWIDE
        elif has_india_signal:
            remote_scope = RemoteScope.INDIA
        else:
            remote_scope = RemoteScope.UNKNOWN
    else:
        remote_scope = RemoteScope.NONE

    # Worldwide-only remote without an explicit India signal is deliberately excluded.
    india_eligible = has_india_signal and not (
        is_remote and remote_scope == RemoteScope.WORLDWIDE
    )

    if city:
        normalized = f"{city}, India"
    elif has_india_signal:
        normalized = "India"
    else:
        normalized = location_text.strip() or "Unknown"

    return LocationInfo(
        country="India" if has_india_signal else None,
        city=city,
        state=state,
        workplace_type=workplace,
        remote_scope=remote_scope,
        india_eligible=india_eligible,
        normalized_location=normalized,
    )
