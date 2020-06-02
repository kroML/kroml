from utils.logger import Logger
from abc import ABC, abstractmethod
from os.path import exists
from keras.models import Model, load_model, Sequential
from keras.layers import Dense, Activation


class Module(ABC):
    """
    Abstract class that represents internal module with __init__ and abstract execute method.
    """
    def __init__(self, config, variables):
        self.config = config
        self.variables = variables
        self.model = Model()

    def save_model(self, filename: str, overwrite= False) -> None:
        """
        Method for saving model into models directory without overwriting
        :param name: name->name of model
        """
        directory = self.config.get_attr("models_directory")
        parts = filename.rpartition('.')
        if parts[1] == '.':
            extension = parts[1] + parts[2]
            filename = parts[0]
        else:
            extension = '.h5'

        if not overwrite:
            number = 1
            while exists(directory + filename + str(number) + extension):
                number += 1
            filename = filename + str(number)

        self.model.save(directory + filename + extension, overwrite)

    def load_model(self, filename: str, lastVersion= False) -> Model:
        """
        Method for loading model
        :param name: name->model name
        :return: Model or Exception
        """
        directory = self.config.get_attr("models_directory")

        parts = filename.rpartition('.')
        if parts[1] == '.':
            extension = parts[1] + parts[2]
            filename = parts[0]
        else:
            extension = '.h5'

        if lastVersion:
            number = 1
            while exists(directory + filename + str(number) + extension):
                number += 1

            if number == 1:
                raise Exception("No saved model for: " + filename + " found!")
            else:
                number -= 1
                return load_model(directory + filename + str(number) + extension)
        else:
            if exists(directory + filename + extension):
                return load_model(directory + filename + extension)
            else:
                raise Exception("No saved model for: " + filename + " found!")