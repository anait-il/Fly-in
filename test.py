from typing import List, Dict, Optional
from graph_builder import Zone, Connection, Graph


class Drone:
    def __init__(self, id: int):
        self.index: int = 0
        self.id: int = id
        self.path: List = []
        self.position: Zone | None = None
        self.in_fly: Connection | None = None
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

    def create_drones(self) -> None:
        drones = [Drone(i+1) for i in range(self.graph.data['nb_drones'])]
        self.drones = drones

    def move_to_restricted(self, next_position: Zone, connection: Connection) -> None:
            if self.waiting:
                self.position = next_position
                self.index += 1
                self.in_fly = None
                connection.leave(self)
                self.waiting = False
            else:
                self.waiting = True
                next_position.enter(self)
                self.in_fly = connection
                connection.enter(self)
                self.position.leave(self)
                self.position = None

    def position(self) -> str:
        return (self.position if self.position else self.in_fly)

    def move_drone(self, next_position: Zone, connection: Connection) -> None:
        self.position.leave(self)
        self.position = next_position
        next_position.enter(self)
        connection.enter(self)
        self.index += 1

    def run_turns(self) -> None:
        result: str = ""

        for drone in self.drones:

            if drone.is_finish:
                continue

            next_position = drone.path[drone.index + 1]
            connection: Connection = self.graph.get_connection(drone.position,
                                         next_position)

            if next_position.is_full() or connection.is_full():
                result += f"{drone.id}<{drone.position()}>"
                continue

            if next_position == self.graph.end:
                drone.is_finish = True
                result += f"{drone.id}<{drone.position()}>"
            else:
                if drone.position and drone.position != self.graph.start:
                    drone.position.drones_in_zone.remove(drone)

                if next_position.zone == 'restricted':
                    drone.move_to_restricted(next_position, connection)

                else:
                    self.move_drone(next_position, connection)
                    connection.drones_in_connection.append(drone)
                    drone.position = next_position
                    next_position.drones_in_zone.append(drone)
                    drone.index += 1
            print(drone, drone.position, end=" ")
        print()

    def execute(self) -> None:
        self.create_drones()
        self.set_paths()
        while not all((drone.is_finish for drone in self.drones)):
            self.run_turns()
