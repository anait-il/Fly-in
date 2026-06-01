"""
Fly-in Pygame Visualizer
Plugs directly into your existing Simulation, Graph, Dijkstra classes.
Usage: python3 visualizer.py <config_file>
"""

from __future__ import annotations

import sys
import math
import pygame  # type: ignore[import]

from typing import Dict, List, Tuple, Optional, cast
from parsing import Parser
from graph_builder import Zone, Connection, Graph
from Dijkstra import Dijkstra
from simulation import Simulation, Drone, Path


# ── CONSTANTS ─────────────────────────────────────────────────────────────────

W, H      = 1280, 780
FPS       = 60
LERP      = 0.12
NODE_R    = 18
MARGIN    = 80

BG     = (8,  13, 24)
GRID_C = (18, 26, 44)
TEXT_C = (170, 220, 210)
DIM_C  = (55,  75,  95)
WHITE  = (255, 255, 255)

COLOR_MAP: Dict[str, Tuple[int, int, int]] = {
    'green':   (0,   210, 100),
    'red':     (220,  40,  60),
    'blue':    (40,  120, 220),
    'yellow':  (230, 200,  30),
    'purple':  (160,  50, 220),
    'orange':  (230, 130,  20),
    'cyan':    (0,   200, 210),
    'white':   (220, 220, 220),
    'black':   (50,   50,  50),
    'brown':   (140,  80,  30),
    'maroon':  (120,  25,  25),
    'gold':    (210, 175,  20),
    'violet':  (140,  80, 210),
    'crimson': (200,  20,  60),
    'darkred': (120,  10,  10),
    'rainbow': (200, 200, 255),
    'gray':    (120, 120, 120),
    'pink':    (220, 100, 140),
}

DRONE_COLORS: List[Tuple[int, int, int]] = [
    (255,  80,  80), (80,  200, 255), (80,  255, 130),
    (255, 200,  50), (200,  80, 255), (255, 140,  40),
    (40,  220, 200), (255,  80, 180), (120, 255,  80),
    (180, 130, 255),
]


# ── SCREEN POSITIONS ──────────────────────────────────────────────────────────

_sx: Dict[str, float] = {}
_sy: Dict[str, float] = {}


def screen_pos(zone: Zone) -> Tuple[float, float]:
    return _sx[zone.name], _sy[zone.name]


def compute_layout(zones: Dict[str, Zone], sw: int, sh: int) -> None:
    if not zones:
        return
    xs   = [z.x for z in zones.values()]
    ys   = [z.y for z in zones.values()]
    minx = min(xs); maxx = max(xs)
    miny = min(ys); maxy = max(ys)
    rw   = maxx - minx or 1
    rh   = maxy - miny or 1
    for z in zones.values():
        _sx[z.name] = MARGIN + (z.x - minx) / rw * (sw - 2 * MARGIN)
        _sy[z.name] = (sh - MARGIN) - (z.y - miny) / rh * (sh - 2 * MARGIN)


# ── DRONE SMOOTH POSITIONS ────────────────────────────────────────────────────

_dpx: Dict[int, float] = {}
_dpy: Dict[int, float] = {}


def drone_target(drone: Drone, graph: Graph) -> Tuple[float, float]:
    if drone.position is not None:
        return screen_pos(drone.position)
    if drone.connection is not None:
        conn = drone.connection
        za   = graph.zone_map.get(conn.zone_a)
        zb   = graph.zone_map.get(conn.zone_b)
        if za and zb:
            ax, ay = screen_pos(za)
            bx, by = screen_pos(zb)
            return (ax + bx) / 2, (ay + by) / 2
    return screen_pos(graph.start)


# ── HELPERS ───────────────────────────────────────────────────────────────────

def zone_color(zone: Zone) -> Tuple[int, int, int]:
    return COLOR_MAP.get(zone.color, (100, 100, 120))


def drone_color(drone: Drone) -> Tuple[int, int, int]:
    return DRONE_COLORS[(drone.id - 1) % len(DRONE_COLORS)]


