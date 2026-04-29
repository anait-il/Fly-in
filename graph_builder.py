import parsing
from typing import List, Dict, Tuple


class Zone:
    def __init__(self, name: str, kind: str, zone: str, max_drones: int, color: str, coordinate: Tuple[int, int]) -> None:
        self.name: str = name
        self.kind: str = kind
        self.zone: str = zone
        self.max_drones: int = max_drones
        self.color: str = color
        self.coordinate: Tuple[int, int] = coordinate
    
    def __str__(self) -> str:
        return f"Zone({self.name})"
    
    def __repr__(self):
        return f"Zone({self.name})"


class Connection:
    def __init__(self, data: Dict[str, str | int]) -> None:
        self.zone_a: str = data['left']
        self.zone_b: str = data['right']
        self.max_capacity: int = data['max_capacity']
    
    def __repr__(self):
        return f"connection({self.zone_a}-{self.zone_b})"

    def get_neighboor(self, current: "Connection") -> "Connection":
        if current == self.zone_a:
            return self.zone_b
        return self.zone_a


class Graph:
    def __init__(self, data: Dict) -> None:
        self.data: dict = data
        self.graph: dict | None = None
        self.zones: List[Zone] = []
        self.connections: List[Connection] = []

    def create_graph(self) -> None:
        data: Dict = self.data

        connections: List[Connection] = self.connections
        self.zone_map: Dict[str, Zone] = {zone.name: zone for zone in self.zones}

        graph = {}
        for zone in self.zones:
            graph[zone] = []

        for edge in connections:
            graph[self.zone_map[edge.zone_a]].append(edge)
            graph[self.zone_map[edge.zone_b]].append(edge)

        self.graph = graph

    def create_zones(self) -> None:
        for key, value in self.data['zones'].items():
            meta = value['meta']
            self.zones.append(Zone(key,
                                   value['type'],
                                   meta['zone'],
                                   meta['max_drones'],
                                   meta['color'],
                                   value['coordinate']))

    def create_connection(self) -> None:
        for con in self.data['connections']:
            self.connections.append(Connection(con))

    def get_zones(self) -> None:
        for zone in self.zones:
            print(zone.name, zone.coordinate, zone.color, zone.kind, zone.max_drones, zone.zone)
    
    def create_zone_and_connection(self) -> None:
        self.create_zones()
        self.create_connection()
