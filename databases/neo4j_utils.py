from neo4j import GraphDatabase
from dotenv import load_dotenv
import neo4j
import os
import ast

load_dotenv()

URI = os.getenv('NEO4J_URL')
AUTH = os.getenv('NEO4J_AUTH')
AUTH = ast.literal_eval(AUTH)

class Neo4j():
    def __init__(self) -> None:
        self.driver = GraphDatabase.driver(URI, auth=AUTH)
        self.database = 'academicworld'
    
    def find_faculty_by_keyword(self, keyword=None):
        query = (
            "match (f:FACULTY)-[:PUBLISH]->(publication:PUBLICATION)-[r:LABEL_BY]->(key:KEYWORD) with f, r, publication, key "
            f"where key.name='{keyword}' "
            "return f.name as Faculty, sum(publication.numCitations*r.score) as Relevant "
            "order by Relevant desc "
            "limit 10"
        )
        # print(query)
        df = self.driver.execute_query(query, database_=self.database, result_transformer_=neo4j.Result.to_df)
        return df

    def find_faculty_by_keywords(self, keywords):
        # keywords_list = "[" + ", ".join(f"'{keyword}'" for keyword in keywords) + "]"
        query = (
            f"WITH {keywords} AS keywords "
            "MATCH (f:FACULTY)-[:PUBLISH]->(publication:PUBLICATION)-[r:LABEL_BY]->(key:KEYWORD) "
            "WHERE key.name IN keywords "
            "WITH f, SUM(publication.numCitations * r.score) AS relevanceScore, COUNT(DISTINCT key.name) AS matchedKeywords, keywords "
            "WHERE matchedKeywords = SIZE(keywords) "
            "RETURN f.name AS Faculty, relevanceScore as Relevant "
            "ORDER BY Relevant DESC "
            "LIMIT 10"
        )
        df = self.driver.execute_query(query, database_=self.database, result_transformer_=neo4j.Result.to_df)
        return df
        
