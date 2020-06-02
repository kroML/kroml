import os
import json
import configparser


class ConfigParser:
    """
    Reads the config file and stores all the values in config object.
    """
    def __init__(self, main_config_file='main_config.ini', mode='execute'):

        self.config_ini = configparser.ConfigParser()

        self.config_ini.read(main_config_file)

        self.config_dir = self.config_ini[mode]['config_dir']

        self.log_file = self.config_ini['default']['log_dir'] + self.config_ini['default']['log_file']

        self.config_ini = configparser.ConfigParser()

        ini_files = []
        json_files = []

        for r, _, f in os.walk(self.config_dir):
            for file in f:
                parts = file.rpartition('.')
                if parts[1] == '.':
                    extension = parts[2]
                else:
                    extension = ''

                if extension == 'ini':
                    ini_files.append(r + file)
                elif extension == 'json':
                    json_files.append(r + file)
                else:
                    continue

        self.get_ini_attrs(ini_files)

        self.get_json_attrs(json_files)

    def set_attr(self, attribute_name, value, overwrite=False):
        """
        Method for loading attributes from config.json
        Sets attributes, and reaasigns values.
        """
        if attribute_name in dir(self) and not overwrite:
            raise Exception(f"Attribute \"{attribute_name}\" already exists, value was NOT overwritten")

        self.__setattr__(attribute_name, value)

    def get_attr(self, attribute_name, default=None):
        """
        Method for finding attributes
        """
        if attribute_name in dir(self) and self.__getattribute__(attribute_name) is not None:
            return self.__getattribute__(attribute_name)

        return default

    def get_ini_attrs(self, files_arr):

        for file in files_arr:
            self.config_ini.read(file)

        for section in self.config_ini:
            for attr in self.config_ini[section]:
                if section == 'bool':
                    self.set_attr(str(attr).lower(), self.config_ini.getboolean(section, attr))
                elif section == 'float':
                    self.set_attr(str(attr).lower(), self.config_ini.getfloat(section, attr))
                elif section == 'int':
                    self.set_attr(str(attr).lower(), self.config_ini.getint(section, attr))
                else:
                    self.set_attr(str(attr).lower(), self.config_ini[section][attr])

    def get_json_attrs(self, files_arr):

        for file_path in files_arr:
            with open(file_path, "r") as json_file:
                attr_dict = json.load(json_file)
                for key, value in attr_dict.items():
                    self.set_attr(key, value)

    def update_config(self, run_json: str):
        run_json_dict = json.loads(run_json)
        for key, value in run_json_dict.items():
            self.set_attr(key, value, overwrite=True)
