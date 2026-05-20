import os
from parsing import Parser, ParserError
from graph_builder import Graph
from Dijkstra import Dijkstra
from simulation import Simulation

if __name__ == "__main__":
    config = Parser()
    try:
        from matplotlib.colors import CSS4_COLORS
        #parsing part
        map_file = os.environ.get('MAP')
        config.load_config(map_file)
        config.validate()

        #create graph
        map = Graph(config.data)
        map.create_zone_and_connection()
        map.create_graph()

        #get the shortest path
        algo = Dijkstra(map)
        algo.get_multi_paths()

        sim = Simulation(map, algo)
        sim.execute()
    except ImportError:
        print('you must first install dependencies:')
        print('use:')
        print('     make install')

    except ParserError as e:
        print("[Error]:", e)

    except OSError as e:
        print(f"[File Error]: {e}")
