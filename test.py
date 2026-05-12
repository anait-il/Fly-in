from typing import List
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
            drone.position.enter(drone)

    def create_drones(self) -> None:
        drones = [Drone(i+1) for i in range(self.graph.data['nb_drones'])]
        self.drones = drones

    def move_to_restricted(drone, next_position: Zone, connection: Connection) -> None:
            if drone.waiting:
                drone.position = next_position
                drone.index += 1
                drone.in_fly = None
                connection.leave(drone)
                drone.waiting = False
            else:
                drone.waiting = True
                next_position.enter(drone)
                drone.in_fly = connection
                connection.enter(drone)
                drone.position.leave(drone)
                drone.position = None

    @staticmethod
    def drone_position(drone) -> str:
        return (drone.position if drone.position else f"<{drone.in_fly}>")

    @staticmethod
    def move_drone(drone, next_position: Zone, connection: Connection) -> None:
        drone.position.leave(drone)
        drone.position = next_position
        drone.position.enter(drone)
        connection.enter(drone)
        drone.index += 1

    def run_turns(self) -> None:
        result: str = ""

        for drone in self.drones:

            if drone.is_finish:
                continue

            next_position = drone.path[drone.index + 1]
            # print()
            # print(f"inside turn: {drone}, {drone.index}, {drone.position}, {next_position}, {drone.path[drone.index]}")
            connection: Connection = self.graph.get_connection(drone.position,
                                         next_position)

            if next_position.is_full():
                continue

            if next_position == self.graph.end:
                drone.is_finish = True
                print('hellp')
                self.move_drone(drone, next_position, connection)
                result += f"D{drone.id}-{self.drone_position(drone)} "

            else:

                if next_position.zone == 'restricted':
                    drone.move_to_restricted(next_position, connection)

                else:
                    self.move_drone(drone, next_position, connection)

                result += f"D{drone.id}-{self.drone_position(drone)} "
        return result

    def execute(self) -> None:
        self.create_drones()
        self.set_paths()
        while not all((drone.is_finish for drone in self.drones)):
            print(self.run_turns())
            print()