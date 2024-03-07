""" Util module that performs logging. """

import logging


def log_msg(functionality: str, level: str, message: str):
    """ Util function that performs logging. """
    # Create a logger
    if functionality == 'general':
        logger = logging.getLogger('general_logger')
    elif functionality == 'error':
        logger = logging.getLogger('error_logger')

    logger.setLevel(logging.DEBUG)  # Set the logging level to DEBUG

    # Create a file handler
    if functionality == 'general':
        handler = logging.FileHandler('log_files/general.log')
    elif functionality == 'error':
        handler = logging.FileHandler('log_files/error.log')

    # Create a formatter
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    # Set the formatter on the handler
    handler.setFormatter(formatter)

    # Add the handler to the logger if it doesn't already exist
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == handler.baseFilename for h in logger.handlers):
        logger.addHandler(handler)
    # Emit a log message
    if level == 'debug':
        logger.debug(message)
    elif level == 'info':
        logger.info(message)
    elif level == 'warning':
        logger.warning(message)
    elif level == 'error':
        logger.error(message)
    elif level == 'critical':
        logger.critical(message)

    return True
