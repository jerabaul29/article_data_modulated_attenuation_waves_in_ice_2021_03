import os
import time

os.environ["TZ"] = "UTC"
time.tzset()

import datetime

from pathlib import Path

import matplotlib as mpl
from matplotlib import cm

import netCDF4 as nc4

import numpy as np

from icecream import ic

ic.configureOutput(prefix="", outputFunction=print)

path_data_2021 = Path("./data_drift_waves_Barents_2021_02_v2021.nc")
path_data_2018 = Path("./data_drift_waves_Barents_2021_02_v2018.nc")


def load_data_from_nc_file(path_data):
    dict_extracted_data = {}

    with nc4.Dataset(path_data, "r", format="NETCDF4") as ds:
        nbr_trajectories = ds.dimensions["trajectory"].size
        list_instruments = []
        for ind_trajectory in range(nbr_trajectories):
            crrt_instrument_id = ""
            array_chars = ds["trajectory_id"][ind_trajectory, :]
            for crrt_char in array_chars:
                if np.ma.is_masked(crrt_char):
                    break
                crrt_instrument_id += crrt_char.decode('ascii')
            list_instruments.append(crrt_instrument_id)

            # read the data content and organize it into
            # dicts {time: (spectrum, swh, hs, tp, tz0)} and {time: (lat, lon)}
            crrt_dict_time_pos = {}
            dict_time_wave = {}

            array_kind = ds["message_kind"][ind_trajectory, :]
            array_lat = ds["lat"][ind_trajectory, :]
            array_lon = ds["lon"][ind_trajectory, :]
            array_spectrum = ds["wave_spectrum"][ind_trajectory, :, :]
            array_swh = ds["swh"][ind_trajectory, :]
            array_hs = ds["hs"][ind_trajectory, :]
            array_tp = ds["tp"][ind_trajectory, :]
            array_tz0 = ds["tz0"][ind_trajectory, :]
            frequencies = ds["frequency"][:]

            for crrt_index, crrt_kind in enumerate(array_kind):
                if np.ma.is_masked(crrt_kind):
                    break
                crrt_kind = crrt_kind.decode('ascii')

                crrt_time = ds["time"][ind_trajectory, crrt_index].data
                crrt_datetime = datetime.datetime.fromtimestamp(float(crrt_time))

                if crrt_kind == "G":
                    crrt_position = (float(array_lat[crrt_index]), float(array_lon[crrt_index]))
                    crrt_dict_time_pos[crrt_datetime] = crrt_position
                elif crrt_kind == "W":
                    crrt_dict_wave = {}
                    crrt_dict_wave["spectrum"] = array_spectrum[crrt_index, :].data
                    crrt_dict_wave["swh"] = float(array_swh[crrt_index])
                    crrt_dict_wave["hs"] = float(array_hs[crrt_index])
                    crrt_dict_wave["tp"] = float(array_tp[crrt_index])
                    crrt_dict_wave["tz0"] = float(array_tz0[crrt_index])
                    crrt_dict_wave["frequencies"] = frequencies
                    dict_time_wave[crrt_datetime] = crrt_dict_wave
                elif crrt_kind == "N":
                    continue
                else:
                    raise RuntimeError("unknown kind {}".format(crrt_kind))

            dict_extracted_data[crrt_instrument_id] = {}
            dict_extracted_data[crrt_instrument_id]["time_pos"] = crrt_dict_time_pos
            dict_extracted_data[crrt_instrument_id]["time_wave"] = dict_time_wave

    return dict_extracted_data


def generate_lists_data(dict_extracted_data_in, list_instruments,
                        time_min, time_max):
    dict_data_lists = {}
    for crrt_instrument in list_instruments:
        dict_data_lists[crrt_instrument] = {}

        dict_time_pos = dict_extracted_data_in[crrt_instrument]["time_pos"]
        dict_time_wave = dict_extracted_data_in[crrt_instrument]["time_wave"]

        dict_data_lists[crrt_instrument]["tll"] = []
        dict_data_lists[crrt_instrument]["lat"] = []
        dict_data_lists[crrt_instrument]["lon"] = []
        dict_data_lists[crrt_instrument]["twh"] = []
        dict_data_lists[crrt_instrument]["swh"] = []
        dict_data_lists[crrt_instrument]["tph"] = []

        for crrt_datetime in sorted(dict_time_pos):
            if crrt_datetime >= time_min and crrt_datetime <= time_max:
                dict_data_lists[crrt_instrument]["tll"].append(crrt_datetime)
                dict_data_lists[crrt_instrument]["lat"].append(dict_time_pos[crrt_datetime][0])
                dict_data_lists[crrt_instrument]["lon"].append(dict_time_pos[crrt_datetime][1])

        for crrt_datetime in sorted(dict_time_wave):
            if crrt_datetime >= time_min and crrt_datetime <= time_max:
                dict_data_lists[crrt_instrument]["twh"].append(crrt_datetime)
                dict_data_lists[crrt_instrument]["swh"].append(dict_time_wave[crrt_datetime]["hs"])
                dict_data_lists[crrt_instrument]["tph"].append(dict_time_wave[crrt_datetime]["tp"])

    return dict_data_lists


# dict_extracted_data contains all the information from the nc file, as a dict
# structure is: [instrument]["time_pos" / "time_wave"][if "time_wave", kind: "hs", etc][datetime][data]
# this is the information for all the instruments, over all times
dict_extracted_data_2021 = load_data_from_nc_file(path_data_2021)
dict_extracted_data_2018 = load_data_from_nc_file(path_data_2018)
dict_extracted_data = {**dict_extracted_data_2018, **dict_extracted_data_2021}


def instrument_label(instrument_key):
    if instrument_key in dict_extracted_data_2018:
        return f"{instrument_key} v2018"
    if instrument_key in dict_extracted_data_2021:
        return f"{instrument_key} v2021"
    raise RuntimeError("unknown instrument")


def load_sic(datetime_in, downsampling=1):
    filename = f"multisensorSeaIce_{datetime_in.year:04}{datetime_in.month:02}{datetime_in.day:02}0600.nc"
    print(f"open sic from {filename}")
    with nc4.Dataset(filename, "r", format="NETCDF4") as nc4_fh:
        sic = nc4_fh.variables['conc'][0, ::downsampling, ::downsampling]
        lon_sic = nc4_fh.variables['lon'][::downsampling, ::downsampling]
        lat_sic = nc4_fh.variables['lat'][::downsampling, ::downsampling]

    return (lon_sic, lat_sic, sic)


class ColormapMapper:
    """A mapper from values to RGB colors using built in colormaps
    and scaling these."""

    def __init__(self, cmap, vmin, vmax, warn_saturated=False):
        """cmap: the matplotlib colormap to use, min: the min value to be plotted,
        max: the max value to be plotted."""
        self.vmin = vmin
        self.vmax = vmax
        self.warn_saturated = warn_saturated
        norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
        self.normalized_colormap = cm.ScalarMappable(norm=norm, cmap=cmap)

    def get_rgb(self, val):
        """Get the RGB value associated with val given the normalized colormap
        settings."""
        if self.warn_saturated:
            if val < self.vmin:
                print("ColormapHelper warning: saturated low value")
            if val > self.vmax:
                print("ColormapHelper warning: saturated high value")

        return self.normalized_colormap.to_rgba(val)
