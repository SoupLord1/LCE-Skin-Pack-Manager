import configparser, os

class ConfigManager():
    valid_dlc_path = False
    parent_path = ""
    
    def __init__(self):
        if (not os.path.exists("config.ini")):
            self.create_config()
        else:
            self.read_config()
            if (not self.parent_path == ""):
                self.valid_dlc_path = True


    def create_config(self):
            self.config = configparser.ConfigParser()
            # Add sections and key-value pairs
            self.config['Config'] = {
                'parent_path': self.parent_path,
            }
            # Write the configuration to a file
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)

    def read_config(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.parent_path = self.config.get("Config", "parent_path")

