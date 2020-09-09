import logging
from . import my_logger
from .data import (
    _read_json, _write_json,
    _shape_params, _get_item
)

def logger(module_name:str, loglevel=logging.DEBUG):
    module_logger = my_logger.get_logger(module_name, loglevel=loglevel)
    return module_logger