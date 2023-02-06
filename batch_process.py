import os

# variable = "T2"  # mandatory
# variable = "TPRC"  # mandatory
# variable = "STRD"  # optional
# variable = "U10"  # optional
# variable = "V10"  # optional
# variable = "SPRES"  # optional: required for RH calculation
# variable = "Td2"  # optional: required for RH calculation

# variables = ["T2", "TPRC", "STRD", "U10", "V10", "SPRES", "Td2"]
variables = ["SPRES", "STRD", "Td2", "U10", "V10"]
# variables = ["STRD", "SPRES", "Td2"]

check_mode = False

# point 0 is already calculated
# coordinate_indexes = [1, 2, 3, 4, 5, 6, 7, 8, 9]
coordinate_indexes = [9]  # point 0 is already calculated
years = [2018, 2019, 2020, 2021, 2022]
months = [f"{month:02}" for month in range(1, 13)]

for index in coordinate_indexes:
    for variable in variables:
        for year in years:
            for month in months:
                command = (
                    f"python  extract_time_series.py --index {index} --coordinates"
                    " data\\coordinates.csv  --metadata data\\metadata.csv"
                    f" --logging INFO --path F:\\DOSYALAR\\ERA5-Land\\{year} "
                    f"-v {variable} -y {year} -m {month}"
                )
                print(command)
                if check_mode is False:
                    os.system(command)
