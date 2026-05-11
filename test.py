from typing import List, Dict, Optional
from graph_builder import Zone, Connection, Graph


class Drone:
    def __init__(self, id: int):
        self.id: int = id
        self.path: List = []
        self.position: Zone | None = None
        self.in_fly: Connection | None = None
        self.is_finish: bool = False
        self.waiting: bool = False
    
    def __str__(self) -> None:
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

    def move_to_restricted(self, drone: Drone, nect) -> None:
            if drone.waiting:
                drone.position = next_position
                drone.path.pop(1)
                drone.in_fly = None
                drone.waiting = False
            else:
                drone.waiting = True
                next_position.drone_in_zone.append(drone)
                drone.in_fly = self.graph.get_connection(drone.position,
                                                            next_position)
                drone.position = None

    def run_turns(self) -> None:
        for drone in self.drones:

            if drone.is_finish:
                continue
            print(drone.path)
            next_position = drone.path[1]
            if next_position.is_full():
                continue
            print(drone, drone.position, next_position)
            if self.graph.get_connection(drone.position,
                                         next_position).is_full():
                continue
            if next_position == self.graph.end:
                drone.is_finish = True
                continue

            if drone.position and drone.position != self.graph.start:
                drone.position.drones_in_zone.remove(drone)

            if next_position.zone == 'restricted':
                if drone.waiting:
                    drone.position = next_position
                    drone.path.pop(1)
                    drone.in_fly = None
                    drone.waiting = False
                else:
                    drone.waiting = True
                    next_position.drone_in_zone.append(drone)
                    drone.in_fly = self.graph.get_connection(drone.position,
                                                               next_position)
                    drone.position = None
                    continue
            else:
                self.graph.get_connection(drone.position, next_position).drones_in_connection.append(drone)
                drone.position = next_position
                next_position.drones_in_zone.append(drone)
                drone.path.pop(1)
            # print(drone, drone.position)

    def execute(self) -> None:
        self.create_drones()
        self.set_paths()
        self.run_turns()
        while not all(drone.is_finish for drone in self.drones):
            self.run_turns()
