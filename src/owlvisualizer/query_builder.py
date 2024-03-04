from rdflib import Graph, URIRef, RDF, OWL, BNode
import rdflib.util
from src.owlvisualizer.graph import graph_utility

motion = "http://www.ease-crc.org/ont/mixing#WhirlstormMotion"
knowledge_graph = Graph()
knowledge_graph.parse("nutronGit/nutronGit/data/mixing.owl")


class QueryBuilder:
    def __init__(self, knowledge_graph: rdflib.Graph):
        self.kg = knowledge_graph
        self.triples = []
        self.sparql_query = "SELECT * WHERE { "

    def add_triple(self, triple: ()):
        self.triples.append(triple)

    def suggest_triples(self, triple: ()):
        if triple[0] is None:
            return self.kg.triples(triple)
        elif triple[0] is not None:
            return self.kg.predicate_objects(triple[0])

        for s, p, o in self.kg.triples(triple):
            print(s, p, o)

    def mock_suggestion(self):
        suggestions = list(self.kg.triples((URIRef(motion), None, None)))
        mocked_solution = []
        for s, p, o in suggestions:
            mocked_solution.append([str(s), str(p), str(o)])
        return mocked_solution
        # for s, p, o in self.kg.triples((URIRef(motion), None, None)):
        #     print(s, p, o)
        # for s2, p2, o2 in self.kg.triples((o, OWL.intersectionOf, None)):
        #     print(p2, o2)
        #     for s3, p3, o3 in self.kg.triples((o2, RDF.first, None)):
        #         print(s3, p3, o3)
        #         for s4, p4, o4 in self.kg.triples((o3, None, None)):
        #             print(s4, p4, o4)

    def mock_suggestion2(self):
        suggestions = list(self.kg.triples((URIRef(motion), None, None)))
        mocked_solution = {}
        for triple in suggestions:
            s, p, o = [str(s) for s in triple]
            if s not in mocked_solution:
                mocked_solution[s] = {}

            if p not in mocked_solution[s]:
                mocked_solution[s][p] = []

            mocked_solution[s][p].append(o)
        return mocked_solution

    def mock_suggestions3(self):
        suggestions = list(self.kg.triples((URIRef(motion), None, None)))
        mocked_solution = {}
        for s, p, o in suggestions:

            s_label = graph_utility.uri_or_literal_2label(node=s)
            p_label = graph_utility.uri_or_literal_2label(node=p)
            o_label = graph_utility.uri_or_literal_2label(node=o)

            if s not in mocked_solution:
                mocked_solution[s] = {s_label: {}}
                if isinstance(s, BNode) and graph_utility.is_list(self.kg, bnode=s):
                    print(f'Subject: {s}')

            if isinstance(o, BNode):
                for _, p2, o2 in self.kg.triples((o, None, None)):
                    t = graph_utility.get_collection_type(p2)
                    # mocked_solution[s][s_label][str(p2)][t[1]].append([o2, t[0]])
                # if graph_utility.is_list(self.kg, o):
                #     print(f'Object: {o}')
                #     for t2 in self.kg.triples((o, None, None)):
                #         for _, p2, o2 in self.kg.triples((t2[2], None, None)):
                #             print(p2, o2)
                #
                #             print(graph_utility.extract_collection_recursive(self.kg, (None, p2, o2)))
            else:
                if p not in mocked_solution[s][s_label]:
                    mocked_solution[s][s_label][p] = {p_label: []}

                mocked_solution[s][s_label][p][p_label].append([o, o_label])

        return mocked_solution


def get_query_builder():
    return QueryBuilder(knowledge_graph)


friends = [{'iri': 'http://bla#Alice', 'label': 'Alice'}, {'iri': 'http://bla#Bob', 'label': 'Bob'}]
hasFriendsRelation = {'iri': 'hasFriendRelation', 'label': 'hasFriend', 'objects': friends}
anotherFriend = {'iri': 'http://bla#Charlie', 'label': 'Charlie', 'predicate': [hasFriendsRelation]}
suggestions = {'subject': [anotherFriend]}
