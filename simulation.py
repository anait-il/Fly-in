from typing import List, cast
from graph_builder import Zone, Connection, Graph
from enum import Enum
from Dijkstra import Dijkstra


class Color(Enum):
    RED = "\x1b[31m"
    BLUE = "\x1b[34m"
    RESET = "\x1b[0m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"


class Path:
    """Represents a path consisting of zones for drones to follow."""

    def __init__(self, path: List[Zone]) -> None:
        """Initializes a path.

        Args:
            path: List of zones in order.
        """

        self.path: List[Zone] = path
        self.cost: int = 0
        self.throughput: int = 0
        self.drones_in_path: int = 0

    def add_drone(self) -> None:
        """Increments the number of drones assigned to this path."""

        self.drones_in_path += 1


class Drone:
    """Represents a drone moving through the graph."""

    def __init__(self, id: int):
        """Initializes a drone.

        Args:
            id: Unique drone identifier.
        """

        self.index: int = 0
        self.id: int = id
        self.path: Path | None = None
        self.position: Zone | None = None
        self.connection: Connection | None = None
        self.is_finish: bool = False
        self.waiting: bool = False
        self.ex: Zone | None = None

    def __str__(self) -> str:
        """Returns drone display string."""

        return f"D{self.id}"

    def __repr__(self) -> str:
        """Returns drone representation."""

        return f"D{self.id}"


class Simulation:
    """Runs the drone movement simulation over a graph."""

    def __init__(self, graph: Graph, dijkstra: Dijkstra) -> None:
        """Initializes the simulation.

        Args:
            graph: Graph structure of zones and connections.
            dijkstra: Precomputed paths and connections.
        """

        self.graph: Graph = graph
        self.drones: List[Drone] = []
        self.paths: List[Path] = self.path_factory(dijkstra.paths)
        self.connections_list: List[list[Connection]] = dijkstra.connections

    def path_factory(self, paths: List[List[Zone]]) -> List[Path]:
        """Creates Path objects from raw zone paths.

        Args:
            paths: List of zone sequences.

        Returns:
            List of Path objects.
        """

        return [Path(path) for path in paths]

    def path_capacity(self, path: Path,
                      connections: List[Connection]) -> int:
        """Computes maximum capacity of a path.

        Args:
            path: Path object.
            connections: Connections along the path.

        Returns:
            Maximum number of drones supported.
        """

        cost = min(zone.max_drones for zone in path.path)
        connection = min(connection.max_capacity for connection in connections)
        return min(cost, connection)

    def set_paths(self) -> None:
        """Assigns paths to drones and computes path costs."""

        for path, conn in zip(self.paths, self.connections_list):
            path.throughput = self.path_capacity(path, conn)
            path.cost = sum(zone.cost for zone in path.path)

        for drone in self.drones:
            min_path: Path = (
                min(self.paths,
                    key=lambda p: (p.cost + (p.drones_in_path/p.throughput))))
            drone.path = min_path
            drone.path.add_drone()
            drone.position = self.graph.start
            drone.position.enter(drone)

    def create_drones(self) -> None:
        """Creates all drones for the simulation."""

        drones = [Drone(i+1) for i in range(self.graph.data['nb_drones'])]
        self.drones = drones

    @staticmethod
    def move_to_restricted(drone: Drone,
                           next_position: Zone,
                           connection: Connection) -> None:
        """Handles movement into restricted zones.

        Args:
            drone: Moving drone.
            next_position: Target zone.
            connection: Connection used.
        """

        if drone.waiting:
            drone.position = next_position
            drone.index += 1
            drone.connection = None
            connection.leave(drone)
            if len(drone.position.drones_in_zone) == 1:
                drone.position.max_drones += 1
                drone.ex = drone.position
            drone.waiting = False
        else:
            drone.waiting = True
            next_position.enter(drone)
            drone.connection = connection
            connection.enter(drone)
            position: Zone = cast(Zone, drone.position)
            position.leave(drone)
            drone.position = None

    @staticmethod
    def drone_position(drone: Drone) -> Zone | str:
        """Returns readable drone position or connection."""

        return (drone.position
                if drone.position
                else f"<{drone.connection}>")

    @staticmethod
    def move_drone(drone: Drone,
                   next_position: Zone,
                   connection: Connection) -> None:
        """Moves a drone to the next zone.

        Args:
            drone: Moving drone.
            next_position: Target zone.
            connection: Connection used.
        """

        if drone.ex:
            drone.ex.max_drones -= 1
            drone.ex = None

        position: Zone = cast(Zone, drone.position)
        position.leave(drone)
        drone.position = next_position
        drone.position.enter(drone)
        connection.enter(drone)
        drone.connection = connection
        drone.index += 1

    def run_turn(self) -> str:
        """Executes a single simulation turn.

        Returns:
            String describing drone movements.
        """

        result: str = ""

        for drone in self.drones:

            if drone.is_finish:
                continue

            path: Path = cast(Path, drone.path)
            position: Zone = cast(Zone, drone.position)
            next_position = path.path[drone.index + 1]

            if next_position.zone == 'restricted' and drone.waiting:
                connection: Connection = cast(Connection, drone.connection)
            else:
                connection = self.graph.get_connection(position,
                                                       next_position)
                if next_position.is_full() or connection.is_full():
                    continue

            if next_position == self.graph.end:

                if next_position.zone == 'restricted':
                    if drone.waiting:
                        drone.is_finish = True
                    self.move_to_restricted(drone, next_position, connection)
                else:
                    drone.is_finish = True
                    self.move_drone(drone, next_position, connection)
                result += f"D{drone.id}-{self.drone_position(drone)} "

            else:

                if next_position.zone == 'restricted':
                    self.move_to_restricted(drone, next_position, connection)

                else:
                    self.move_drone(drone, next_position, connection)

                result += f"D{drone.id}-{self.drone_position(drone)} "

        for drone in self.drones:
            if drone.waiting:
                continue

            if drone.connection:
                drone.connection.leave(drone)
                drone.connection = None

        return result

    def execute(self) -> None:
        """Runs the full simulation until completion."""

        count: int = 0

        self.create_drones()
        self.set_paths()
        for i, path in enumerate(self.paths, start=1):
            way = ""
            for zone in path.path:
                way += ' -> ' if way else ''
                way += f"{zone}"
            way = Color.YELLOW.value + way + Color.RESET.value
            print(f"path{i}: {way}")
        print()
        while not all((drone.is_finish for drone in self.drones)):
            count += 1
            print(self.run_turn(), end="\n\n")
        print(Color.GREEN.value + f"Total Turns: {count}" + Color.RESET.value)
