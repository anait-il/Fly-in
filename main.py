import sys
from parsing import Parser, ParserError
from pprint import pprint
from matplotlib.colors import CSS4_COLORS
from graph_builder import Graph
from Dijkstra import Dijkstra


if __name__ == "__main__":
    config = Parser()
    try:

        config.load_config("01_dead_end_trap.txt")
        config.validate()

        map = Graph(config.data)
        map.create_zone_and_connection()
        map.create_graph()
        algo = Dijkstra(map)
        algo.shortest_path()
    except ParserError as e:
        print("[Error]:", e)
    # except ValueError:
    #     print('why')
    except OSError as e:
        print(f"[File Error]: {e}")
