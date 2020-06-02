from manipulation.modules.abstract_module import Module
from utils.logger import Logger

logger = Logger(__name__)


@logger.for_all_methods(True)
class ExampleModule(Module):

    def execute(self, param: dict):
        df = self.variables.get_object('df_lda_in')
        self.variables.set_object(key='df_lda_out', obj=df)
        raise Exception("Example module exception")

    def train(self, param: dict):
        pass
