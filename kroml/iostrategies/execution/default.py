from utils.logger import Logger
from iostrategies.execution.abstract_execution import Execution
from iostrategies.execution.abstract_execution import initialize_modules
from iostrategies.execution.abstract_execution import initialize_functions


logger = Logger(__name__)


@logger.for_all_methods(in_args=True)
class default(Execution):

    @initialize_modules
    @initialize_functions
    def initialize(self, modules, import_modules_list, func_name):
        self.modules = modules
        self.func_name = func_name

    def execute(self):
        for ind, function in enumerate(self.function_list):
            try:
                function(self.modules[ind].get("params", {}))
                self.variables.set_module_status(self.modules[ind].get('class_name'), True)
            except Exception as e:
                self.variables.set_module_status(self.modules[ind].get('class_name'), False)
                if self.error_handling == 'skip':
                    logger.error(str(e), inp_class=self.modules[ind].get('class_name'),
                                 inp_func=self.func_name, created_by='system')
                    continue
                elif self.error_handling == 'exit':
                    logger.error(str(e), inp_class=self.modules[ind].get('class_name'),
                                 inp_func=self.func_name, created_by='system')
                    raise e
                else:
                    pass
