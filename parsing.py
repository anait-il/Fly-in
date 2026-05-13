import re
from matplotlib.colors import CSS4_COLORS
from typing import Match


class ParserError(Exception):
    ...


class Parser:
    def __init__(self) -> None:
        self.lines: str | None = None
        self.data = {
            "nb_drones": None,
            "zones": {},
            "connections": []
        }
        self.line_count: int = 0
        self.start: int = 0
        self.end: int = 0
        self.zones: list = []

    @staticmethod
    def zone_meta_split(match: Match, line: str, nb_drones: int) -> dict:
        default_values = ("color", 'max_drones', 'zone')
        default_meta = ('normal', 'blocked', 'restricted', 'priority')
        data: dict = {}
        meta_dict: dict = {}

        meta = match.group("meta")
        if not meta:
            data = {
                'color': None,
                'zone': None,
                'max_drones': None
            }
        else:
            meta = meta.strip("[]").strip()
            meta = meta.lower()
            for item in meta.split():
                key, value = item.split('=', 1)
                if key in meta_dict:
                    raise ParserError(f"Duplicate metadata in line [{line}]")
                if key not in default_values:
                    print(key, value)
                    raise ParserError(f"invalid metadata [{item}]")
                meta_dict[key.lower()] = value.lower()

            data = {
                'color': meta_dict.get('color'),
                'zone': meta_dict.get('zone'),
                'max_drones': meta_dict.get('max_drones')
            }

        if not data['color']:
            data['color'] = 'none'
        if not data['zone']:
            data['zone'] = 'normal'
        else:
            if data['zone'] not in default_meta:
                raise ParserError(f'invalid metadata in line {line}')
        if not data['max_drones']:
            if match.group('type').lower() in ('end_hub', 'start_hub'):
                data['max_drones'] = nb_drones
            else:
                data['max_drones'] = 1
        else:
            try:
                data['max_drones'] = int(data['max_drones'])
                if data['max_drones'] <= 0:
                    raise ValueError()
            except ValueError:
                raise ParserError(f"Error in line [{line}]: max_drones must be positive-integer")
        if match.group('type').lower() == 'end_hub' or match.group('type').lower() == 'start_hub':
            if data['max_drones'] < nb_drones:
                raise ParserError("start zone / end zone can't handle all drones in nb_drones")
            if data['zone'] == 'blocked':
                raise ParserError("start/end zone can't be blocked")
        return data

    @staticmethod
    def con_meta_split(match: Match, line: str) -> str:
        meta_default = ["max_link_capacity"]

        meta = match.group("meta")
        if meta is None:
            meta = "max_link_capacity=1"
        else:
            meta = meta.strip("[]").strip()
            meta = meta.lower()
            if meta.split('=', 1)[0] not in meta_default:
                raise ParserError(f"invalid meta data in line [{line}]")
        value = meta.split("=", 1)[1]
        try:
            value = int(value)
            if value <= 0:
                raise ValueError()
        except ValueError:
            raise ParserError("value of max link capacity must be positive-integer")

        return meta

    def load_config(self, config_file: str) -> None:
        with open(config_file) as file:
            hubs: int = ("start_hub", "hub", "end_hub")
            self.nb_drones_count: int = 0

            for line in file:
                if line.startswith("#") or line.startswith("\n"):
                    continue
                self.line_count +=1
                if self.line_count == 1:
                    if not line.lower().startswith("nb_drones"):
                        raise ParserError("nb_drones must be the first line")

                for char in line:
                    if char == "#":
                        line = line.split("#")[0]
                        break
                line = line.strip()

                if line.lower().startswith("nb_drones"):
                    self.nb_drones_count += 1

                    pattern = r"\s*(\w+):\s*(-?\d+)$"
                    match = re.match(pattern, line)
                    if not match:
                        raise ParserError(f"format invalid in line [{line}]")
                    self.data["nb_drones"] = match.group(2)
                    self.validate_nb_drones()

                elif line.lower().startswith(hubs):
                    zone_pattern = (
                        r"^(?P<type>\w+)\s*:"
                        r"(?P<value>"
                            r"\s*(?P<name>\w+)\s+"
                            r"(?P<x>-?\d+)\s+"
                            r"(?P<y>-?\d+)\s*"
                            r"(?:\s+(?P<meta>\[\s*(?:\w+=-?\w+)(?:\s+\w+=-?\w+)*\]))?"
                        r")\s*$")

                    match = re.match(zone_pattern, line)
                    if not match:
                        raise ParserError(f"format invalid in line [{line}]")
                    self.data['zones'][match.group('name')] = {
                        'coordinate' : (match.group('x'), match.group("y")),
                        'type': match.group('type').lower(),
                        'meta': self.zone_meta_split(match, line, self.data['nb_drones'])}
                    if match.group("name") in self.zones:
                        raise ParserError(f"invalid name in line [{line}] (already used)")
                    self.zones.append(match.group('name'))
                    if match['type'] == 'end_hub':
                        self.end += 1
                    elif match['type'] == 'start_hub':
                        self.start += 1

                elif line.lower().startswith("connection"):
                    connection_pattern = (
                        r"(?P<type>\w+):"
                        r"(?P<value>\s*(?P<name1>\w+)-(?P<name2>\w+)\s*"
                        r"(?:\s+(?P<meta>\[\s*(\w+=-?\w+)(\s+\w+=-?\w+)*\s*\]))?)\s*$")

                    match = re.match(connection_pattern, line)
                    if not match:
                        raise ParserError(f"format invalid in line [{line}]")

                    self.data['connections'].append(
                        list(
                            (match.group("name1"),
                             match.group("name2"),
                             self.con_meta_split(match, line))))

                else:
                    raise ParserError(f"unknowen format in line [{line}]")
            if self.start == 0:
                raise ParserError("start point is missing")

            if self.start > 1:
                raise ParserError("multiple start zones, must be only one")

            if self.end == 0:
                raise ParserError("end point is missing")

            if self.end > 1:
                raise ParserError("multiple end zones, must be only one")

    def validate_nb_drones(self) -> None:
            value = self.data['nb_drones']

            if not value:
                raise ParserError("nb_drones is missing")
            if self.nb_drones_count > 1:
                raise ParserError("dublicate nb_drones line")

            try:
                value = int(value)
            except ValueError:
                raise ParserError("nb_drones must be a positive-integer")

            if value <= 0:
                raise ParserError("nb_drones must be > 0")

            self.data['nb_drones'] = value

    def validate(self) -> None:
        from pprint import pprint

        def validate_zones() -> None:
            data = self.data['zones']
            for zone, value in data.items():
                x, y = value['coordinate']
                x = int(x)
                y = int(y)
                value['coordinate'] = (x, y)
                meta = value['meta']
                color = meta['color']
                if not color.lower() in CSS4_COLORS and color.lower() != "rainbow":
                    if color == 'none':
                        pass
                    else:
                        raise ParserError(f"Invalid color {color}")
                max_drones = meta['max_drones']
                try:
                    max_drones = int(max_drones)
                except ValueError:
                    raise ParserError("max drones should be positive-integer")

        def validate_connections() -> None:
            data = self.data['connections']
            if not data:
                raise ParserError("No connections provided, You must provide a connections between zones")
            edges = []

            for edge in data:
                a, b, meta = edge
                if a not in self.zones:
                    raise ParserError(f"zone '{a}' in [connection: {a}-{b}] not found")
                if b not in self.zones:
                    raise ParserError(f"zone '{b}' in [connection: {a}-{b}] not found")
                if a == b:
                    raise ParserError(f"Invalid Connection (not allowed): {a}-{b}")
                if {'left': a, 'right': b, 'max_capacity': int(meta.split('=')[1])} in edges or {'left': b, 'right': a, 'max_capacity': int(meta.split('=')[1])} in edges:
                    raise ParserError(f"Duplicat connection between '{a}' and '{b}'")
                edges.append({
                    'left': a,
                    'right': b,
                    'max_capacity': int(meta.split('=')[1])
                })
            self.data['connections'] = edges

        validate_zones()
        validate_connections()
