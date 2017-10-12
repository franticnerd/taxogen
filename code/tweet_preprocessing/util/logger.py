import logging

class Logger:
    def __init__(self, logging_file):
        self.logger = logging.getLogger("MAIN LOG")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(filename=logging_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

    def get_logger(self):
        return self.logger

    @staticmethod
    def build_log_message(class_name, function_name, message):
        return class_name + "/" + function_name + ": " + message
