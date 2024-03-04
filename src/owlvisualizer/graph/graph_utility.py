from rdflib import Graph, RDF, OWL
from rdflib.term import URIRef, Literal, Node, BNode
from typing import Union

restriction_type = [OWL.hasValue, OWL.someValuesFrom, OWL.allValuesFrom]
collection_type = {OWL.intersectionOf: ('Intersection', 'owl:intersectionOf'), OWL.unionOf: ('Union', 'owl:unionOf')}


def uri_or_literal_2label(node: Union[URIRef, Literal, Node, str]) -> str:
    if isinstance(node, Literal) or isinstance(node, BNode):
        return str(node)
    else:
        if '#' in str(node):
            return str(node).split('#')[-1]
        else:
            return str(node).split('/')[-1]


def is_list(knowledge_graph: Graph, bnode: BNode):
    for _, _, c in knowledge_graph.triples((bnode, None, None)):
        for p in knowledge_graph.predicates(c):
            if p == RDF.first:
                return True
    return False


def is_restriction(knowledge_graph: Graph, bnode: BNode):
    matched_triple = list(knowledge_graph.triples((bnode, RDF.type, OWL.Restriction)))
    return len(matched_triple) > 0


def extract_collection_recursive(knowledge_graph: Graph, triple):
    _, p, el = triple
    if p == RDF.first:
        edge, node = None, None
        for _, p2, el2 in knowledge_graph.triples((el, None, None)):
            if p2 == OWL.onProperty:
                edge = el2
            if p2 in restriction_type:
                node = el2

        if isinstance(node, BNode) and is_restriction(node):
            return
        else:
            print("Return element")
            print(node, edge)
            return node, edge

    else:
        for list_rest_triple in knowledge_graph.triples((el, None, None)):
            return extract_collection_recursive(knowledge_graph=knowledge_graph, triple=list_rest_triple)


def get_collection_type(property):
    return collection_type.get(property)
