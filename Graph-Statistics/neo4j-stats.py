from neo4j import GraphDatabase
import networkx as nx
import matplotlib.pyplot as plt
import warnings
driver = GraphDatabase.driver('bolt://localhost:7687', auth=("neo4j", "password"))

query = """
MATCH (n)-[r]->(c) RETURN *
"""
session = driver.session(database="test4")
results = session.run(query)

G = nx.MultiDiGraph()

nodes = list(results.graph()._nodes.values())
for node in nodes:
    G.add_node(node.element_id, labels=node._labels, properties=node._properties)

rels = list(results.graph()._relationships.values())
for rel in rels:
    G.add_edge(rel.start_node.element_id, rel.end_node.element_id, key=rel.element_id, type=rel.type, properties=rel._properties)

# finding cluster coefficient 


# finding open and closed triangles
neo4jNodes = list(G.nodes)
def findingTriangles(nodes:list):
    print(nodes)
    closedTri = 0
    openTri = 0
    for node in nodes:
        firstPre = nx.MultiDiGraph.predecessors(G,n=node)
        for secondNode in firstPre:
            secondPre = nx.MultiDiGraph.predecessors(G,n=secondNode)
            for third in secondPre:
                triangle = nx.MultiDiGraph.predecessors(G,n=third)
                for triangle in secondPre:
                  # print(triangle,'triangle')
                  if triangle == node:
                    closedTri += 1
                  else:
                    openTri +=1
    return {'closedTriangles' :closedTri, 'openTriangles': openTri }


triangles = findingTriangles(neo4jNodes)
print(triangles['closedTriangles'], triangles['openTriangles'])
print("cluster coeffeicnt = ", 3*triangles["closedTriangles"]/triangles["openTriangles"])
print(nx.density(G), " Density of Neo4j Graph")
print(len(list(G.nodes)), " Number of Nodes")
print(len(list(G.edges)), "Number of edges in a Graph")
print(len(list(G.out_degree)), " amount of out degrees")
print(len(list(G.in_degree)), " amount of in degrees")
print(len(list(nx.strongly_connected_components(G=G)))/len(list(G.nodes)), " Strongly connected components")
print(len(list(nx.weakly_connected_components(G=G)))/ len(list(G.nodes)), " fraction of nodes in a weakly connected component")
