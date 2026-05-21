import re
import os
from matplotlib.colors import CSS4_COLORS
from typing import Match, Dict, Tuple


class ParserError(Exception):
    """Custom exception raised for parser-related errors."""
    ...


class Parser:
    """Parse and validate drone simulation configuration files.

    Attributes:
        lines (str | None):
            Raw file content.

        data (Dict):
            Parsed configuration data containing drones,
            zones, and connections.

        line_count (int):
            Number of processed lines.

        start (bool):
            Whether a start hub was declared.

        end (bool):
            Whether an end hub was declared.

        zones (list[str]):
            List of declared zone names.
    """

    def __init__(self) -> None:
        """Initialize parser state and configuration storage."""

        self.data: Dict = {
            "nb_drones": None,
            "zones": {},
            "connections": [],
            'line': None
        }
        self.line_count: int = 0
        self.start: bool = False
        self.end: bool = False
        self.zones: list = []

    @staticmethod
    def zone_meta_split(match: Match,
                        line: str,
                        nb_drones: int,
                        line_number: int) -> dict:
        """Parse and validate zone metadata.

        Args:
            match (Match):
                Regex match object containing parsed zone information.

            line (str):
                Original configuration line.

            nb_drones (int):
                Total number of drones declared in the configuration.

            line_number (int):
                Current line number in the configuration file.

        Returns:
            dict:
                Parsed metadata dictionary containing:
                    - color (str)
                    - zone (str)
                    - max_drones (int)

        Raises:
            ParserError:
                If metadata is invalid, duplicated, or contains
                unsupported values.
        """

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
                    raise ParserError(f"Duplicate metadata {key} at "
                                      f"line {line_number}: '{line}'")
                if key not in default_values:
                    raise ParserError(f"unknown metadata {key} at "
                                      f"line {line_number}: '{item}'")
                meta_dict[key] = value

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
                raise ParserError(f"unknown zone type "
                                  f"{data['zone']} at line {line_number}: "
                                  f"'{line}'")
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
                raise ParserError(f"expected positive-integer for "
                                  f"max_drones got '{data['max_drones']}' at "
                                  f"line {line_number}")
        is_end: bool = match.group('type') == 'end_hub'
        is_start: bool = match.group('type') == 'start_hub'
        if is_end or is_start:
            if data['max_drones'] < nb_drones:
                raise ParserError(f"invalid metadata at line {line_number}: "
                                  "start_zone/end_zone must handle all "
                                  "drones in nb_drones")
            if data['zone'] == 'blocked':
                raise ParserError(f"invalid metadata at line {line_number}: "
                                  "start/end zones can't be blocked")
        return data

    @staticmethod
    def con_meta_split(match: Match, line: str, line_number: int) -> str:
        """Parse and validate connection metadata.

        Args:
            match (Match):
                Regex match object containing parsed connection data.

            line (str):
                Original configuration line.

            line_number (int):
                Current line number in the configuration file.

        Returns:
            str:
                Validated connection metadata string.

        Raises:
            ParserError:
                If metadata format or values are invalid.
        """

        meta_default = ["max_link_capacity"]

        meta: str = match.group("meta")
        if meta is None:
            meta = "max_link_capacity=1"
        else:
            meta = meta.strip("[]").strip()
            meta = meta.lower()
            if meta.split('=', 1)[0] not in meta_default:
                raise ParserError("invalid meta data at line "
                                  f"{line_number}: '{line}'")
        value: int | str = meta.split("=", 1)[1]
        try:
            value = int(value)
            if value <= 0:
                raise ValueError()
        except ValueError:
            raise ParserError(f"expected positive_integer for "
                              f"max_link_capacity got '{value}' at "
                              f"line {line_number}")
        return meta

    def load_config(self, config_file: str | None) -> None:
        """Load and parse a drone simulation configuration file.

        Args:
            config_file (str | None):
                Path to the configuration file.

        Raises:
            ParserError:
                If the file is missing, empty, malformed,
                or contains invalid configuration data.
        """

        if not config_file:
            raise ParserError("no such file")
        if os.path.getsize(config_file) == 0:
            raise ParserError("empty file")

        with open(config_file) as file:
            hubs: Tuple[str, str, str] = ("start_hub", "hub", "end_hub")
            self.nb_drones_count: bool = False

            for i, line in enumerate(file, start=1):
                if line.startswith("#") or line.startswith("\n"):
                    continue

                self.line_count += 1
                if self.line_count == 1:
                    if not line.lower().strip().startswith("nb_drones"):
                        raise ParserError("missing required field in "
                                          f"line {i}: nb_drones must be "
                                          "the first line")

                for char in line:
                    if char == "#":
                        line = line.split("#")[0]
                        break
                line = line.strip()

                if line.lower().startswith("nb_drones"):
                    if self.nb_drones_count:
                        raise ParserError("dublicate field 'nb_drones' "
                                          f"at line {i}")

                    self.nb_drones_count = True

                    pattern = r"\s*(\w+)\s*:\s*([-+]?\d+)$"
                    match = re.match(pattern, line)
                    if not match:
                        raise ParserError("invalid line format at line "
                                          f"{i}: '{line}'")
                    self.data["nb_drones"] = match.group(2)
                    self.validate_nb_drones(i)

                elif line.lower().startswith(hubs):
                    zone_pattern = (
                        r"\s*(?P<type>\w+)\s*:"
                        r"(?P<value>"
                        r"\s*(?P<name>\w+)\s+"
                        r"(?P<x>[-+]?\d+)\s+"
                        r"(?P<y>[+-]?\d+)\s*"
                        r"(?:(?P<meta>\[(\s*(?:\w+=-?[^\s-]+)"
                        r"(?:\s+\w+=-?[^\s-]+)*\s*)?\]))?"
                        r")\s*$")

                    match = re.match(zone_pattern, line)
                    if not match:
                        raise ParserError(f"invalid line format at "
                                          f"line {i}: '{line}'")
                    self.data['zones'][match.group('name')] = {
                        'coordinate': (match.group('x'), match.group("y")),
                        'type': match.group('type').lower(),
                        'meta': self.zone_meta_split(match,
                                                     line,
                                                     self.data['nb_drones'],
                                                     i),
                        'line': i}
                    if match.group("name") in self.zones:
                        raise ParserError("duplicate name "
                                          f"'{match.group('name')}' "
                                          f"at line {i} (already used)")
                    self.zones.append(match.group('name'))
                    if match['type'] == 'end_hub':
                        if self.end:
                            raise ParserError(f"duplicate zone 'end_hub' at "
                                              f"line {i}: must be only one")
                        self.end = True
                    elif match['type'] == 'start_hub':
                        if self.start:
                            raise ParserError(f"duplicate zone 'start_hub' at "
                                              f"line {i}: must be only one")
                        self.start = True

                elif line.lower().startswith("connection"):
                    connection_pattern = (
                        r"\s*(?P<type>\w+)\s*:"
                        r"(?P<value>\s*(?P<name1>\w+)-(?P<name2>\w+)\s*"
                        r"(?:(?P<meta>\[(\s*(\w+=-?[^\s-]+)\s*)?\]))?)\s*$")

                    match = re.match(connection_pattern, line)
                    if not match:
                        raise ParserError(
                            f"invalid line format at line {i}: '{line}'")

                    self.data['connections'].append(
                        list(
                            (match.group("name1"),
                             match.group("name2"),
                             self.con_meta_split(match, line, i),
                             i)))

                else:
                    raise ParserError(f"unknowen format at line {i}: '{line}'")
            if not self.start:
                raise ParserError("missing required field: 'start_hub'")

            if not self.end:
                raise ParserError("missing required field: 'end_hub'")

    def validate_nb_drones(self, line: int) -> None:
        """Validate the number of drones declared in the configuration.

        Args:
            line (int):
                Line number containing the nb_drones field.

        Raises:
            ParserError:
                If nb_drones is not a positive integer.
        """

        value = self.data['nb_drones']
        try:
            value = int(value)
        except ValueError:
            raise ParserError(f"expected integer for 'nb_drones' but got "
                              f"'{line}' nb_drones must be a positive-integer")

        if value <= 0:
            raise ParserError(f"negative/zero value not allowed "
                              f"for 'nb_drones' at line {line}: "
                              f"nb_drones must be a positive-integer")

        self.data['nb_drones'] = value

    def validate(self) -> None:
        """Validate parsed zones and connections.

        This method validates:
            - Zone coordinates
            - Zone metadata
            - Connection integrity
            - Duplicate/self connections
            - Connection capacities

        Raises:
            ParserError:
                If any validation rule fails.
        """

        def validate_zones() -> None:
            """Validate all declared zones.

            Checks:
                - Coordinate validity
                - Color validity
                - max_drones type and value

            Raises:
                ParserError:
                    If zone data is invalid.
            """

            data = self.data['zones']
            for _, value in data.items():
                x, y = value['coordinate']
                x = int(x)
                y = int(y)
                value['coordinate'] = (x, y)
                meta = value['meta']
                color = meta['color'].lower()
                line = value['line']
                if color not in CSS4_COLORS and color != "rainbow":
                    if color == 'none':
                        pass
                    else:
                        raise ParserError(
                            f"unkown color '{color}' at line {line}")
                max_drones = meta['max_drones']
                try:
                    max_drones = int(max_drones)
                except ValueError:
                    raise ParserError(f"expected integer for 'max_drones' "
                                      f"but got '{max_drones}' at line {line}")

        def validate_connections() -> None:
            """Validate all declared connections.

            Checks:
                - Unknown zones
                - Self connections
                - Duplicate connections
                - Connection capacities

            Raises:
                ParserError:
                    If any connection is invalid.
            """

            data = self.data['connections']
            if not data:
                raise ParserError("No connections provided, "
                                  "You must provide a connections "
                                  "between zones")
            edges = []

            for edge in data:
                a, b, meta, line = edge
                if a not in self.zones:
                    raise ParserError(f"unknown zone '{a}' at line {line}: "
                                      f"'connection: {a}-{b}'")
                if b not in self.zones:
                    raise ParserError(f"unkown zone '{b}' at line {line}: "
                                      f"'connection: {a}-{b}'")
                if a == b:
                    raise ParserError(f"self connection not allowed for zone "
                                      f"{a} at line {line}")
                capacity = int(meta.split('=')[1])
                edge_ab = {'left': a, 'right': b, 'max_capacity': capacity}
                edge_ba = {'left': b, 'right': a, 'max_capacity': capacity}

                if edge_ab in edges or edge_ba in edges:
                    raise ParserError(f"Duplicat connection '{a}-{b}'"
                                      f"at line {line}")
                edges.append({
                    'left': a,
                    'right': b,
                    'max_capacity': int(meta.split('=')[1])
                })
            self.data['connections'] = edges

        validate_zones()
        validate_connections()
