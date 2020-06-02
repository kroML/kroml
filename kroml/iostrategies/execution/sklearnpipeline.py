from utils.logger import Logger
from iostrategies.execution.abstract_execution import Execution
from iostrategies.execution.abstract_execution import initialize_modules
from iostrategies.execution.abstract_execution import initialize_functions
from sklearn.pipeline import Pipeline


logger = Logger(__name__)


@logger.for_all_methods(in_args=True)
class sklearnpipeline(Execution):

    @initialize_modules
    @initialize_functions
    def initialize(self, modules, import_modules_list, func_name):
        self.func_name = func_name

        pipeline_list = []
        for module in self.init_modules:
            pipeline_list.append(tuple([module.__name__, module]))

        self.modules = Pipeline(pipeline_list)

    def execute(self):
        self.variables.set_object("output", getattr(self.modules, self.func_name)(self.variables.get_object("input")))

