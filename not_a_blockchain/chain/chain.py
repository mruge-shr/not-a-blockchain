from uuid import uuid4

class Chain:
    def __init__(self):
        self.head = Block()

    def add_block(self, transactions):
        new_block = Block()
        new_block.transactions = [
            Transaction(*t) for t in transactions
        ]
        new_block.prev = self.head 
        self.head = new_block
    
    def print(self):
        block = self.head 
        while block:
            print(block)
            block = block.prev

    def get_metadata(self, id):
        for (k,v) in self.nodes:
            if k == id: return v 
        return {}
    
    def get_name(self, id):
        meta = self.get_metadata(id)
        return meta.get('name',id)

    @property
    def nodes(self):
        nodes = {}
        block = self.head
        while block:
            for t in block.transactions:
                if t.isGenesis and t not in nodes.keys():
                    nodes[t.a] = t.c
            block = block.prev
        return nodes.items()

    @property
    def transactions(self):
        transactions = []
        block = self.head
        while block:
            for t in block.transactions:
                if not t.isGenesis:
                    transactions += [t]
            block = block.prev   
        return transactions

    @property
    def actions(self):
        return {k:v for (k,v) in self.nodes if v.get('type',"").lower() == 'action'}

    @property
    def objects(self):
        return {k:v for (k,v) in self.nodes if v.get('type',"").lower() != 'action'}
    
    @property
    def relations(self):
        relations = []
        for t in self.transactions:
            relations += [(t.a,t.b,t.c)]
        return relations

    @property
    def graph(self):
        nodes = []
        edges = []
        block = self.head
        while block:
            for transaction in block.transactions:
                a = transaction.actor
                b = transaction.target
                r = transaction.action
                if a not in nodes: nodes += [a]
                if b not in nodes: nodes += [b]
                if (a,b,r) not in edges: edges += [(a,b,r)]
            block = block.prev
        return nodes,edges

class Block:
    def __init__(self):
        self.id = uuid4().hex
        self.prev = False
        self.transactions = []

    def __str__(self):
        return f"{self.id}, trans: {len(self.transactions)}"

class Transaction:
    def __init__(self, actor, target, action):
        self.actor  = actor
        self.target = target
        self.action = action

    @property
    def isGenesis(self): return self.actor == self.target 
    @property
    def a(self): return self.actor
    @property
    def b(self): return self.target
    @property
    def c(self): return self.action

class Action:
    def __init__(self):
        self.actions = dict(
            CREATED=uuid4().hex,
            USED=uuid4().hex,
            APPROVED=uuid4().hex
        )
