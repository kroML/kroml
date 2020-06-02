import os
import sys
import json
from utils.logger import Logger

from utils.config_parser import ConfigParser
from utils.variable_context import VariableContext

from managers.input_manager import InputManager
from managers.module_manager import ModuleManager
from managers.output_manager import OutputManager

WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

logger = Logger(__name__)


class MainExecution:

    def __init__(self, config_json='{"main_config_file": "main_config.ini", "mode": "execute"}'):
        self.config = None
        self.variables = None
        self.set_input_params(config_json)

        self.input_manager = None
        self.module_manager = None
        self.output_manager = None

        self.initialize()

    def set_input_params(self, config_json):
        params_dict = json.loads(config_json)

        self.config = ConfigParser(main_config_file=params_dict.get('main_config_file'), mode=params_dict.get('mode'))

    def initialize(self):

        Logger.set_logger_settings(l_stream=sys.stdout, l_filename=self.config.get_attr('log_file'))

        self.variables = VariableContext(self.config)

        self.input_manager = InputManager(self.config, self.variables, self.config.get_attr("error_handler"))
        self.module_manager = ModuleManager(self.config, self.variables, self.config.get_attr("error_handler"))
        self.output_manager = OutputManager(self.config, self.variables, self.config.get_attr("error_handler"))

    def execute(self, run_json="{}"):

        self.config.update_config(run_json)

        self.variables = VariableContext(self.config)

        try:
            self.input_manager.execute()
            self.module_manager.execute()
            self.output_manager.execute()
        except Exception as e:
            raise e
        finally:
            self.variables.save_context()
            return self.variables.get_object('response')


if __name__ == '__main__':
    os.chdir(WORKING_DIRECTORY)

    main_exe = MainExecution()
    main_exe.execute()
