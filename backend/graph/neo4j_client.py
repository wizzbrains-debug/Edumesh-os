import os
from typing import Dict, Any
from dotenv import load_dotenv
import networkx as nx
from neo4j import GraphDatabase

load_dotenv()


class Neo4jClient:
    def __init__(self):
        # Load environment variables with local fallbacks
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")

        self.driver = None
        self.use_mock = False

        # In-memory fallback graph (demo-safe)
        self.mock_graph = nx.DiGraph()

        try:
            self.driver = GraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
            )
            self.driver.verify_connectivity()
            print("✅ Connected to Neo4j successfully.")
        except Exception as e:
            print(
                f"⚠️ WARNING: Neo4j unavailable ({e}). "
                "Switching to IN-MEMORY MOCK mode."
            )
            self.use_mock = True

    def close(self):
        if self.driver:
            self.driver.close()

    # -----------------------------
    # Node Upserts
    # -----------------------------

    def upsert_person(self, person_data: Dict[str, Any]):
        if self.use_mock:
            self.mock_graph.add_node(
                person_data["id"],
                labels="Person",
                **person_data
            )
            return

        query = (
            "MERGE (p:Person {id: $id}) "
            "SET p += $props"
        )

        with self.driver.session() as session:
            session.run(
                query,
                id=person_data["id"],
                props=person_data
            )

    def upsert_skill(self, skill_name: str):
        if self.use_mock:
            self.mock_graph.add_node(
                skill_name,
                labels="Skill",
                name=skill_name
            )
            return

        query = "MERGE (s:Skill {name: $name})"

        with self.driver.session() as session:
            session.run(query, name=skill_name)

    def upsert_need(self, need_name: str):
        if self.use_mock:
            self.mock_graph.add_node(
                need_name,
                labels="Need",
                name=need_name
            )
            return

        query = "MERGE (n:Need {name: $name})"

        with self.driver.session() as session:
            session.run(query, name=need_name)

    # -----------------------------
    # Relationships
    # -----------------------------

    def create_relationship(
        self,
        from_id: str,
        to_id: str,
        rel_type: str,
        props: Dict[str, Any] | None = None
    ):
        if props is None:
            props = {}

        if self.use_mock:
            self.mock_graph.add_edge(
                from_id,
                to_id,
                type=rel_type,
                **props
            )
            return

        query = (
            "MATCH (a), (b) "
            "WHERE (a.id = $from_id OR a.name = $from_id) "
            "AND (b.id = $to_id OR b.name = $to_id) "
            f"MERGE (a)-[r:{rel_type}]->(b) "
            "SET r += $props"
        )

        with self.driver.session() as session:
            session.run(
                query,
                from_id=from_id,
                to_id=to_id,
                props=props
            )

    # -----------------------------
    # Fetching (for visualization)
    # -----------------------------

    def get_all_nodes(self):
        if self.use_mock:
            return list(self.mock_graph.nodes(data=True))

        query = "MATCH (n) RETURN n"

        with self.driver.session() as session:
            result = session.run(query)
            return [record["n"] for record in result]
