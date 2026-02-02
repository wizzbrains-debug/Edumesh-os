from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class Person:
    id: str
    name: str
    role: str
    bio: Optional[str] = ""
    # We might store raw skills/needs strings here for simplicity or purely reliance on relationships

@dataclass
class Skill:
    name: str
    category: Optional[str] = "General"

@dataclass
class Need:
    name: str
    urgency: str # e.g. "HIGH", "MEDIUM", "LOW"

@dataclass
class Opportunity:
    name: str
    description: str
    required_skill: str

# Relationship Types
REL_HAS_SKILL = "HAS_SKILL"
REL_HAS_NEED = "HAS_NEED"
REL_MENTORS = "MENTORS" # Person -> Person
REL_CAN_FILL = "CAN_FILL" # Person -> Opportunity
