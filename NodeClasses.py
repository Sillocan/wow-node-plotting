from collections import namedtuple, defaultdict, Counter
from typing import List

MapNodeLocation = namedtuple('MapNodeLocation', ['name', 'x', 'y'])
Node = namedtuple('Node', ['name', 'id'])


class Map(object):

    def __init__(self, name):
        self.name = name
        self.node_set = set()

    def __str__(self):
        return "%s" % self.name

    def get_nodes(self) -> List[MapNodeLocation]:
        return list(self.node_set)

    def add_node(self, node_loc: MapNodeLocation):
        self.node_set.add(node_loc)

    def get_counts(self):
        data = dict(Counter(node.name for node in self.get_nodes()))
        data['Total'] = sum(count for count in data.values())
        return data

    def clear(self):
        self.node_set.clear()


