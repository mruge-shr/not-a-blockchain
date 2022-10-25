from jinja2 import Template
from os.path import dirname, join
import yaml, json

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
    nodes = [{'data': {'id': n, 'label': chain.get_name(n)}} for n in nodes]
    edges = [{'data': {'source': e[0], 'target': e[1], 'label': chain.get_name(e[2])}} for e in edges]
    return nodes + edges

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
        func =  output_cytochain
    elif mode == 'cytograph':
        func = output_cytograph
    content = func(obj)
    if filename:
        with open(filename, 'w') as f:
            f.write(content)
    return content

def toYaml(chain):
    return yaml.dump(chain.toObj())

def toJson(chain):
    return json.dumps(chain.toObj())

def fromTxt(txt):
    from .chain import Chain, Transaction, Block
    obj = []
    try:
        obj = yaml.safe_load(txt)
    except Exception as e:
        try:
            obj = json.loads(txt)
        except Exception as e:
            pass
        pass
    if obj:
        newChain = Chain()
        for b in obj[::-1]:
            id = b.get('id', None)
            p = newChain.get_block(b.get('prev', False))
            ts = [Transaction(t['a'],t['b'],t['c']) for t in b.get('transactions', [])]
            newChain.add_block(block=Block(id=id, prev=p, transactions=ts))
        return newChain
    else:
        return Chain()
     