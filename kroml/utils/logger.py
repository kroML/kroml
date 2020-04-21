import time
import logging
import sys
import inspect
from datetime import datetime


class Logger:
    """
    Class for management logs and setting unified format, output location and logging methods.
    """
    @staticmethod
    def get_last_run_id(now_obj, filepath=None):
        filepath = filepath.replace('<date>', now_obj.strftime("%d.%m.%Y")) \
                           .replace('<time>', now_obj.strftime("%H:%M:%S"))

        try:
            with open(filepath) as fp:
                lines = fp.readlines()
                run_id = int(lines[-1].partition('|')[0]) + 1
        except Exception as e:
            print(str(e))
            run_id = now_obj.strftime("%Y%m%d") + '000000001'

        return run_id

    @staticmethod
    def set_logger_settings(logger_name: str = None, l_stream=sys.stderr, l_filename=None,
                            l_level=logging.DEBUG, l_format: str = '%(asctime)-15s|%(levelname)s|%(message)s'):
        """
        Setting up logger setting

        :param logger_name: name of logger
        :param l_stream: output stream of data
        :param l_filename: output file
        :param l_level: logger level
        :param l_format: format of output message
        """
        now = datetime.now()

        if logger_name is not None:
            pass
        else:
            root_logger = logging.getLogger()

            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            run_id = Logger.get_last_run_id(now, filepath=l_filename)

            log_formatter = logging.Formatter(f"{run_id}|{l_format}")

            root_logger.setLevel(l_level)

            if l_filename is not None:
                l_filename = l_filename.replace('<date>', now.strftime("%d.%m.%Y")) \
                                       .replace('<time>', now.strftime("%H:%M:%S"))

                file_handler = logging.FileHandler(l_filename)
                file_handler.setFormatter(log_formatter)
                root_logger.addHandler(file_handler)

            if l_stream is not None:
                console_handler = logging.StreamHandler(l_stream)
                console_handler.setFormatter(log_formatter)
                root_logger.addHandler(console_handler)

    def __init__(self, name=None):
        self.name = name
        self.logger = logging.getLogger(name)
        self.start = time.time()
        self.arr = []

    def debug(self, message: str, inp_class=None, inp_func=None, msg_type='code_exec', created_by='user'):
        if inp_class is None:
            inp_class = inspect.currentframe().f_back.f_locals['self'].__class__.__name__

        if inp_func is None:
            inp_func = inspect.currentframe().f_back.f_code.co_name

        self.logger.debug(f"{inp_class}|{inp_func}|{created_by}|{msg_type}|{message}")

    def info(self, message: str, inp_class=None, inp_func=None, msg_type='code_exec', created_by='user'):
        if inp_class is None:
            inp_class = inspect.currentframe().f_back.f_locals['self'].__class__.__name__

        if inp_func is None:
            inp_func = inspect.currentframe().f_back.f_code.co_name

        self.logger.info(f"{inp_class}|{inp_func}|{created_by}|{msg_type}|{message}")

    def warning(self, message: str, inp_class=None, inp_func=None, msg_type='code_exec', created_by='user'):
        if inp_class is None:
            inp_class = inspect.currentframe().f_back.f_locals['self'].__class__.__name__

        if inp_func is None:
            inp_func = inspect.currentframe().f_back.f_code.co_name

        self.logger.warning(f"{inp_class}|{inp_func}|{created_by}|{msg_type}|{message}")

    def error(self, message: str, inp_class=None, inp_func=None, msg_type='code_exec', created_by='user'):
        if inp_class is None:
            inp_class = inspect.currentframe().f_back.f_back.f_locals['self'].__class__.__name__

        if inp_func is None:
            inp_func = inspect.currentframe().f_back.f_back.f_code.co_name

        self.logger.error(f"{inp_class}|{inp_func}|{created_by}|{msg_type}|{message}")

    def __start_time(self, message: str, inp_class=None, inp_func=None) -> None:
        """
        Starts the timer for specific method.

        :param str message: input message (Name of class and method)
        :return None: Writes to log file / output
        """
        self.start = time.time()
        self.debug(message, inp_class=inp_class, inp_func=inp_func, msg_type='time', created_by='system')

    def __end_time(self, message: str, inp_class=None, inp_func=None) -> None:
        """
        Prints the execution time of specific method.

        :param str message: Input message (Name of class and method)
        :return None: Writes to log file / output
        """
        end = time.time() - self.start

        hours = int(end / 3600)
        minutes = int(end / 60 % 60)
        seconds = end % 60

        self.debug(message + ' Runtime: {}h {}m {:.4f}s'.format(hours, minutes, seconds),
                   inp_class=inp_class, inp_func=inp_func, msg_type='time', created_by='system')

    def for_all_methods(self, in_args=True, skip_func=tuple()):
        """
        Function for decorating all the class methods.
        """

        def wrapper(inp_class):
            for attr in inp_class.__dict__:
                if callable(getattr(inp_class, attr)):
                    if attr not in skip_func:
                        setattr(inp_class, attr, self.decorate(inp_class, getattr(inp_class, attr), in_args=in_args))
            return inp_class

        return wrapper

    def decorate(self, inp_class, inp_funct, in_args=False):
        """
        Support function for decorating class methods.
        """

        def wrapper(*args, **kwargs):
            if in_args:
                message = f"Start: Inputs - {list(args[1:])}"
            else:
                message = "Start"

            self.__start_time(message, inp_class=inp_class.__name__, inp_func=inp_funct.__name__)

            result = inp_funct(*args, **kwargs)
            self.__end_time("End", inp_class=inp_class.__name__, inp_func=inp_funct.__name__)
            return result

        return wrapper
