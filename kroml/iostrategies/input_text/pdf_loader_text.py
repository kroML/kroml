from iostrategies.input_text.loader_text import Loader
from utils.logger import Logger
from pdfminer.pdfpage import PDFPage

logger = Logger(__name__)


@logger.for_all_methods(in_args=True)
class PDFLoader(Loader):

    def __init__(self, config, variables):
        super().__init__(config, variables)

    def load(self, input_file: dict) -> None:
        """
        Function loads PDF file, which name is stored in input_file's 'file_name', into list of pdf objects (name stored
        in input_file's 'variable_name') with or without renaming columns - according to 'format_strategy'.
        Dataframe is stored as object in variables with a key as input_file's 'variable_name'.

        :param dict input_file: Function takes as a parameter dictionary, that contains name of the file that should be
        loaded with a key 'file_name', a name of object where this file will be written with a key 'variable_name'
        and optional key 'format_strategy' where the value is a name of input strategy to be used to map column names.
        :return None: No return value
        """
        pdf_path = self.config.get_attr('input_directory') + input_file.get('file_name')

        document = open(pdf_path, 'rb')
        pdf_list_of_objects = PDFPage.get_pages(document)

        self.variables.set_object(key=input_file['variable_name'], obj=pdf_list_of_objects)
