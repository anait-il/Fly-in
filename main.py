try:
    import os
    from parsing import Parser, ParserError
    from graph_builder import Graph
    from Dijkstra import Dijkstra
    from simulation import Simulation
except ImportError:
    print("""You must first install depencies.
Install it with:
            > make install
""")
    exit(1)

if __name__ == "__main__":
    config = Parser()
    try:

        # parsing part
        map_file = os.environ.get('MAP')
        config.load_config(map_file)
        config.validate()

        # create graph
        print(config.data['connections'])
        map = Graph(config.data)
        map.create_zone_and_connection()
        map.create_graph()

        # get the shortest path
        algo = Dijkstra(map)
        algo.get_multi_paths()

        sim = Simulation(map, algo)
        sim.execute()

    except ParserError as e:
        print("[Error]:", e)

    except OSError as e:
        print(f"[File Error]: {e}")
    
    except Exception as e:
        print(f"Error: {e}")
