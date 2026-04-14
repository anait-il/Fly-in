

class parser:
    def __init__(self) -> None:
        self.lines: str | None = None
        self.data = {
            "drones_nb": None,
            "zones": {},
            "connections": []
        }

    def load_config(self, config_file: str) -> None:
        with open(config_file) as file:
            lines = file.read()
        self.lines = lines
    
    def parsing(self) -> None:
        lines = self.lines
        for line in lines:

            type, values = line.split(":")

            if line.startswith("#"):
                continue

            elif line.startswith("nb_drones".lower()):
                self.data("nb_drones") = values
            
            elif type.startswith("start_hub".lower())