from graph_builder import Graph, Zone, Connection
from typing import List


class Drone:
    def __init__(self, id: int, start: Zone) -> None:
        self.id: int = id
        self.position: Zone = start
        self.next_position: Zone = None
        self.path = []
        self.is_finish = False
    



class Simulation:
    def __init__(self, graph: Graph, shortest_path: List):
        self.drones = []
        self.graph = graph
    def set_path(self, paths: list[list[str]]):
        for i, v in enumerate(self.drones):
            v.path = paths[i % len(paths)]
    def create_drones(self) -> list[Drone]:
        nb_drones = self.graph.data["nb_drones"]
        drones = [Drone(i+1, self.graph.zones[0]) for i in range(nb_drones)]
        self.drones = drones
    def can_move(self, next_position, drone):
        # complete with condition if the drone can do to the next position
        # check zone type, connection capacity, zone capacity
        pass
    def move_drone(self, next_position, drone):
        next_position.drone_in_zone.append()
        drone.position = next_position
        self.path.pop(1)
        if next_position == end_zone:
            drone.is_finish = True
    def process_turns(self):
        for i in self.drone:
            if i.is_finish:
                continue
                
            next_position = self.path[1]
            can_move = self.can_move(self, next_position, i)
            if can_move:
                self.move_drone()


            
    def run_turns(self):
        self.create_drones()
        paths = [["s1", "z1"], ["s1", "z2"], ["s1", "z3"], ["s1", "z4"]]
        self.set_path(paths)
        # for i in self.drones:
        #     print("path of drone", i.id, i.path)
        while not all(i.is_finish for i in self.drones):
            self.process_turns()
