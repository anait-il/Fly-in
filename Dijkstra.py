from graph_builder import Graph, Zone, Connection
from parsing import ParserError
from typing import List, Dict
import heapq
from itertools import count


class Dijkstra:
    """
    Find shortest and alternative paths in a weighted graph.

    This class implements a modified version of the Dijkstra algorithm
    to compute the shortest path between a start hub and an end hub.

    The algorithm:
        - Avoids blocked zones.
        - Prioritizes zones marked as ``"priority"``.
        - Supports generating multiple alternative paths by increasing
          traversal costs after each discovered path.

    Attributes:
        path (List[Zone]):
            The latest shortest path found.

        graph (Dict[Zone, List[Connection]]):
            Adjacency representation of the graph.

        object_graph (Graph):
            Original graph object containing helper methods.

        map (Dict[str, Zone]):
            Mapping of zone kinds to their corresponding zone objects.

        paths (List[List[Zone]]):
            List of all discovered paths.
    """

    def __init__(self, graph: Graph) -> None:
        """
        Initialize the Dijkstra solver.

        Args:
            graph (Graph):
                Graph object containing zones and connections.
        """

        self.path: List[Zone] = []
        self.graph: Dict[Zone, List[Connection]] = graph.graph
        self.object_graph: Graph = graph
        self.map: Dict[str, Zone] = {zone.kind: zone for zone in self.graph}
        self.paths: List[List[Zone]] = []

    def shortest_path(self) -> None:
        """
        Compute the shortest path from start hub to end hub.

        Uses a priority queue (heap) to explore the graph while tracking
        the minimum known cost to each zone.

        Priority zones are explored before normal zones.

        Raises:
            ParserError:
                If no valid path exists between the start and end hubs.

        Side Effects:
            Updates:
                - ``self.path`` with the discovered shortest path.
        """

        start: Zone = self.map['start_hub']

        heap: List = [(0, 0, 0, start)]
        privous: Dict = {}
        unique: count[int] = count()
        costs = {zone: float("infinity") for zone in self.graph}
        costs[self.map['start_hub']] = 0

        def get_neighbors(zone: Zone) -> List[Zone]:
            """Return all reachable neighbors of a zone.

            Blocked zones are ignored.

            Args:
                zone (Zone):
                    Zone whose neighbors should be retrieved.

            Returns:
                List[Zone]:
                    Reachable neighboring zones.
            """

            neighbors: List = []
            for con in self.graph[zone]:
                other_name: str = con.get_other(zone)
                other: Zone = self.object_graph.zone_map[other_name]
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
            raise ParserError('No path exists to goal — '
                              'network is disconnected!')
        current = self.map['end_hub']
        while current is not None:
            self.path.append(current)
            current = privous.get(current)
        self.path.reverse()

    def get_connections_from_path(self,
                                  path: List[Zone],
                                  connections: List[List[Connection]]) -> None:
        """Convert a path of zones into graph connections.

        Args:
            path (List[Zone]):
                Ordered list of zones representing a path.

            connections (List[List[Connection]], optional):
                Existing collection of connection paths.
                Defaults to an empty list.

        Returns:
            List[List[Connection]]:
                Updated collection containing the extracted connections.
        """

        connection: List = []
        for i in range(len(path)-1):
            connection.append(self.object_graph.get_connection(path[i],
                                                               path[i+1]))
        connections.append(connection)

    def get_multi_paths(self) -> None:
        paths: List[List[Zone]] = []
        connections: List[List[Connection]] = []
        while True:
            self.shortest_path()
            if self.path in paths:
                break
            paths.append(self.path)
            self.get_connections_from_path(self.path, connections)
            for zone in self.path:
                zone.cost += 2
            self.path = []
        self.paths = paths
        self.connections = connections