def find_hovered(graph: Graph, mx: int, my: int) -> Optional[str]:
    for zone in graph.graph.keys():
        sx, sy = screen_pos(zone)
        if math.hypot(mx - sx, my - sy) < NODE_R + 6:
            return zone.name
    return None


# ── DRAW FUNCTIONS ────────────────────────────────────────────────────────────

def draw_grid(surf: pygame.Surface) -> None:
    sw, sh = surf.get_size()
    for x in range(0, sw, 40):
        pygame.draw.line(surf, GRID_C, (x, 0), (x, sh))
    for y in range(0, sh, 40):
        pygame.draw.line(surf, GRID_C, (0, y), (sw, y))


def draw_paths(surf: pygame.Surface, sim: Simulation) -> None:
    path_cols = [
        (0, 200, 255, 60), (255, 180, 0, 60),
        (0, 255, 130, 60), (255, 80, 200, 60),
    ]
    for i, path in enumerate(sim.paths):
        col = path_cols[i % len(path_cols)]
        zones = path.path
        for j in range(len(zones) - 1):
            ax, ay = screen_pos(zones[j])
            bx, by = screen_pos(zones[j + 1])
            pygame.draw.line(surf, col[:3],
                             (int(ax), int(ay)),
                             (int(bx), int(by)), 3)


