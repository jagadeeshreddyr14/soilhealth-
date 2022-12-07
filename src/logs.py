import logging
import os

class MyLogger:

    def __init__(self, module_name, filename, logging_level=logging.INFO, log_path="../logs") -> None:

        self.module_name = module_name
        self.filename = filename
        self.logging_level = logging_level
        # self.log_path = log
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)
                

    def create_logs(self):
        # create logger on the current module and set its level
        logger = logging.getLogger(self.module_name)
        logger.setLevel(self.logging_level)
        logger.propagate = False

        # create a formatter that creates a single line of json with a comma at the end
        formatter = logging.Formatter(
            (
                '{"time":"%(asctime)s", "module":"%(name)s",'
                ' "line_no":%(lineno)s, "level":"%(levelname)s", "msg":"%(message)s"},'
            )
        )

        # Create a FileHandler Instance
        file_handler = logging.FileHandler(self.filename)
        file_handler.setFormatter(formatter)

        # create a channel for handling the logger and set its format
        stream_handler = logging.StreamHandler()
        # stream_handler.setFormatter(formatter)


        if (logger.hasHandlers()):
            logger.handlers.clear()

        logger.addHandler(file_handler)

        return logger
    
    
if __name__ == "__main__":
    
    dirname = os.path.dirname(os.path.abspath(__file__))
    os.chdir(dirname)
    
    logger = MyLogger(module_name=__name__,
                    filename="../logs/soil_health.log").create_logs()
    
    
    logger.info('hello')
    logger.info('yes')
