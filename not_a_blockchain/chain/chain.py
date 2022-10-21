from typing import Iterable
from uuid import uuid4

class Chain:
    def __init__(self,blank=False):
        if not blank:
            self.head = Block()
        else:
            self.head = False

    def toObj(self):
        block = self.head
        output = []
        while block:
            output += [block.toObj()]
            block = block.prev
        return output

    def get_block(self, id):
        block = self.head
        while block:
            if block.id == id:
                return block
            block = block.prev

    def add_block(self, block=None, transactions=[]):
        if isinstance(block, Block):
            new_block = block
        else:
            trans = []
            for t in transactions:
                if isinstance(t, Transaction):
                    trans += [t]
                else:
                    trans += [Transaction(*t)]
            new_block = Block(transactions=trans)
            new_block.prev = self.head
        self.head = new_block


    def get_metadata(self, id):
        return self.nodes.get(id, {})
    
    def get_id(self, v, k='name'):
        for id in self.nodes.keys():
            if self.nodes[id].get(k) == v:
                return id
        return None

    
    def get_name(self, id):
        meta = self.get_metadata(id)
        return meta.get('name',id)

    @property
    def nodes(self):
        nodes = {}
        for t in self.transactions:
            if t.isGenesis:
                if t.a not in nodes.keys(): nodes[t.a] = {}    
                nodes[t.a] |= t.c
        return nodes

    @property
    def transactions(self):
        ts = []
        block = self.head
        while block:
            for t in block.transactions:
                ts += [t]
            block = block.prev   
        return ts

    @property
    def actions(self):
        return {k:v for (k,v) in self.nodes.items() if v.get('type',"").lower() == 'action'}

    @property
    def objects(self):
        return {k:v for (k,v) in self.nodes.items() if v.get('type',"").lower() != 'action'}
    
    @property
    def relations(self):
        return [(t.a,t.b,t.c) for t in self.transactions if not t.isGenesis]

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
    def __init__(self, prev=False, id=None, transactions=[]):
        if id is None:
            id = uuid4().hex
        self.id = id
        self.prev = prev
        self.transactions = transactions

    def __str__(self):
        return f"{self.id}, trans: {len(self.transactions)}"

    def toObj(self):
        if self.prev:
            prev = self.prev.id 
        else:
            prev = False
        return dict(
            id=self.id,
            prev=prev,
            transactions=[
                t.toObj()
                for t in self.transactions]
        )
    

class Transaction:
    def __init__(self, actor, target, action):
        self.a = actor
        self.b = target
        self.c = action

    def toObj(self):
        return dict(
            a=self.a,
            b=self.b,
            c=self.c
        )

    @property
    def isGenesis(self): return self.a == self.b 
