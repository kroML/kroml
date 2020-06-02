from managers.manager import Manager
from utils.logger import Logger
from iostrategies.output_db.db_writer_pd import DBWriter
from iostrategies.io_strategy_pd import IOStrategy

logger = Logger(__name__)


@logger.for_all_methods(in_args=False,
                        skip_func=['save_to_files',
                                   'save_to_db'])
class OutputManager(Manager):
    """
    Inherits from Manager and it is responsible for writing into output files from dataframes and handling eventual
    exceptions.
    """

    def execute(self) -> None:
        """
        This function reads names of files from config.json, which are about to be created. Based on the extension of
        file, function recognize a file type and initialize corresponding Writer class. Then it calls write() function
        of picked Writer, which create a new file and fill it up with data from given Dataframe.
        If the extension is not recognized as any of the Excel, CSV or Pickle file, function writes a warning in logger.
        """
        # Save data to the file
        self.save_to_files()

        # Save data to databases
        self.save_to_db()

    def save_to_files(self):
        """
        Method for saving data into data files.
        """
        if self.config.get_attr('output_files') is None:
            logger.info("No database output found", created_by='system')
            return None

        output_strategy = IOStrategy(self.config, self.variables)

        for output_file in self.config.get_attr('output_files', default=[]):
            if output_file is not None:
                # Choosing type of dataframe - spark, text or pandas(default)
                if output_file.get('output_type') == 'spark':
                    pass
                elif output_file.get('output_type') == 'text':
                    pass
                elif output_file.get('output_type') == 'pandas':
                    try:
                        output_strategy.save(output_file)
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
                    pass
            else:
                logger.error('Output_file is None, check in config.json if every item in output_files has file_name '
                             'and variable_name.', created_by='system')

    def save_to_db(self):
        """
        Method for saving data into database.
        """

        if self.config.get_attr('output_db') is None:
            logger.info("No database output found", created_by='system')
            return None

        for output_database in self.config.get_attr('output_db', default=[]):
            # Choosing type of dataframe
            if output_database.get('output_type') == 'spark':
                pass
            elif output_database.get('output_type') == 'text':
                pass
            else:
                try:
                    db_loader = DBWriter(config=self.config, variables=self.variables)
                    db_loader.write(output_database)
                except Exception as e:
                    error_message = str(e)
                    logger.error(error_message, created_by='system')
                    if self.error_handling == 'skip':
                        continue
                    elif self.error_handling == 'exit':
                        raise e
                    else:
                        raise e
