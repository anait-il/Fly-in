from graph_builder import Graph, Zone, Connection
from typing import List, Dict, Tuple
import heapq
from itertools import count
import random


class Dijkstra:
    def __init__(self, graph: Graph) -> None:
        self.path = None
        self.graph: Dict[Zone, List[Connection]] = graph.graph
        self.ograph: Graph = graph
        self.map: Dict[str, Zone] = {zone.kind: zone for zone in self.graph}

    def shortest_path(self) -> None:
        start: Zone = self.map['start_hub']

        heap: List = [(0, 0, start)]
        heapq.heapify(heap)
        privous: Dict = {}
        unique: int = count()

        def get_neighbors(zone: Zone) -> None:
            neighbors: List = []
            for con in self.graph[zone]:
                other = con.get_other(zone)
                other = self.ograph.zone_map[other]
                if other.kind == 'blocked' or other.visited:
                    continue
                neighbors.append(other)
            return neighbors

        while heap:
            _, _, current = heapq.heappop(heap)
            current.visited = True
            neighbors: List = get_neighbors(current)
            for neighbor in neighbors:
                heapq.heappush(heap, ((neighbor.cost + current.cost),
                                      next(unique),
                                      neighbor))
                new_cost = neighbor.cost + current.cost
                if new_cost < (privous[neighbor].cost + neighbor.cost):
                    privous[neighbor] = current
        

            if current is self.map['end_hub']:
                break
        from pprint import pprint
        current = self.map['end_hub']
        self.path = []
        while current is not None:
            self.path.append(current)
            current = privous.get(current)
        self.path.reverse()
        pprint(f'the path is : {self.path}')                   
