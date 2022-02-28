import sys
import datetime
from pathlib import Path


def read_config(config_file):
    """Returns a dictionary with the contents of the config file, where each key is an ID, and each value is a list
    of the elements of a row of the file"""
    data_struct = {}

    try:  # check if file exists
        with open(config_file, 'r') as f:
            data = f.readlines()[1:]  # Ignore the header
    except Exception as e:
        print("File could not be read. Are you sure you spelled the name correctly? " + str(e))
        sys.exit(1)

    for line in data:
        stripped_line = line.strip().split(",")[:-1]
        data_struct[stripped_line[0]] = stripped_line[1:]

    f.close()
    return data_struct


def process_pressure_data(digits, time_sec, pressure_data):
    """Organises multiplexed pressure data into pressure_data dictionary. The keys are IDs 180 and 181 and their values
    are another dictionary. This second dictionary has two keys, time1 and time2, to contain the time the samples were
    taken. It also has individual lists for every pressure sample."""

    pressures = [int("".join(digits[2:6]), 16), int("".join(digits[6:10]), 16), int("".join(digits[10:14]), 16)]

    # If MUX = 0
    if digits[1] == "0":
        pressure_data["180"]["Time1"].append(time_sec)
        for i in range(3):
            pressure_data["180"]["Pressure" + str(i + 1)].append(pressures[i])

    # If MUX = 1. These samples contain information from both IDs
    elif digits[1] == "1":
        pressure_data["180"]["Time2"].append(time_sec)
        pressure_data["180"]["Pressure4"].append(pressures[0])

        pressure_data["181"]["Time1"].append(time_sec)
        for i in range(5, 7):
            pressure_data["181"]["Pressure" + str(i)].append(pressures[i - 4])

    # If MUX = 2
    else:
        pressure_data["181"]["Time2"].append(time_sec)
        for i in range(7, 9):
            pressure_data["181"]["Pressure" + str(i)].append(pressures[i - 7])

    return pressure_data


def create_pressure_files(filename, pressure_data):
    """Create csv files for the pressure data."""
    # Time and pressure lists are equal in size.
    for device_id in pressure_data:
        with open("Pressure sensor" + "_" + device_id + "_" + filename.split("/")[-1], 'w') as f:
            f.write("%s,%s,%s\n" % ("Package ID", "Pressure units", "Time units"))
            f.write("%s,%s,%s\n" % (device_id, "mBar", "Seconds"))

            if device_id == "180":
                f.write("%s,%s,%s,%s,%s,%s\n" % (
                    "Time (1-3)", "Pressure1", "Pressure2", "Pressure3", "Time (4)", "Pressure4"))

            else:
                f.write("%s,%s,%s,%s,%s,%s\n" % (
                    "Time (5-6)", "Pressure5", "Pressure6", "Time (7-8)", "Pressure7", "Pressure8"))

            time_val1 = pressure_data[device_id]["Time1"]
            time_val2 = pressure_data[device_id]["Time2"]

            length_time1 = len(time_val1)
            length_time2 = len(time_val2)

            # Within an ID, the number of samples for two given pressures might not be equal. Empty spaces are added
            # to fill in the spaces. These spaces will only need to be added if
            for i in range(max(length_time1, length_time2)):
                # Write time1
                if i < length_time1:
                    f.write("%s" % time_val1[i])
                else:
                    f.write(",")

                # If ID is 180 and not all values have been written for pressures corresponding to list time1
                if device_id == "180" and i < length_time1:
                    # Write pressure values for pressures 1-3
                    for j in range(3):
                        f.write(",%s" % pressure_data[device_id]["Pressure" + str(j + 1)][i])

                # If ID is 181 and not all values have been written for time1
                elif device_id == "181" and i < length_time1:
                    # Write pressure values for pressures 5-6
                    for j in range(5, 7):
                        f.write(",%s" % pressure_data[device_id]["Pressure" + str(j)][i])

                # If all values have been written
                else:
                    for j in range(2):
                        f.write(",")

                # Write time2
                if i < length_time2:
                    f.write(",%s" % time_val2[i])

                else:
                    f.write(",")

                # If ID is 180 and not all values have been written for pressures corresponding to list time2
                if device_id == "180" and i < length_time2:
                    # Write pressure value for pressures 4
                    f.write(",%s" % pressure_data[device_id]["Pressure4"][i])

                # If ID is 181 and not all values have been written for time2
                elif device_id == "181" and i < length_time2:
                    # Write pressure values for pressures 7 and 8
                    for j in range(7, 9):
                        f.write(",%s" % pressure_data[device_id]["Pressure" + str(j)][i])

                else:
                    f.write(",")

                f.write("\n")


