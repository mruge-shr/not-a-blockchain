from uuid import uuid4

class Node:
    def __init__(self):
        self.id=uuid4().hex

class User(Node):
    def __init__(self):
        super().__init__()

class Asset(Node):
    def __init__(self):
        super().__init__()

class Action(Node):
    def __init__(self):
        super().__init__()