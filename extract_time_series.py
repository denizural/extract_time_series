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
import numpy as np
import pandas as pd
import netCDF4 as nc4
from scipy.interpolate import RegularGridInterpolator

LOGGING_LEVELS = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]


def bilinear_interpolation(nc_var, lats, lons, lat, lon):
    # find the closest coordinate
    lats_min_loc = np.abs(lats - lat).argmin()
    lons_min_loc = np.abs(lons - lon).argmin()

    # TODO: esitlik durumuna bak
    # TODO: IMPORTANT: ERA5 goes from North to South (downward) and East to West
    if lats[lats_min_loc] <= lat:
        index_south = lats_min_loc
        index_north = lats_min_loc - 1
    else:
        index_south = lats_min_loc + 1
        index_north = lats_min_loc
        logger.debug("No here")

    if lons[lons_min_loc] <= lon:
        index_west = lons_min_loc
        index_east = lons_min_loc + 1
    else:
        index_west = lons_min_loc - 1
        index_east = lons_min_loc

    south = lats[index_south]
    north = lats[index_north]
    west = lons[index_west]
    east = lons[index_east]

    delta_lon = east - west
    delta_lat = north - south

    var_sw = nc_var[index_south, index_west]
    var_se = nc_var[index_south, index_east]
    var_nw = nc_var[index_north, index_west]
    var_ne = nc_var[index_north, index_east]

    # TODO: be careful for the east - west sign
    delta_east = east - lon
    delta_west = lon - west
    south_level = (delta_east / delta_lon) * var_sw + (delta_west / delta_lon) * var_se
    north_level = (delta_east / delta_lon) * var_nw + (delta_west / delta_lon) * var_ne

    interpolated_data = ((north - lat) / delta_lat) * south_level + (
        (lat - south) / delta_lat
    ) * north_level

    return interpolated_data


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
        default=None,
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
    parser.add_argument(
        "-l", "--logging", type=str, help="logging level", default="ERROR"
    )

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
    logging.basicConfig(
        format=FORMAT,
        level=cmd_args.logging,
        handlers=[RichHandler(show_level=True, show_time=False, show_path=False)],
    )
    # logging.basicConfig(format=FORMAT, level=logging.DEBUG, datefmt="")

    logger = logging.getLogger("rich")
    logger.info("::: main code is called")
    logger.debug(cmd_args)

    # coordinates.index.to_list()
    metadata_fpath = pathlib.Path(cmd_args.metadata)
    logger.debug(f"metadata file exists: {metadata_fpath.exists()}")
    metadata = pd.read_csv(metadata_fpath)
    logger.debug(metadata)

    # TODO: add testing: inside the current coordinates file
    index = cmd_args.index
    assert index is not None
    # Eg. index > len(coordinates)-1 -> IndexError

    # open coordinates file
    coordinates_fpath = pathlib.Path(cmd_args.coordinates)
    logger.debug(f"coordinate file exists: {coordinates_fpath.exists()}")
    coordinates = pd.read_csv(coordinates_fpath)
    coordinates = coordinates.iloc[index]

    # TODO: add testing
    path = cmd_args.path
    assert path is not None
    path = pathlib.Path(path)
    assert path.exists()

    # TODO: add testing
    variable = cmd_args.variable
    assert variable is not None
    prefixes = metadata.prefix.to_list()
    assert variable in prefixes
    # extract the ERA5 variable name from the table. Eg. t2m, u10, ...
    era_var_name = metadata[metadata.prefix == variable]["variable_name"][0]

    year = cmd_args.year

    # eg. T2_2016_10.nc
    # TODO: month will be MM and will be a variable
    nc_fname = f"{variable}_{year}_10.nc"
    nc_fpath = path / nc_fname

    # TODO: add testing
    logger.debug(nc_fpath)
    assert nc_fpath.exists()

    # logger.debug("Hello, World!")
    # logger.info("Hello, World!")
    # logger.warning("Hello, World!")
    # logger.error("Hello, World!")
    # logging.debug("Hi There")
    # logger.error("[bold red blink]Server is shutting down![/]", extra={"markup": True})

    # sample file
    # nc_fname = "U10_2016_01.nc"
    # nc_fpath = work_dir / nc_fname

    # TODO: wind data
    # var_name = "t2m"

    # open the file and retrieve the coordinates & data
    nc_file = nc4.Dataset(nc_fpath)
    lats = nc_file.variables["latitude"][:]
    lons = nc_file.variables["longitude"][:]

    time_index = 0
    nc_var = nc_file.variables[era_var_name][time_index, :, :]

    time = nc_file.variables["time"][:]
    t_raw = nc_file.variables["time"]
    times = nc4.num2date(t_raw, t_raw.units, t_raw.calendar)

    # logger.debug(len(lats))
    # logger.debug(len(lons))
    # logger.debug(times[0])
    # logger.debug(times[-1])
    # logger.debug(coordinates)

    # diff_lats = np.diff(lats)
    # print(diff_lats.min())
    # print(diff_lats.max())

    lat = coordinates.latitude
    lon = coordinates.longitude
    # logger.debug(lat)
    # logger.debug(lon)

    # 2D meshgrid of ERA grid
    lat2d, lon2d = np.meshgrid(lats, lons, indexing="ij")

    interpolator = RegularGridInterpolator(
        (lats, lons), nc_var, method="linear", bounds_error=False, fill_value=None
    )

    fine_data = interpolator((lat, lon))

    my_value = bilinear_interpolation(nc_var, lats, lons, lat, lon)

    logger.debug(f"scipy: {fine_data}")
    logger.debug(f"my value: {my_value}")
    logger.debug(f"difference: {fine_data - my_value}")


# TODO: add configuration file: eg. json as an alternative for cmd line arguments


# TODO: check if selected variable is present
# TODO: check input path, metadata path, coordinates path

# TODO:
# - function for parsing metadata file
# - function for parsing coordinates file
