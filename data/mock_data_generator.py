import json
import os

def generate_mock_data(db):
    json_path = os.path.join(os.path.dirname(__file__), "mock_community.json")
    
    if not os.path.exists(json_path):
        print(f"Warning: {json_path} not found. Skipping mock generation.")
        return

    with open(json_path, "r") as f:
        data = json.load(f)

    for person in data.get("people", []):
        # 1. Upsert Person
        # Copy person data but exclude lists (skills, interests) for properties if needed, 
        # but Neo4j supports list properties. 
        # For graph purity, we separate skills into nodes, but keeping them as props is also fine.
        # We'll pass the whole dict to upsert_person as requested.
        db.upsert_person(person)

        # 2. Create Skill Relationships
        for skill in person.get("skills", []):
            db.upsert_skill(skill)
            db.create_relationship(person["id"], skill, "HAS_SKILL")

    print(f"✅ Mock data generated from {json_path}")
