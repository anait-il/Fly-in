from typing import List
from graph_builder import Zone, Connection, Graph
from enum import Enum
import Dijkstra


class Color(Enum):
    RED = "\x1b[31m"
    BLUE = "\x1b[34m"
    RESET = "\x1b[0m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"

class Path:
    def __init__(self, path: List[Zone]) -> None:
        self.path: List[Zone] = path
        self.cost: int = 0
        self.drones_in_path: int = 0

    def add_drone(self) -> None:
        self.drones_in_path += 1


class Drone:
    def __init__(self, id: int):
        self.index: int = 0
        self.id: int = id
        self.path: List = []
        self.position: Zone | None = None
        self.connection: Connection | None = None
        self.is_finish: bool = False
        self.waiting: bool = False
        self.ex: Zone | None = None

    def __str__(self) -> None:
        return f"D{self.id}"

    def __repr__(self) -> None:
        return f"D{self.id}"


class Simulation:
    def __init__(self, graph: Graph, dijkstra: Dijkstra) -> None:
        self.graph: Graph = graph
        self.drones: List[Drone] = []
        self.paths: List[List[Zone]] = self.path_factory(dijkstra.paths)
        self.connections_list: List[list[Connection]] = dijkstra.connections

    def path_factory(self, paths: List[List[Zone]]) -> None:
        return [Path(path) for path in paths]

    def path_capacity(self, path: List[Zone], connections: List[Connection]) -> int:
        cost = min(zone.max_drones for zone in path.path)
        connection = min(connection.max_capacity for connection in connections)
        return min(cost, connection)

    def set_paths(self) -> None:

        for path, conn in zip(self.paths, self.connections_list):
            path.throughput = self.path_capacity(path, conn)
            path.cost = sum(zone.cost for zone in path.path)

        for drone in self.drones:
            drone.path = min(self.paths, key=lambda p: (p.cost + (p.drones_in_path / p.throughput)))
            drone.path.add_drone()
            drone.position = self.graph.start
            drone.position.enter(drone)

        # for i, drone in enumerate(self.drones):
        #     drone.path = self.paths[i % len(self.paths)]
        #     drone.position = self.graph.start
        #     drone.position.enter(drone)

    def create_drones(self) -> None:
        drones = [Drone(i+1) for i in range(self.graph.data['nb_drones'])]
        self.drones = drones

    @staticmethod
    def move_to_restricted(drone, next_position: Zone, connection: Connection) -> None:
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
                drone.position.leave(drone)
                drone.position = None

    @staticmethod
    def drone_position(drone) -> str:
        return (drone.position
                if drone.position
                else f"<{drone.connection}>")

    @staticmethod
    def move_drone(drone, next_position: Zone, connection: Connection) -> None:
        if drone.ex:
            drone.ex.max_drones -= 1
            drone.ex = None

        drone.position.leave(drone)
        drone.position = next_position
        drone.position.enter(drone)
        connection.enter(drone)
        drone.connection = connection
        drone.index += 1

    def run_turn(self) -> None:
        result: str = ""

        for drone in self.drones:

            if drone.is_finish:
                continue

            next_position = drone.path.path[drone.index + 1]
            if next_position.zone == 'restricted' and drone.waiting:
                connection = drone.connection
            else:
                connection: Connection = self.graph.get_connection(drone.position,
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

            if drone.connection and drone in drone.connection.drones_in_connection:
                drone.connection.leave(drone)

        return result

    def execute(self) -> None:
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
