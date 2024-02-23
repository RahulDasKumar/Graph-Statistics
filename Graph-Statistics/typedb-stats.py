from typedb.client import *
from typedb_ml.networkx.query_graph import Query
from typedb_ml.typedb.thing import Thing
import networkx as nx
import matplotlib.pyplot as plt
query = """match
$mastery($n1,$n2) isa mastery;
$n1 isa Question;
$n2 isa Learning_Outcome;
$mastery2($n2,$x) isa mastery;
$x isa Learning_Concept;
"""


contains = """match 
$entity isa entity;
$pe ($entity, $y) isa contain;
"""
G = nx.MultiDiGraph()
N = nx.MultiDiGraph()
TypeDBGraph = nx.MultiDiGraph()
G.add_node('x')
G.add_node('s')
queryclass = [Query(G,query),Query(G,contains)]

def build_thing(typedb_thing):
    iid = typedb_thing.get_iid()
    type_label = typedb_thing.get_type().get_label().name()
    if typedb_thing.is_entity():
        base_type = "entity"
    elif typedb_thing.is_relation():
        base_type = "relation"
    elif typedb_thing.is_attribute():
        base_type = "attribute"
    else:
        raise RuntimeError("Unexpected Concept")

    if base_type == 'attribute':
        value_type = typedb_thing.get_type().get_value_type()
        assert value_type in Thing.VALUE_TYPES
        value = typedb_thing.get_value()

        return Thing(iid, type_label, base_type, value_type, value)

    return Thing(iid, type_label, base_type)


def concept_dict_from_concept_map(concept_map):
    return {variable: build_thing(typedb_concept) for variable, typedb_concept in concept_map.map().items()}


with TypeDB.core_client("localhost:1729") as client:
  with client.session("edu-graph-7",SessionType.DATA) as session:
      with session.transaction(TransactionType.READ) as tx:
          # combined_graph = build_graph_from_queries(queryclass, tx)
          for query in queryclass:
            concept_maps = tx.query().match(query.string)
            concept_dicts = [concept_dict_from_concept_map(concept_map) for concept_map in concept_maps]
            for concept_dict in concept_dicts:
              node1 = list(concept_dict.values())[0]
              node2 = list(concept_dict.values())[-1]
              TypeDBGraph.add_nodes_from([node1,node2])
              TypeDBGraph.add_edge(node1,node2)

def findingTriangles(nodes:list):
    closedTri = 0
    openTri = len(nodes) / 3
    hasThird = False
    for node in nodes:
        # print(node, "first node \n")
        firstPre = nx.MultiDiGraph.predecessors(TypeDBGraph,n=node)
        for secondNode in firstPre:
            # print(secondNode, 'predecessor\n')
            secondPre = nx.MultiDiGraph.predecessors(TypeDBGraph,n=secondNode)
            if secondPre != None:
              hasThird = True
              for triangle in secondPre:
                  # print(triangle,'triangle')
                  if triangle == node:
                    closedTri += 1
                  else:
                    openTri +=1 
    return (closedTri,openTri)


triangles = findingTriangles(TypeDBGraph.nodes)
print(triangles[0], " amount of closed triangles")
print(triangles[-1], " amount of open triangles")
print(nx.density(TypeDBGraph), " Density of TypeDB Graph")
print(len(list(TypeDBGraph.nodes)), " Number of Nodes")
print(len(list(TypeDBGraph.edges)), "Number of edges in a Graph")
print(len(list(TypeDBGraph.out_degree)), " amount of out degrees")
print(len(list(TypeDBGraph.in_degree)), " amount of in degrees")
print(len(list(nx.strongly_connected_components(G=TypeDBGraph)))/len(list(TypeDBGraph.nodes)), " fraction of nodes in a Strongly connected components")
print(len(list(nx.weakly_connected_components(G=TypeDBGraph)))/ len(list(TypeDBGraph.nodes)), " fraction of nodes in a weakly connected component")