def draw_connections(surf: pygame.Surface,
                     graph: Graph,
                     font_sm: pygame.font.Font) -> None:
    seen = set()
    for zone, conns in graph.graph.items():
        for conn in conns:
            key = tuple(sorted([conn.zone_a, conn.zone_b]))
            if key in seen:
                continue
            seen.add(key)

            za = graph.zone_map.get(conn.zone_a)
            zb = graph.zone_map.get(conn.zone_b)
            if not za or not zb:
                continue

            occupied = len(conn.drones_in_connection)
            cap      = conn.max_capacity
            ratio    = occupied / cap if cap > 0 else 0
            r = int(60  + ratio * 180)
            g = int(120 - ratio * 80)
            b = int(200 - ratio * 140)
            width = 1 + int(ratio * 3)

            ax, ay = screen_pos(za)
            bx, by = screen_pos(zb)
            pygame.draw.line(surf, (r, g, b),
                             (int(ax), int(ay)),
                             (int(bx), int(by)), width)

            mx = int((ax + bx) / 2)
            my = int((ay + by) / 2)
            cap_s = font_sm.render(f"{occupied}/{cap}", True, (80, 120, 150))
            surf.blit(cap_s, (mx - cap_s.get_width() // 2,
                              my - cap_s.get_height() // 2))


def draw_zones(surf: pygame.Surface,
               graph: Graph,
               font_sm: pygame.font.Font,
               hovered: Optional[str]) -> None:
    for zone in graph.graph.keys():
        sx, sy   = screen_pos(zone)
        isx, isy = int(sx), int(sy)
        base     = zone_color(zone)
        occupied = len(zone.drones_in_zone)
        max_d    = zone.max_drones
        full     = occupied >= max_d
        is_hov   = hovered == zone.name
        radius   = NODE_R + (4 if is_hov else 0)

        # glow
        gc   = NODE_R * 3
        glow = pygame.Surface((gc * 2, gc * 2), pygame.SRCALPHA)
        for gr in range(NODE_R * 2, 4, -4):
            alpha = int(22 * (1 - gr / (NODE_R * 2)))
            pygame.draw.circle(glow, (*base, alpha), (gc, gc), gr)
        surf.blit(glow, (isx - gc, isy - gc))

        # fill + border
        fill = (50, 20, 20) if full else (18, 24, 40)
        pygame.draw.circle(surf, fill,   (isx, isy), radius)
        pygame.draw.circle(surf,
                           WHITE if is_hov else base,
                           (isx, isy), radius, 2)

        # occupancy arc
        if 0 < max_d < 9999:
            angle = 2 * math.pi * occupied / max_d
            if angle > 0.01:
                arc_r   = pygame.Rect(isx - radius - 4,
                                      isy - radius - 4,
                                      (radius + 4) * 2,
                                      (radius + 4) * 2)
                arc_col = (255, 60, 60) if full else (60, 210, 120)
                pygame.draw.arc(surf, arc_col, arc_r,
                                math.pi / 2,
                                math.pi / 2 + angle, )

        # name label below
        lbl = font_sm.render(zone.name, True, base)
        surf.blit(lbl, (isx - lbl.get_width() // 2,
                        isy + radius + 3))

        # occupancy inside
        cap_str = f"{occupied}/{'inf' if max_d >= 9999 else max_d}"
        cap_s   = font_sm.render(cap_str, True, WHITE)
        surf.blit(cap_s, (isx - cap_s.get_width() // 2,
                          isy - cap_s.get_height() // 2))


def draw_drones(surf: pygame.Surface,
                drones: List[Drone],
                font_sm: pygame.font.Font) -> None:
    for drone in drones:
        if drone.is_finish:
            continue
        x, y  = int(_dpx[drone.id]), int(_dpy[drone.id])
        color = drone_color(drone)
        pygame.draw.circle(surf, color, (x, y), 8)
        pygame.draw.circle(surf, WHITE, (x, y), 8, 1)
        lbl = font_sm.render(f"D{drone.id}", True, WHITE)
        surf.blit(lbl, (x - lbl.get_width() // 2,
                        y - lbl.get_height() // 2 - 16))


def draw_hud(surf: pygame.Surface,
             font: pygame.font.Font,
             font_sm: pygame.font.Font,
             turn: int,
             sim: Simulation,
             paused: bool,
             speed: int,
             log: str) -> None:
    sw, sh  = surf.get_size()
    nb      = len(sim.drones)
    done    = sum(1 for d in sim.drones if d.is_finish)

    bar = pygame.Surface((sw, 46), pygame.SRCALPHA)
    bar.fill((8, 13, 24, 210))
    surf.blit(bar, (0, 0))

    items = [
        (f"TURN  {turn}",        (0,  210, 170), 16),
        (f"DRONES  {done}/{nb}", (160, 200, 255), 190),
        ("PAUSED" if paused else "RUNNING",
         (220, 180, 40) if paused else (60, 220, 120), 370),
        (f"SPEED  {speed}x",    (150, 150, 200), 560),
    ]
    for text, color, x in items:
        s = font.render(text, True, color)
        surf.blit(s, (x, 14))

    ctrl = font_sm.render(
        "SPACE=pause  UP/DOWN=speed  R=restart  Q=quit",
        True, DIM_C)
    surf.blit(ctrl, (sw - ctrl.get_width() - 12, 16))

    log_bar = pygame.Surface((sw, 28), pygame.SRCALPHA)
    log_bar.fill((5, 10, 20, 190))
    surf.blit(log_bar, (0, sh - 28))
    log_s = font_sm.render(log[:140], True, (100, 170, 150))
    surf.blit(log_s, (10, sh - 22))


def draw_tooltip(surf: pygame.Surface,
                 zone: Zone,
                 font_sm: pygame.font.Font) -> None:
    max_d = zone.max_drones
    lines = [
        zone.name,
        f"type : {zone.kind}",
        f"zone : {zone.zone}",
        f"color: {zone.color}",
        f"max  : {'inf' if max_d >= 9999 else max_d}",
        f"here : {len(zone.drones_in_zone)} drones",
        f"coord: ({zone.x}, {zone.y})",
    ]
    pad = 10
    lh  = 18
    bw  = max(font_sm.size(l)[0] for l in lines) + pad * 2
    bh  = len(lines) * lh + pad * 2
    mx, my = pygame.mouse.get_pos()
    sw, sh = surf.get_size()
    bx = min(mx + 14, sw - bw - 4)
    by = min(my - 10, sh - bh - 4)

    box = pygame.Surface((bw, bh), pygame.SRCALPHA)
    box.fill((8, 18, 32, 225))
    pygame.draw.rect(box, (0, 190, 160), (0, 0, bw, bh), 1)
    surf.blit(box, (bx, by))

    for i, line in enumerate(lines):
        color = (0, 215, 175) if i == 0 else TEXT_C
        s = font_sm.render(line, True, color)
        surf.blit(s, (bx + pad, by + pad + i * lh))


# ── SETUP ─────────────────────────────────────────────────────────────────────

def setup(filepath: str) -> Tuple[Simulation, Graph]:
    parser = Parser()
    parser.load_config(filepath)
    parser.validate()

    graph = Graph(parser.data)
    graph.create_zone_and_connection()
    graph.create_graph()

    dijkstra = Dijkstra(graph)
    dijkstra.find_paths()

    sim = Simulation(graph, dijkstra)
    sim.create_drones()
    sim.set_paths()

    return sim, graph


def init_drone_positions(sim: Simulation, graph: Graph) -> None:
    sx, sy = screen_pos(graph.start)
    for drone in sim.drones:
        _dpx[drone.id] = sx
        _dpy[drone.id] = sy


# ── MAIN ──────────────────────────────────────────────────────────────────────

class Visualizer:
    def __init__(self, sim: Simulation, graph: Graph) -> None:
        self.sim   = sim
        self.graph = graph
        # state variables
        self.turn      = 0
        self.paused    = True
        self.speed     = 1
        self.last_step = 0.0
        self.log       = "Press SPACE to start"
        self.hovered: Optional[str] = None

    def run(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
        pygame.display.set_caption("Fly-in Visualizer")
        clock   = pygame.time.Clock()  # clock is separate!
        font    = pygame.font.SysFont("monospace", 15, bold=True)
        font_sm = pygame.font.SysFont("monospace", 11)

        compute_layout(self.graph.zone_map, W, H)
        init_drone_positions(self.sim, self.graph)

        running = True
        while running:
            clock.tick(FPS)
            now = pygame.time.get_ticks() / 1000.0

            # events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE):
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_UP:
                        self.speed = min(self.speed + 1, 10)
                    elif event.key == pygame.K_DOWN:
                        self.speed = max(self.speed - 1, 1)
                elif event.type == pygame.VIDEORESIZE:
                    compute_layout(self.graph.zone_map,
                                   event.w, event.h)

            # hover
            mx, my       = pygame.mouse.get_pos()
            self.hovered = find_hovered(self.graph, mx, my)

            # simulation step
            all_done = all(d.is_finish for d in self.sim.drones)
            if not self.paused and not all_done:
                if now - self.last_step >= 1.0 / self.speed:
                    self.last_step = now
                    self.turn += 1
                    self.log = (f"Turn {self.turn}: "
                                + self.sim.run_turn().replace('\n', '  '))

            if all_done and not self.paused:
                self.paused = True
                self.log    = f"All drones arrived in {self.turn} turns!"

            # lerp
            lf = LERP * (1 + self.speed * 0.4)
            for drone in self.sim.drones:
                tx, ty = drone_target(drone, self.graph)
                _dpx[drone.id] += (tx - _dpx[drone.id]) * lf
                _dpy[drone.id] += (ty - _dpy[drone.id]) * lf

            # draw
            screen.fill(BG)
            draw_grid(screen)
            draw_paths(screen, self.sim)
            draw_connections(screen, self.graph, font_sm)
            draw_zones(screen, self.graph, font_sm, self.hovered)
            draw_drones(screen, self.sim.drones, font_sm)
            draw_hud(screen, font, font_sm,
                     self.turn, self.sim,
                     self.paused, self.speed, self.log)

            if self.hovered:
                zone = self.graph.zone_map.get(self.hovered)
                if zone:
                    draw_tooltip(screen, zone, font_sm)

            pygame.display.flip()

        pygame.quit()
