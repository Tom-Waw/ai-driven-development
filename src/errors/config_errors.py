class ConfigError(Exception):
    def __init__(self, message: str, config_name: str):
        self.message = message
        self.config_name = config_name

    def __str__(self):
        return f"Error in {self.config_name} config: {self.message}"
