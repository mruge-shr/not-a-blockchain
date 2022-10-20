from jinja2 import Template
from os.path import dirname, join

def get_nodes_and_edges(chain):
    nodes = chain.objects.keys()
    edges = chain.relations
    return nodes, edges


def output_chain(chain):
    edges = []
    block = chain.head
    while block.prev:
        edges += [(block.id, block.prev.id)]
        block = block.prev
    template = join(dirname(__file__),'templates','chain.j2')
    with open(template) as template:
        return Template(template.read()).render(
            edges=edges
        )

def output_graph(chain):
    nodes, edges = get_nodes_and_edges(chain)
    template = join(dirname(__file__),'templates','graph.j2')
    with open(template) as template:
        return Template(template.read()).render(
            nodes=nodes,
            edges=edges
        )

def output_cytograph(chain):
    nodes, edges = get_nodes_and_edges(chain)
    elements = []
    for node in nodes:
        elements  += [{'data': {'id': node, 'label': chain.get_name(node)}}]
    for edge in edges:
        elements  += [{'data': {'source': edge[0], 'target': edge[1], 'label': chain.get_name(edge[2])}}]
    return elements

def output_cytochain(chain):
    done = []
    nodes = []
    edges = []
    block = chain.head
    while block:
        if block.id not in done:
            done += [block.id]
            nodes  += [{'data': {'id': block.id, 'label': block.id[:6]}}]
        if block.prev:
            edges += [{'data': {'source': block.id, 'target': block.prev.id}}]
        block = block.prev
    return nodes+edges

def output(obj, mode='chain', filename=None):
    if mode == 'chain':
        func = output_chain
    elif mode == 'graph':
        func = output_graph
    elif mode == 'cytochain':
        func = output_cytochain
    elif mode == 'cytograph':
        func = output_cytograph
    content = func(obj)
    if filename:
        with open(filename, 'w') as f:
            f.write(content)
    return content