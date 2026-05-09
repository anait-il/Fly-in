from typing import List, Dict, Optional
from graph_builder import Zone, Connection, Graph


class Drone:
    def __init__(self, id: int):
        self.id: int = id
        self.path: List = []
        self.position: Zone = self.path[0]
        self.is_finish: bool = False


class Simulation:
    def __init__(self, graph: Graph, paths: List) -> None:
        self.graph: Graph = graph
        self.drones: List[Drone] = []
        self.paths: List = paths

    def set_paths(self):
        for i, drone in enumerate(self.drones):
            drone.path = self.paths[i % len(self.paths)]

    def create_drones(self) -> None:
        drones = [Drone(i+1) for i in range(self.graph.data['nb_drones'])]
        self.drones = drones

    def run_turns(self) -> None:
        for drone in self.drones:
            if drone.is_finish:
                continue
            next_position = drone.path[1]
            if next_position.is_full():
                continue
            if self.graph.data[next_position].is_full():
                continue
            if next_position.zone == 'restricted':
                drone.position = self.graph.data[next_position]
            else:
                drone.position = next_position
                drone.path.pop(1)
            next_position.drone_in_zone.append(drone)
            self.graph.graph[next_position].drone_in_connection.append(drone)

    def execute(self) -> None:
        while not all(drone.is_finish for drone in self.drones):
            self.run_turns()
