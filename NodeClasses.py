from collections import namedtuple

MapNodeLocation = namedtuple('MapNodeLocation', ['name', 'x', 'y'])
Node = namedtuple('Node', ['name', 'id'])


class Map(object):

    def __init__(self, name):
        self.name = name
        self.node_location_list = []
        # self.node_map = []

    def __str__(self):
        return "%s" % self.name

    def add_node(self, map_node_location: MapNodeLocation):
        self.node_location_list.append(map_node_location)
