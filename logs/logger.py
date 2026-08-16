import logging


def get_logger(name:str):

    logger = logging.getLogger(name)
    logger.setLevel("INFO")


    if not logger.handlers:
        file_handler = logging.FileHandler("logs/app.log")

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)


    return logger


