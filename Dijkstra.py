from graph_builder import Graph, Zone, Connection
from parsing import ParserError
from typing import List, Dict
import heapq
from itertools import count
from pprint import pprint


class Dijkstra:

    def __init__(self, graph: Graph) -> None:
        self.path: List[Zone] = []
        self.graph: Dict[Zone, List[Connection]] = graph.graph
        self.object_graph: Graph = graph
        self.map: Dict[str, Zone] = {zone.kind: zone for zone in self.graph}
        self.paths: List[List[Zone]] = []

    def shortest_path(self) -> None:
        start: Zone = self.map['start_hub']

        heap: List = [(0, 0, 0, start)]
        privous: Dict = {}
        unique: int = count()
        costs = {zone: float("infinity") for zone in self.graph}
        costs[self.map['start_hub']] = 0

        def get_neighbors(zone: Zone) -> None:
            neighbors: List = []
            for con in self.graph[zone]:
                other = con.get_other(zone)
                other = self.object_graph.zone_map[other]
                if other.zone == 'blocked':
                    continue
                neighbors.append(other)
            return neighbors

        while heap:
            _, _, _, current = heapq.heappop(heap)
            neighbors: List = get_neighbors(current)
            for neighbor in neighbors:
                priority = 0 if neighbor.zone == "priority" else 1
                new_cost = neighbor.cost + costs[current]
                if new_cost < costs[neighbor]:
                    heapq.heappush(heap, (priority, new_cost,
                                        next(unique),
                                        neighbor))
                    privous[neighbor] = current
                    costs[neighbor] = new_cost

            if current == self.map['end_hub']:
                break

        if self.map['end_hub'] not in privous:
            raise ParserError('No path exists to goal — network is disconnected!')
        current = self.map['end_hub']
        while current is not None:
            self.path.append(current)
            current = privous.get(current)
        self.path.reverse()

    def get_connections_from_path(path, connections=[]) -> None:
        connection: List = []
        for i in range(len(path)-1):
            connection.append(object_graph.get_connection(path[i], path[i+1]))
        connections.append(connection)
        return connections

    def get_multi_paths(self) -> None:
        paths: List = []
        connections = []
        while True:
            self.shortest_path()
            if self.path in paths:
                break
            paths.append(self.path)
            connections = self.get_connections_from_path(self.path)
            for zone in self.path:
                zone.cost += 2
            self.path = []
        self.paths = paths
        self.connections = connections
