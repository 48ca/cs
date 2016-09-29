EPSILON = 1.0 * 10**-15

class Node:
    def __init__(self,i):
        self.nodes = set()
        self.deg = 0
        self.id = i
    def add_node(self,n):
        if n not in self.nodes and n != self:
            self.nodes.add(n)
            self.deg += 1
    def add_nodes(self, ns):
        for n in ns:
            self.add_node(n)
    def __str__(self):
        return "<Node: {}>".format(self.id)
    def __repr__(self):
        return str(self)
