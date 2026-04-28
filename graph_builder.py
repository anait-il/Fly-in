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


class Graph:
    def __init__(self, data: Dict) -> None:
        self.data: dict = data
        self.graph: dict | None = None
        self.zones: List[Zone] = []

    def create_graph(self) -> None:
        data: Dict = self.data

        connections: list[Dict[str, int | str]] = data['connections']
        self.zone_map: Dict[str, Zone] = {zone.name: zone for zone in self.zones}

        graph = {}
        for zone in self.zones:
            graph[zone] = []

        for edge in connections:
            graph[self.zone_map[edge['left']]].append((self.zone_map[edge['right']], edge['max_capacity']))
            graph[self.zone_map[edge['right']]].append((self.zone_map[edge['left']], edge['max_capacity']))

        self.graph = graph

    def ceate_zones(self) -> None:
        for key, value in self.data['zones'].items():
            meta = value['meta']
            self.zones.append(Zone(key,
                                   value['type'],
                                   meta['zone'],
                                   meta['max_drones'],
                                   meta['color'],
                                   value['coordinate']))

    def get_zones(self) -> None:
        for zone in self.zones:
            print(zone.name, zone.coordinate, zone.color, zone.kind, zone.max_drones, zone.zone)
