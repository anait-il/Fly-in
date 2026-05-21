from __future__ import annotations
from typing import List, Dict, Tuple, TYPE_CHECKING, cast


if TYPE_CHECKING:
    from simulation import Drone


class Zone:
    """Represents a zone in the drone network."""

    def __init__(self,
                 name: str,
                 kind: str,
                 zone: str,
                 max_drones: int,
                 color: str,
                 coordinate: Tuple[int, int]) -> None:
        """Initializes a zone.

        Args:
            name: Zone name.
            kind: Zone category.
            zone: Zone type.
            max_drones: Maximum allowed drones.
            color: Display color.
            coordinate: Zone coordinates.
        """

        self.name: str = name
        self.kind: str = kind
        self.zone: str = zone
        self.max_drones: int = max_drones
        self.color: str = color
        self.coordinate: Tuple[int, int] = coordinate
        self.cost: int = self.set_cost(zone)
        self.visited: bool = False
        self.drones_in_zone: List[Drone] = []

    def is_full(self) -> bool:
        """Checks whether the zone is full."""

        return len(self.drones_in_zone) == self.max_drones

    def __str__(self) -> str:
        """Returns the zone name."""

        return f"{self.name}"

    def __repr__(self) -> str:
        """Returns the zone representation."""

        return f"{self.name}"

    def set_cost(self, zone_type: str) -> int:
        """Returns traversal cost for a zone type.

        Args:
            zone_type: Type of zone.

        Returns:
            Traversal cost.
        """

        if zone_type == "priority":
            return 0

        if zone_type == "restricted":
            return 2

        return 1

    def enter(self, drone: Drone) -> None:
        """Adds a drone to the zone.
        Args:
            drone: Drone entering the zone.
        """

        self.drones_in_zone.append(drone)

    def leave(self, drone: Drone) -> None:
        """Removes a drone from the zone.

        Args:
            drone: Drone leaving the zone.
        """

        self.drones_in_zone.remove(drone)


class Connection:
    """Represents a connection between two zones."""

    def __init__(self, data: Dict[str, str | int]) -> None:
        """Initializes a connection.

        Args:
            data: Connection metadata.
        """

        self.zone_a: str = cast(str, data['left'])
        self.zone_b: str = cast(str, data['right'])
        self.name: str = f"{self.zone_a}-{self.zone_b}"
        self.max_capacity: int = cast(int, data['max_capacity'])
        self.drones_in_connection: List[Drone] = []

    def enter(self, drone: Drone) -> None:
        """Adds a drone to the connection.

        Args:
            drone: Drone entering the connection.
        """

        self.drones_in_connection.append(drone)

    def leave(self, drone: Drone) -> None:
        """Removes a drone from the connection.

        Args:
            drone: Drone leaving the connection.
        """

        self.drones_in_connection.remove(drone)

    def is_full(self) -> bool:
        """Checks whether the connection is full."""

        return len(self.drones_in_connection) == self.max_capacity

    def __repr__(self) -> str:
        """Returns the connection representation."""

        return f"{self.zone_a}-{self.zone_b}"

    def get_other(self, current: Zone) -> str:
        """Returns the opposite zone name.

        Args:
            current: Current zone.

        Returns:
            Opposite zone name.
        """

        if current.name == self.zone_a:
            return self.zone_b
        return self.zone_a


class Graph:
    """Represents the drone navigation graph."""

    def __init__(self, data: Dict) -> None:
        """Initializes the graph.

        Args:
            data: Graph configuration data.
        """

        self.data: Dict = data
        self.zones: List[Zone] = []
        self.connections: List[Connection] = []

    def create_graph(self) -> None:
        """Builds the adjacency graph."""

        connections: List[Connection] = self.connections
        self.zone_map: Dict[str, Zone] = {zone.name: zone
                                          for zone in self.zones}

        graph: Dict[Zone, List[Connection]] = {}
        for zone in self.zones:
            graph[zone] = []

        for edge in connections:
            graph[self.zone_map[edge.zone_a]].append(edge)
            graph[self.zone_map[edge.zone_b]].append(edge)

        self.graph: Dict[Zone, List[Connection]] = graph

    def create_zones(self) -> None:
        """Creates graph zones."""

        for key, value in self.data['zones'].items():
            meta = value['meta']
            self.zones.append(Zone(key,
                                   value['type'],
                                   meta['zone'],
                                   meta['max_drones'],
                                   meta['color'],
                                   value['coordinate']))
        self.end: Zone = next(
            (zone for zone in self.zones if zone.kind == 'end_hub'))
        self.start: Zone = next(
            (zone for zone in self.zones if zone.kind == 'start_hub'))

    def create_connection(self) -> None:
        """Creates graph connections."""

        for con in self.data['connections']:
            self.connections.append(Connection(con))

    def create_zone_and_connection(self) -> None:
        """Creates zones and connections."""

        self.create_zones()
        self.create_connection()

    def get_connection(self, zone1: Zone, zone2: Zone) -> Connection:
        """Returns the connection between two zones.

        Args:
            zone1: First zone.
            zone2: Second zone.

        Returns:
            Matching connection.
        """

        return next((connection
                     for connection in self.connections
                     if connection.name == f"{zone1.name}-{zone2.name}"
                     or connection.name == f"{zone2.name}-{zone1.name}"))