def create_files(sample_dict, config, filename):
    """Create a file for every ID in sample_dict"""
    for device_id in sample_dict:
        with open(config[device_id][0] + "_" + device_id + "_" + filename.split("/")[-1], 'w') as f:
            f.write("%s,%s,%s\n" % ("Package ID", "Measurement units", "Time unit"))
            f.write("%s,%s,%s\n" % (device_id, config[device_id][-1], "Seconds"))

            f.write("%s,%s\n" % ("Time", "Samples"))
            for i in range(len(sample_dict[device_id]["Time"])):
                f.write("%s" % sample_dict[device_id]["Time"][i])
                for j in range(len(sample_dict[device_id]["Samples"])):
                    f.write(",%s" % sample_dict[device_id]["Samples"][j][i])
                f.write("\n")


def update_data_dictionary(data_dict, device_id, sample_digits, distribution, first_time):
    """Add given sample to the data dictionary."""
    for i in range(len(distribution)):
        # Make a list inside "Samples" that will hold the measurement
        if first_time:
            data_dict[device_id]["Samples"].append([])

        sample_unit = "".join(sample_digits[:(int(distribution[i]) * 2)])
        del sample_digits[:(int(distribution[i]) * 2)]

        # If the measurement is from an ECU packet, the digits need to be flipped
        if 2000 <= int(device_id) <= 2007:
            sample_unit = sample_unit[2:] + sample_unit[:2]

        measurement = int(sample_unit, 16)
        data_dict[device_id]["Samples"][i].append(measurement)

    return data_dict


def convert_to_sec(time):
    """Converts a string representing a time with the format H:M:S to seconds and returns it."""
    time_list = time.split(":")
    seconds = float(time_list[2]) + float(time_list[0]) * 3600 + float(time_list[1]) * 60
    return str(seconds)


def read_file(filename, config_file):
    """Reads a test file and creates two dictionaries: pressure_data and data_dict.
    pressure_data only contains aero pressure data, which is divided in IDs 180 and 181.
    data_dict contains sample information on all other devices. The keys are the IDs and the values are another
    dictionary. This second dictionary contains a list of lists -of all the samples divided into bytes- and another
    list with the time those samples were taken."""

    try:  # check if file exists
        with open(filename, 'r') as f:
            data = f.readlines()
    except Exception as e:
        print("File could not be read. Are you sure you spelled the name correctly? " + str(e))
        sys.exit(1)

    # Delete NUL bytes
    new_data = []  # Each element is a row from the file (strings)
    for line in data:
        new_line = line.replace('\00', '')
        new_data.append(new_line)

    data_dict = {}
    pressure_data = {
        "180": {"Time1": [], "Time2": [], "Pressure1": [], "Pressure2": [], "Pressure3": [], "Pressure4": []},
        "181": {"Time1": [], "Time2": [], "Pressure5": [], "Pressure6": [], "Pressure7": [], "Pressure8": []}
    }
    for row in new_data:
        stripped_line = row.strip().split(",")
        time = stripped_line[0].split(":")

        # read only lines with data samples
        if len(stripped_line) == 3 and len(time) == 3:
            timestamp = stripped_line[0].split(" ")[1]
            # Convert time into seconds
            time_sec = convert_to_sec(timestamp)

            # sample number should be separated into digits
            sample_digits = [str(a) for a in str(stripped_line[2])]
            device_id = stripped_line[1][2:]

            try:
                distribution = [str(a) for a in str(config_file[device_id][2])]
            except KeyError:
                if device_id == "585":
                    pressure_data = process_pressure_data(sample_digits, time_sec, pressure_data)
                    continue

                else:
                    print("ID", device_id, "unknown. A file for it could not be created.")
                    continue

            if device_id in data_dict:
                first_time = False

            else:
                data_dict[device_id] = {"Time": [], "Samples": []}
                first_time = True

            data_dict[device_id]["Time"].append(time_sec)
            data_dict = update_data_dictionary(data_dict, device_id, sample_digits, distribution, first_time)
    f.close()

    # Create csv files
    create_files(data_dict, config_file, filename)
    create_pressure_files(filename, pressure_data)


def main():
    config_dir = Path(input("Please input the path of the config.csv file\n"))
    file_dir = input("Please input the path of the test file\n")

    # Create a dictionary containing the information inside the config file
    config_dict = read_config(config_dir)
    # CONFIG.CSV file does not contain information about IDs 2006 and 2007
    config_dict["2006"] = ["ECU", "8", "2222", "%i %i %i %i", "x10-Degrees x10-Degrees x10-Percentage milliVolts"]
    config_dict["2007"] = ["ECU", "6", "222", "%i %i %i", "Percentage x10-Percentage x10-Percentage"]

    # Create csv files
    read_file(file_dir, config_dict)


if __name__ == '__main__':
    main()
