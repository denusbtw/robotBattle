import json


class GameConfig:
    def __init__(self,
                 difficulty: str,
                 config_path: str = 'config.json',
                 difficulties_path: str ='difficulties.json',
                 textures_path: str ='textures.json'):
        self.difficulty = difficulty
        self.config = {}
        self.difficulty_settings = {}
        self.textures = {}

        self._load_config(config_path)
        self._load_difficulties(difficulties_path)
        self._load_textures(textures_path)

        self._apply_difficulty()

    def _load_config(self, path: str) -> None:
        with open(path, 'r') as f:
            self.config = json.load(f)

    def _load_difficulties(self, path: str) -> None:
        with open(path, 'r') as f:
            all_difficulties = json.load(f)
        if self.difficulty in all_difficulties:
            self.difficulty_settings = all_difficulties[self.difficulty]
        else:
            raise ValueError(f"Difficulty '{self.difficulty}' not found in {path}")

    def _load_textures(self, path: str) -> None:
        with open(path, 'r') as f:
            self.textures = json.load(f)

    def _apply_difficulty(self) -> None:
        if "default" in self.textures and self.difficulty in self.textures["default"]:
            self.textures["default"] = self.textures["default"][self.difficulty]
        else:
            raise ValueError(f"Default textures for difficulty '{self.difficulty}' not found.")

    def get_grid_settings(self) -> dict:
        return self.config.get("grid", {})

    def get_gameplay_settings(self) -> dict:
        return self.config.get("gameplay", {})

    def get_color_settings(self) -> dict:
        return self.config.get("colors", {})

    def get_difficulty_settings(self) -> dict:
        return self.difficulty_settings

    def get_textures_settings(self) -> dict:
        return self.textures