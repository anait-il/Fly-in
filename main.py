import sys
from parsing import Parser, ParserError
from pprint import pprint
from matplotlib.colors import CSS4_COLORS
from graph_builder import Graph


if __name__ == "__main__":
    config = Parser()
    try:

        config.load_config("02_simple_fork.txt")
        config.validate()

        map = Graph(config.data)
        map.ceate_zones()
        map.create_graph()
        for a, b in map.graph.items():
            print(a, b)
    except ParserError as e:
        print("[Error]:", e)
    except OSError as e:
        print(f"[File Error]: {e}")
