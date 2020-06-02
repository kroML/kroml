from managers.manager import Manager
from utils.logger import Logger
import importlib
import os
import ast
import sys
import traceback

logger = Logger(__name__)


@logger.for_all_methods(in_args=False,
                        skip_func=['get_declaration_from_source',
                                   'recognize_module'])
class ModuleManager(Manager):
    """
    Inherits from Manager and it is responsible for handling process of all internal modules in modules folder and
    catching possible exceptions.
    """
    def __init__(self, config, variables, error_handling='exit'):
        super().__init__(config, variables, error_handling)

        self.execution_module = None

        self.modules_dict = self.config.get_attr('modules', default=[])

        if not self.modules_dict or not isinstance(self.modules_dict, list):
            logger.warning("Modules dictionary is empty")
            self.modules_dict = []

        self.initialized_modules = []
        self.initialize_modules()
        self.initialize()

    @staticmethod
    def get_declaration_from_source(text: str, obj_type: type = ast.ClassDef) -> list:
        """
        Function gets a single declaration from python source code.
        Checks if input text contains a class and if it does, appends it to output list.

        :param str text: Path, in which we are looking for classes.
        :param obj_type: Type of objects searched for in a file. <ast.ClassDef or ast.FunctionDef>
        :return list: List of all classes found in input path.
        """
        names = []

        tree = ast.parse(text)
        for node in tree.body:
            if isinstance(node, obj_type):
                names.append(node.name)
        return names

    @staticmethod
    def recognize_module(directory: str, obj_type: type = ast.ClassDef) -> dict:
        """
        Recognizes module to use by searching through modules directory and returning all .py files with their paths,
        opening them and looking for classes inside. Names of found modules are saved into dictionary alongside path to
        the file.

        :return dict: Dictionary with name of found module as the key and path to module as value.
        """
        files = []
        module_names_paths = {}
        # searching through modules directory and returning all .py files with their paths
        # r=root, d=directories, f = files
        for r, _, f in os.walk(directory):
            for file in f:
                parts = file.rpartition('.')
                if parts[1] == '.':
                    extension = parts[2]
                else:
                    extension = ''
                if extension == 'py':
                    files.append(os.path.join(r, file))

        # opens each file and finds classes inside them and saves them
        # into a dictionary with path to the file as key
        for file in files:
            try:
                with open(file, "r") as f:
                    module_names = ModuleManager.get_declaration_from_source(f.read(), obj_type)
            except Exception as e:
                module_names = []
                logger.warning(f"File \"{file}\" cannot be parsed for modules "
                               f"due to the error: {traceback.format_exc()}")

            if module_names:
                # if module_names is not empty
                file_modified = file.rpartition('.')[0].replace("./", "").replace(".\\", "")\
                                                       .replace("/", ".").replace("\\", ".")
                for module in module_names:
                    if module not in module_names_paths:
                        module_names_paths[module] = [file_modified]
                    else:
                        module_names_paths[module].append(file_modified)

        return module_names_paths

    def initialize_modules(self) -> None:
        module_names_paths = ModuleManager.recognize_module(self.config.get_attr('modules_directory'))
        for module in self.modules_dict:
            try:
                if not isinstance(module, dict):
                    error_message = f"Module \"{module}\" is not a valid dictionary input for module."
                    raise Exception(error_message)

                elif module.get('class_name'):
                    # if the path is present
                    if module.get('module_path'):
                        imported_module = importlib.import_module(module.get('module_path'))
                    else:
                        if not module_names_paths.get(module.get('class_name')):
                            error_message = f"Module \"{module.get('class_name')}\" was not found."

                            raise Exception(error_message)
                        elif len(module_names_paths[module.get('class_name')]) != 1:
                            error_message = f"More than one occurrence of module " \
                                            f"\"{module.get('class_name')}\" were found."
                            raise Exception(error_message)
                        else:
                            imported_module = importlib.import_module(module_names_paths
                                                                      [module.get('class_name')][0])

                    # append module to initialized list
                    if imported_module is not None:
                        self.initialized_modules.append(imported_module)
            except Exception as e:
                logger.error(str(e), created_by='system', inp_class='ModuleManager',
                             inp_func='initialize_modules')
                if self.error_handling == 'skip':
                    continue
                elif self.error_handling == 'exit':
                    raise e
                else:
                    raise e

    def initialize(self) -> None:

        execution_names_paths = ModuleManager.recognize_module(self.config.get_attr('executions_directory'))
        try:
            if self.config.get_attr('execution_mode') is not None:
                if not execution_names_paths.get(self.config.get_attr('execution_mode')):
                    import_execution = importlib.import_module(execution_names_paths['default'][0])
                    logger.warning("Execution mode not found! Using default execution.")
                else:
                    import_execution = importlib.import_module(
                        execution_names_paths[self.config.get_attr('execution_mode')][0])
            else:
                # use default execution
                import_execution = importlib.import_module(execution_names_paths['default'][0])
                logger.warning("Execution mode is NONE. Using default execution.")

            self.execution_module = getattr(import_execution,
                                            self.config.get_attr('execution_mode'))(self.config, self.variables,
                                                                                    self.error_handling)

            self.execution_module.initialize(self.modules_dict, self.initialized_modules, self.config.get_attr("run"))

        except Exception as e:
            logger.error(str(e), inp_func=self.config.get_attr("run"), created_by='system')
            raise e

    def execute(self) -> None:
        self.execution_module.execute()
