from managers.manager import Manager
from utils.logger import Logger
from iostrategies.input_db.db_loader_pd import DBLoader
from iostrategies.io_strategy_pd import IOStrategy

logger = Logger(__name__)


@logger.for_all_methods(in_args=False, skip_func=['get_input_files', 'get_input_db'])
class InputManager(Manager):
    """
    Inherits from Manager and it is responsible for opening and reading input files and their saving into
    dataframes inside of variable objects alongside with handling exceptions that could appear during process.
    """
    def execute(self) -> None:
        """
        This function reads names of input files, which are about to be processed. Based on the extension of file,
        function recognize a file type and initialize corresponding Loader class. Then it calls load() function
        of picked Loader, which reads data from this file and writes them inside given Dataframe.
        If the extension is not recognized as any of the Excel, CSV or Pickle file, function writes a warning in logger.

        :return None: No return value.
        """
        # Load data from files and choose dataframe - pandas(default), spark or text
        self.input_strategy = IOStrategy(self.config, self.variables)

        self.get_input_files()
        self.get_input_db()

    def get_input_files(self):
        """
        Method for loading input from files if input attribute exists in config.json
        """
        if self.config.get_attr('input_files') is None:
            logger.info("No files input found", created_by='system')
            return None

        for input_file in self.config.get_attr('input_files', default=[]):
            if input_file.get("run") == self.config.get_attr("run") or input_file.get("run") == "all":
                if not self.config.get_attr("debug") or \
                   input_file.get('variable_name') not in self.variables.object_dict:

                    if input_file.get('input_type') == 'spark':
                        pass
                    elif input_file.get('input_type') == 'text':
                        pass
                    elif input_file.get('input_type') == 'pandas':
                        try:
                            self.input_strategy.load(input_file)
                        except Exception as e:
                            logger.error(str(e), created_by='system')
                            if self.error_handling == 'skip':
                                continue
                            elif self.error_handling == 'exit':
                                raise e
                            else:
                                raise e
                    else:
                        pass
                else:
                    logger.info(input_file.get("file_name") + " was skiped because it was loaded from pickle file.",
                                created_by='system')
            else:
                logger.info(input_file.get("file_name") + " was skipped due to its 'run' attribute.",
                            created_by='system')

    def get_input_db(self):
        """
        Method for loading input from DataBase if input attribute exists in config.json
        """

        if self.config.get_attr('input_db') is None:
            logger.info("No database input found", created_by='system')
            return None

        for input_database in self.config.get_attr('input_db', default=[]):
            if input_database.get("run") == self.config.get_attr("run") or input_database.get("run") == "all":
                if input_database.get('input_type') == 'spark':
                    pass
                elif input_database.get('input_type') == 'text':
                    pass
                else:
                    try:
                        db_loader = DBLoader(config=self.config, variables=self.variables)
                        db_loader.load(input_database)
                    except Exception as e:
                        error_message = str(e)
                        logger.error(error_message, created_by='system')
                        if self.error_handling == 'skip':
                            continue
                        elif self.error_handling == 'exit':
                            self.variables.save_context()
                            raise e
                        else:
                            raise e
            else:
                logger.info(str(input_database.get("db_name")) + " was skipped due to its 'run' attribute.",
                            created_by='system')
