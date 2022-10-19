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