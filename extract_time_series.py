#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""extract_time_series.py:
A command-line tool to extract time series from ERA5-Land dataset
"""

__author__ = "Deniz Ural"
__authors__ = ["Deniz Ural"]
__contact__ = "denizural86@gmail.com"
__copyright__ = ""
__date__ = "2023/01/19"
__email__ = "denizural86@gmail.com"
__license__ = "GPLv3"
__maintainer__ = "Deniz Ural"
__status__ = "Development"  # Production
__version__ = "0.0.1"

import argparse
import sys
import pathlib
import logging
from rich.logging import RichHandler

LOGGING_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]

def parse_command_line_args():
    example_text = """EXAMPLES:
    Getting Help:
        extract_time_series.py --help
    
    Basic Usage:
        extract_time_series.py --index 1 --variable T2 --year 2016 
            --path /some/path --coordinates /etc/coords.csv
            --metadata /etc/metadata.csv
    
    Dry Run or Logging:
        extract_time_series.py ... --check --logging DEBUG
    """

    prog_name = pathlib.Path(sys.argv[0]).name

    # command line argument parser
    parser = argparse.ArgumentParser(
        prog=prog_name,
        epilog=example_text,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    required_args = parser.add_argument_group("required named arguments")

    required_args.add_argument(
        "-i",
        "--index",
        type=int,
        required=True,
        help="index from the locations database",
    )

    required_args.add_argument(
        "-v", "--variable", type=str, required=True, help="ERA5 variable", default=None
    )

    required_args.add_argument(
        "-y", "--year", type=str, required=True, help="year", default=None
    )

    required_args.add_argument(
        "-p",
        "--path",
        type=str,
        required=True,
        help="path to input file directory",
        default=None,
    )

    required_args.add_argument(
        "-c",
        "--coordinates",
        type=str,
        required=True,
        help="path to coordinates csv file",
        default=None,
    )

    required_args.add_argument(
        "-m",
        "--metadata",
        type=str,
        required=True,
        help="path to metadata csv file",
        default=None,
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="check mode (ie. dry run): no action is performed",
        default=False,
    )

    # choices=LOGGING_LEVELS
    parser.add_argument("-l", "--logging", type=str, help="logging level", default="ERROR")

    cmd_args = parser.parse_args()

    # Check if the command line arguments are valid
    if cmd_args.logging not in LOGGING_LEVELS:
        err_msg = f"{cmd_args.logging} is not a valid logging level"
        raise ValueError(err_msg)
        # TODO: add an exception handler and print list of logging levels

    return cmd_args


if __name__ == "__main__":
    cmd_args = parse_command_line_args()

    # logging information
    # FORMAT = '%(levelname)-8s | %(message)s'
    FORMAT = "%(message)s"
    logging.basicConfig(format=FORMAT, level=cmd_args.logging, handlers=[RichHandler(show_level=True, show_time=False, show_path=False)])
    # logging.basicConfig(format=FORMAT, level=logging.DEBUG, datefmt="")

    logger = logging.getLogger("rich")
    logger.info("::: main code is called")
    print(cmd_args)

    logger.debug("Hello, World!")
    logger.info("Hello, World!")
    logger.warning("Hello, World!")
    logger.error("Hello, World!")
    logging.debug("Hi There")
    logger.error("[bold red blink]Server is shutting down![/]", extra={"markup": True})


# TODO: check if selected variable is present
# TODO: check input path, metadata path, coordinates path

# TODO:
# - function for parsing metadata file
# - function for parsing coordinates file
