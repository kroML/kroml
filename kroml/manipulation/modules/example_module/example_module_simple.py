from manipulation.modules.example_module.example_module import ExampleModule
from utils.logger import Logger
import time

logger = Logger(__name__)


@logger.for_all_methods(True)
class ExampleModuleSimple(ExampleModule):

    def execute(self, param: dict):
        #input_df = param['input_df']
        #df = self.variables.get_object(input_df)

        time.sleep(2)

        self.variables.set_object('a', None)

        time.sleep(2)

    def train(self, param: dict):
        pass
