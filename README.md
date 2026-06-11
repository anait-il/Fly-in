*This project has been created as part of the 42 curriculum by anait-il.

# Fly-in 🚁

## Description

**Fly-in** is a drone routing and simulation project. The goal is to move a fleet of drones from a start hub to an end hub through a network of interconnected zones, minimizing the total number of turns required for all drones to reach the destination.

The project involves three main stages:

- **Parsing** — reading and validating a custom configuration file format that describes the zone graph, connections, and constraints
- **Pathfinding** — finding optimal paths using Dijkstra's algorithm, with support for multiple paths to distribute drone load
- **Simulation** — simulating drone movement turn by turn, respecting zone capacity, link capacity, and restricted zone rules

Each zone has a type (`hub`, `restricted`, `priority`, `blocked`), a color, coordinates, and a maximum drone capacity. Connections between zones have a maximum link capacity. Drones must navigate the graph without exceeding any capacity constraint.

---

## Instructions

### Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
make install
```

This runs `uv sync` and installs all dependencies defined in `pyproject.toml`.

### Running

```bash
make run MAP=path/to/config.txt
```

If no `MAP` is provided, the default map is used:

```bash
make run
```

### Debug mode

```bash
make debug MAP=path/to/config.txt
```

Runs the simulation under Python's built-in debugger (`pdb`).

### Lint

```bash
make lint         # flake8 + mypy with strict flags
```

### Clean

```bash
make clean
```

Removes `__pycache__` and `.mypy_cache` directories.

---

## Algorithm Choices & Implementation Strategy

### Parsing

The config file is parsed line by line using **regular expressions**. Each line is matched against patterns for zone definitions, connection definitions, and metadata blocks. Errors are raised with descriptive messages including line numbers.

Parsed data is validated for:
- Required fields (`start_hub`, `end_hub`, `nb_drones`)
- Valid zone types and colors
- Connection references to existing zones
- Duplicate connections and self-connections

### Graph Construction

The graph is represented as an **adjacency list** where:
- Keys are `Zone` objects
- Values are lists of `Connection` objects

Each `Connection` stores references to both endpoint zone names and a `max_capacity` value. A `zone_map` dictionary maps zone names to `Zone` objects for O(1) lookup.

### Pathfinding — Dijkstra's Algorithm

Dijkstra's algorithm is used to find the shortest path(s) from `start_hub` to `end_hub`. The weight of each node is the **zone's turn cost** (number of turns a drone must spend in that zone).

Key implementation details:
- A **min-heap** (`heapq`) ensures the cheapest zone is always processed first
- A **`costs` dictionary** tracks the accumulated cost to reach each zone and prevents reprocessing with worse costs
- A **`previous` dictionary** records the optimal predecessor of each zone for path reconstruction
- A **unique counter** (`itertools.count`) resolves heap tie-breaking without comparing `Zone` objects directly
- Blocked zones are skipped during neighbor expansion

Multiple paths are computed by increasing the cost of zones in the privous route and re-running Dijkstra, providing alternative routes for drone distribution.

### Drone Distribution

Drones are distributed across available paths using a **greedy score formula**:

```
score = path_cost + (drones_assigned / path_capacity)
```

- `path_cost` penalizes longer paths
- `drones_assigned / path_capacity` penalizes congested paths

The drone is always assigned to the path with the **lowest score**, naturally balancing between path length and available capacity. Path capacity is defined as the minimum of all zone `max_drones` and connection `max_capacity` values along the path (the bottleneck).

### Simulation

The simulation runs turn by turn until all drones have reached the end hub:

- Each turn, every drone attempts to move to the next zone in its assigned path
- Movement is blocked if the next zone or connection is at full capacity
- **Restricted zones** require an extra turn: the drone flies toward the zone (enters the connection) on turn N, then enters the zone on turn N+1
- Zone and connection state is managed through `enter()` and `leave()` methods on each object
- The simulation outputs drone positions each turn using ANSI color codes

---

## Visual Representation

User chose a map from maps (you can download it from the project page)

#### example:
```
# Easy Level 1: Simple linear path
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

and the output will be like this:
```
path1: start -> waypoint1 -> waypoint2 -> goal

====Turn 1====

D1-waypoint1


====Turn 2====

D1-waypoint2
D2-waypoint1


====Turn 3====

D1-goal
D2-waypoint2


====Turn 4====

D2-goal


Total turns: 4
```

this representition includes zone colors and informations about chosing map, so the project verification made easy.

---

## Resources

### Dijkstra's Algorithm
- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Graph theory introduction — Khan Academy](https://www.khanacademy.org/computing/computer-science/algorithms/graph-representation/a/representing-graphs)
- [Python heapq documentation](https://docs.python.org/3/library/heapq.html)

### Python
- [Python re module](https://docs.python.org/3/library/re.html)
- [uv documentation](https://docs.astral.sh/uv/)

### AI Usage

**Claude (Anthropic)** was used throughout this project as a learning and debugging assistant:

- **Parsing** — guided regex pattern 
and helping to understand this module.
- **Dijkstra implementation** — explained the algorithm and the difference between BFS and Dijkstra, clarified the role of the `costs` dictionary and heap guarantee
- **Drone distribution** — discussed throughput formulas and tradeoffs between path length and capacity
- **Simulation** — helped design the state management via `enter()`/`leave()` methods
- **Tooling** — explained `uv`, Makefile structure, environment variables, ANSI color codes, mypy, and circular import resolution using `TYPE_CHECKING`

AI was used as a **teaching tool** — explaining concepts and guiding thinking — rather than generating complete solutions directly.
