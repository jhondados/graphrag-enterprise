"""GraphRAG pipeline with community detection."""
from neo4j import GraphDatabase
from langchain_google_vertexai import ChatVertexAI
from graspologic.partition import hierarchical_leiden
import networkx as nx

class GraphRAGPipeline:
    def __init__(self, neo4j_uri: str, project_id: str = ""):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=("neo4j", "password"))
        self.llm = ChatVertexAI(model_name="gemini-1.5-pro-002")
        self.graph = nx.Graph()

    def build_communities(self):
        """Leiden community detection for hierarchical graph partitioning."""
        partition = hierarchical_leiden(self.graph, max_cluster_size=10)
        return partition

    def global_search(self, query: str) -> str:
        """Map-reduce search across all community summaries."""
        communities = self.build_communities()
        # Map: query each community
        community_answers = [self.llm.invoke(f"Answer based on community {c}: {query}") for c in communities[:20]]
        # Reduce: synthesize final answer
        combined = "\n".join([a.content for a in community_answers])
        return self.llm.invoke(f"Synthesize these partial answers into one: {combined}").content
