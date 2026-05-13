from typing import List
from graph_builder import Zone, Connection, Graph
from enum import Enum


class Color(Enum):
    RED = "\x1b[31m"
    BLUE = "\x1b[34m"
    RESET = "\x1b[0m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"


class Drone:
    def __init__(self, id: int):
        self.index: int = 0
        self.id: int = id
        self.path: List = []
        self.position: Zone | None = None
        self.connection: Connection | None = None
        self.is_finish: bool = False
        self.waiting: bool = False

    def __str__(self) -> None:
        return f"D{self.id}"

    def __repr__(self) -> None:
        return f"D{self.id}"


class Simulation:
    def __init__(self, graph: Graph, paths: List) -> None:
        self.graph: Graph = graph
        self.drones: List[Drone] = []
        self.paths: List = paths

    def set_paths(self):
        for i, drone in enumerate(self.drones):
            drone.path = self.paths[i % len(self.paths)]
            drone.position = self.graph.start
            drone.position.enter(drone)

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
                drone.position.leave(drone)
                print('drone in zone',drone,  next_position.drones_in_zone)
                drone.waiting = False
            else:
                drone.waiting = True
                next_position.enter(drone)
                drone.connection = connection
                connection.enter(drone)
                print(drone)
                drone.position.leave(drone)
                drone.position = None

    @staticmethod
    def drone_position(drone) -> str:
        return (drone.position
                if drone.position
                else f"<{drone.connection}>")

    @staticmethod
    def move_drone(drone, next_position: Zone, connection: Connection) -> None:
        drone.position.leave(drone)
        drone.position = next_position
        drone.position.enter(drone)
        connection.enter(drone)
        drone.connection = connection
        drone.index += 1

    def run_turns(self) -> None:
        result: str = ""

        for drone in self.drones:

            if drone.is_finish:
                continue

            next_position = drone.path[drone.index + 1]
            if next_position.zone == 'restricted' and drone.waiting:
                connection = drone.connection
            else:
                connection: Connection = self.graph.get_connection(drone.position,
                                                                   next_position)
                if next_position.is_full() or connection.is_full():
                    print(drone, connection, connection.drones_in_connection)
                    continue

            if next_position == self.graph.end:
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
            for zone in path:
                way += ' -> ' if way else ''
                way += f"{zone}"
            way = Color.YELLOW.value + way + Color.RESET.value
            print(f"path{i}: {way}")
        print()
        while not all((drone.is_finish for drone in self.drones)):
            count += 1
            print(self.run_turns(), end="\n\n")
        print(Color.GREEN.value + f"Total Turns: {count}" + Color.RESET.value)
