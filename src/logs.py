import logging

def MyLogger(module_name, filename, logging_level = logging.INFO):
    # create logger on the current module and set its level
    logger = logging.getLogger(module_name)
    logger.setLevel(logging_level)



    # create a formatter that creates a single line of json with a comma at the end
    formatter = logging.Formatter(
        (
            '{"time":"%(asctime)s", "module":"%(name)s",'
            ' "line_no":%(lineno)s, "level":"%(levelname)s", "msg":"%(message)s"},'
        )
    )


    # Create a FileHandler Instance
    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(formatter)

    # create a channel for handling the logger and set its format
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    # connect the logger to the channel
    stream_handler.setLevel(logging_level)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    return logger
