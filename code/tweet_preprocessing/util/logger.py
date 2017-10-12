import logging


class Logger:
    def __init__(self, logging_file):
        self.logger = logging.getLogger("MAIN LOG")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(filename=logging_file)
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        fh.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.addHandler(fh)

    def get_logger(self):
        return self.logger

    @staticmethod
    def get_logger(logger_name):
        return logging.getLogger(logger_name)

    @staticmethod
    def build_log_message(class_name, function_name, message):
        return class_name + "/" + function_name + ": " + message
