from abc import ABC, abstractmethod
from utils.logger import Logger

logger = Logger(__name__)


def initialize_modules(funct):
    def wrapper(*args, **kwargs):
        if "import_modules_list" in kwargs:
            import_module_list = kwargs["import_modules_list"]
        elif len(args) > 2:
            import_module_list = args[2]
        else:
            import_module_list = []

        if "modules" in kwargs:
            module_list = kwargs["modules"]
        elif len(args) > 1:
            module_list = args[1]
        else:
            module_list = []

        init_modules = []

        for ind, module in enumerate(import_module_list):
            concrete_module = getattr(module,
                                      module_list[ind].get('class_name'))(args[0].config, args[0].variables)
            init_modules.append(concrete_module)
        args[0].init_modules = init_modules

        res = funct(*args, **kwargs)
        return res

    return wrapper


def initialize_functions(funct):
    def wrapper(*args, **kwargs):
        if "func_name" in kwargs:
            function_name = kwargs["func_name"]

        elif len(args) > 2:
            function_name = args[3]
        else:
            function_name = None

        function_list = []

        if function_name:
            for module in args[0].init_modules:
                concrete_function = getattr(module, function_name)
                function_list.append(concrete_function)

        args[0].function_list = function_list

        res = funct(*args, **kwargs)

        return res

    return wrapper


@logger.for_all_methods(in_args=True)
class Execution(ABC):
    def __init__(self, config, variables, error_handling):
        self.config = config
        self.variables = variables
        self.error_handling = error_handling
        self.modules = []
        self.func_name = ""


    @abstractmethod
    def initialize(self, modules_list, func_name):
        pass

    @abstractmethod
    def execute(self):
        """
        Method for executing modules
        :return: None
        """
        pass
