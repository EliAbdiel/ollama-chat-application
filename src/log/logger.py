import logging
from typing import Optional

def setup_logger(logger_name: Optional[str] = 'LOGGER') -> logging.Logger:
        """
        Sets up a logger with a specified name. If no name is provided,
        the root logger is used. The logger is configured to log messages
        to the console with a timestamp, logger name, log level, and message.
        
        Args:
            logger_name (Optional[str]): The name of the logger. Defaults to LOGGER.
        
        Returns:
            logging.Logger: The configured logger instance.
        """
        logger = logging.getLogger(logger_name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger