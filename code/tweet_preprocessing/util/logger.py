import logging


class Logger:
    def __init__(self, logging_file):
        self.logger = logging.getLogger("MAIN LOG")
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(filename=logging_file)
        self.logger.addHandler(fh)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

    def get_logger(self):
        return self.logger

    def info(self, message):
        self.logger.info(message)

    def exception(self, message):
        self.logger.exception(message)

    @staticmethod
    def get_logger(logger_name):
        return logging.getLogger(logger_name)

    @staticmethod
    def build_log_message(class_name, function_name, message):
        return class_name + "/" + function_name + ": " + message
