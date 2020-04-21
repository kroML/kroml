import pickle
from kroml.utils.logger import Logger
from kroml.utils.config_parser import ConfigParser

logger = Logger(__name__)

VAR_CON_FILE = 'variable_context.pickle'


@logger.for_all_methods(in_args=False,
                        skip_func=['set_object',
                                   'get_object',
                                   'save_context',
                                   'load_context',
                                   'set_module_status',
                                   'get_status'])
class VariableContext:
    """
    Variable context stores all the variables used in program execution to a dictionary schema.
    Variable can be an object of various type. It is stored under a specific string value to dictionary.
    """

    def __init__(self, config: ConfigParser):
        self.config = config
        self.object_dict = {}
        self.run_status_dict = {}

        # establishment of modules
        if self.config.get_attr("debug") and self.check_module_context():
            self.load_context()
            logger.info("Loading saved flow from variable context pickle file", created_by='system')
        else:
            for module in self.config.get_attr('modules'):
                if module.get('class_name') is not None:
                    self.run_status_dict[module.get('class_name')] = None
            logger.warning("Creating empty variable and status dictionary", created_by='system')

    def get_object(self, key: str) -> object:
        """
        Returns object from variable context stored under specific key.
        Returns None if key is not present in the variable context dictionary.

        :param str key: Value of specific key in dictionary
        :return object: Object stored in variable context
        """
        return self.object_dict.get(key, None)

    def set_object(self, key: str, obj: object, replace: bool = False) -> None:
        """
        Stores an object in variable context dictionary under specific key.

        :param object obj: Object to be stored in dictionary
        :param str key: Key being added to a dictionary
        :param bool replace: If set on true, new value will replace the previous one stored under the specific key.
        Default set on false.
        :return None: No return value

        """

        if obj is None:
            pass
        elif replace:
            self.object_dict[key] = obj
        else:
            if key not in self.object_dict:
                self.object_dict[key] = obj
            else:
                raise Exception("Trying setting on existing value! KEY=\"{}\"\n"
                                "Use parameter replace=True or call del_object(key) first.".format(key))

    def del_object(self, key: str) -> bool:
        """
        Deletes a key from dictionary with corresponding object.

        :param str key: Value of specific key in dictionary
        :return bool: Returns True if object was deleted from variable context dictionary.
                      Returns False if key was not present in dictionary and thus could not be deleted.
        """
        if key in self.object_dict:
            del self.object_dict[key]
            return True
        return False

    def save_context(self):
        """
        Saves object of variable context into a pickle file.

        :return None: No return value
        """
        filename = VAR_CON_FILE
        tmp_dict = {"status": self.run_status_dict, "variables": self.object_dict}
        with open(filename, 'wb') as outfile:
            pickle.dump(tmp_dict, outfile)

    def check_module_context(self):
        """
        Method for checking if pickle file structure is same as module_flow.
        :return bool
        """
        filename = VAR_CON_FILE
        with open(filename, 'rb') as infile:
            tmp_dict = pickle.load(infile)
            saved_run_status_dict = tmp_dict["status"]

        for module in self.config.get_attr("modules"):
            if module.get("class_name") not in saved_run_status_dict:
                return False
        return True

    def load_context(self):
        """
        Loads variable context from a pickle file into an object.

        :return None: No return value
        """
        filename = VAR_CON_FILE
        with open(filename, 'rb') as infile:
            tmp_dict = pickle.load(infile)
            self.object_dict = tmp_dict["variables"]
            self.run_status_dict = tmp_dict["status"]

    def set_status(self, obj: object) -> None:
        """
        Updates module execution dictionary.
        :return:
        """
        if obj is None:
            pass
        else:
            self.run_status_dict = obj

    def get_status(self):
        """
        Get module execution dictionary.
        :return:
        """
        return self.run_status_dict

    def set_module_status(self, module: str, value: bool):
        """
        :param module:
        :param value:
        :return:
        """
        if self.run_status_dict[module] is None:
            self.run_status_dict[module] = value
        else:
            print(self.run_status_dict[module])
            raise Exception("Trying to overwrite module status!")
