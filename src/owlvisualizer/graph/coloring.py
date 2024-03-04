from rdflib import OWL
def color_classes(graph: dict):
    nodes = [n for n in graph.get("nodes") if 'Task' in n.get("id")]
    for task in nodes:
        task.update({'color': {"background": "lime", "border": "black"}})

    nodes = [n for n in graph.get("nodes") if 'Motion' in n.get("id")]
    for motion in nodes:
        motion.update({'color': {"background": "orangered", "border": "black"}})
    nodes = [n for n in graph.get("nodes") if 'Motion' not in n.get("id") and 'Task' not in n.get("id")]
    for node in nodes:
        node.update({"color": "lightblue"})


def color_parameters(graph: dict):
    for edge in graph.get('edges'):
        relation = edge.get('label')
        if relation != 'subClassOf' and relation != 'owl:intersectionOf':
            child = edge.get("from")
            node = [n for n in graph.get("nodes") if n.get("id") == child][0]
            node.update({'color': {"background": "yellow", "border": "black"}})
