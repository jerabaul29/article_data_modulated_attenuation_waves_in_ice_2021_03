import os
import time

os.environ["TZ"] = "UTC"
time.tzset()

import datetime

from icecream import ic

ic.configureOutput(prefix="", outputFunction=print)

# the hand picked times and instruments when the oscillatory amplitude happens
dict_event_metadata = {
    # (datetime.datetime(2021, 3, 12, 0, 0, 0), datetime.datetime(2021, 3, 14, 23, 59, 59)): ["19636", "19631"],
    (datetime.datetime(2021, 3, 12, 0, 0, 0), datetime.datetime(2021, 3, 14, 23, 59, 59)): ["19636"],
    (datetime.datetime(2021, 3, 1, 0, 0, 0), datetime.datetime(2021, 3, 3, 23, 59, 59)): ["19648"],
}

# the hand picked times in the swh timestamps when have peaks or troughs of swh
dict_twh_event_peaks = {
    (datetime.datetime(2021, 3, 12, 0, 0, 0), datetime.datetime(2021, 3, 14, 23, 59, 59)):
        {
            "19636":
            [
                datetime.datetime(2021, 3, 12, 10, 2, 45),
                datetime.datetime(2021, 3, 12, 14, 7, 41),
                datetime.datetime(2021, 3, 12, 22, 5, 16),
                datetime.datetime(2021, 3, 13, 2, 8, 14),
                datetime.datetime(2021, 3, 13, 8, 5, 48),
                datetime.datetime(2021, 3, 13, 18, 0, 32),
                datetime.datetime(2021, 3, 13, 22, 0, 47),
                datetime.datetime(2021, 3, 14, 6, 7, 15),
                datetime.datetime(2021, 3, 14, 10, 5, 51),
            ],

    },
    (datetime.datetime(2021, 3, 1, 0, 0, 0), datetime.datetime(2021, 3, 3, 23, 59, 59)):
        {
            "19648":
            [
                datetime.datetime(2021, 3, 1, 10, 1, 10),
                datetime.datetime(2021, 3, 1, 18, 1, 58),
                datetime.datetime(2021, 3, 2, 0, 0, 51),
                datetime.datetime(2021, 3, 2, 6, 1, 21),
                datetime.datetime(2021, 3, 2, 12, 0, 24),
                datetime.datetime(2021, 3, 2, 18, 0, 40),
                datetime.datetime(2021, 3, 2, 20, 1, 6),
                datetime.datetime(2021, 3, 3, 8, 0, 34),
                datetime.datetime(2021, 3, 3, 12, 0, 44),
            ],
    }
}

list_instruments_close_each_other = [
    "13319",
    "19631",
]

ic(dict_event_metadata)
