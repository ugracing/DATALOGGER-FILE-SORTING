import sys
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


def read_file(filename, config_file):
    """Reads a test file and returns a dictionary, where the keys are the IDs and the values are another dictionary. 
    This second dictionary contains a list with all the samples and another list with the time those samples were 
    taken. """

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
    for row in new_data:

        stripped_line = row.strip().split(",")
        time_stamp = stripped_line[0].split(":")

        # read only lines with data samples
        if len(stripped_line) == 3 and len(time_stamp) == 3:

            time_sec = time_stamp[2]

            # sample number should be separated into digits
            sample_digits = [str(a) for a in str(stripped_line[2])]
            device_id = stripped_line[1][2:]

            # IDs 585, 2006 and 2007 are ignored for now
            # if device_id not in config_file:
            #    continue

            try:
                distribution = [str(a) for a in str(config_file[device_id][2])]

            except KeyError:
                if device_id == "585":
                    distribution = ["2", "2", "2", "2"]
                    device_id = "181"

                    if sample_digits[1] == "0":
                        device_id = "180"

                    elif sample_digits[1] == "1":
                        device_id = "180_181"

                else:
                    print("ID", device_id, "unknown. A file for it could not be created.")
                    continue

            # Process second CAN packet containing pressure data -- not yet working
            if device_id == "180_181":
                sample_unit = "".join(sample_digits[:(int(distribution[0]) * 2)])
                del sample_digits[:(int(distribution[0]) * 2)]

                if "180" in data_dict:
                    # Store first sample into ID 180
                    data_dict["180"]["Time"].append(time_sec)
                    data_dict["180"]["Samples"][0].append(sample_unit)

                else:
                    data_dict["180"] = {"Time": [time_sec], "Samples": []}
                    sample_list = [sample_unit]
                    data_dict["180"]["Samples"].append(sample_list)

                if "181" in data_dict:
                    data_dict["181"]["Time"].append(time_sec)

                    for i in range(2):
                        # sample corresponding to a unit
                        sample_unit = "".join(sample_digits[:(int(distribution[i]) * 2)])
                        del sample_digits[:(int(distribution[i]) * 2)]
                        data_dict[device_id]["Samples"][i].append(sample_unit)

                else:
                    data_dict["181"] = {"Time": [time_sec], "Samples": []}
                    for i in range(2):
                        # sample corresponding to a unit
                        sample_unit = "".join(sample_digits[:(int(distribution[i]) * 2)])
                        del sample_digits[:(int(distribution[i]) * 2)]
                        sample_list = [sample_unit]
                        data_dict[device_id]["Samples"].append(sample_list)

            else:
                if device_id in data_dict:
                    data_dict[device_id]["Time"].append(time_sec)

                    for i in range(len(distribution)):
                        # sample corresponding to a unit
                        sample_unit = "".join(sample_digits[:(int(distribution[i]) * 2)])
                        del sample_digits[:(int(distribution[i]) * 2)]
                        data_dict[device_id]["Samples"][i].append(sample_unit)

                else:
                    data_dict[device_id] = {"Time": [time_sec], "Samples": []}
                    for i in range(len(distribution)):
                        # sample corresponding to a unit
                        sample_unit = "".join(sample_digits[:(int(distribution[i]) * 2)])
                        del sample_digits[:(int(distribution[i]) * 2)]
                        sample_list = [sample_unit]
                        data_dict[device_id]["Samples"].append(sample_list)

    f.close()
    return data_dict


def create_files(sample_dict, config, filename):
    """Create a file for every ID"""
    for device_id in sample_dict:
        with open(config[device_id][0] + "_" + device_id + "_" + filename.split("/")[-1], 'w') as f:
            f.write("%s,%s\n" % ("Package ID", "Units"))
            f.write("%s,%s\n" % (device_id, config[device_id][-1]))

            # units = config[device_id][-1].split(" ")

            f.write("%s,%s\n" % ("Time", "Samples"))
            for i in range(len(sample_dict[device_id]["Time"])):
                f.write("%s" % sample_dict[device_id]["Time"][i])
                for j in range(len(sample_dict[device_id]["Samples"])):
                    f.write(",%s" % sample_dict[device_id]["Samples"][j][i])
                f.write("\n")


def main():
    # config_dir = r"/Users/marinasanjose/PycharmProjects/file_sorting/CONFIG.CSV"
    # file_dir = r"/Users/marinasanjose/PycharmProjects/file_sorting/TEST19.CSV"
    config_dir = Path(input("Please input the path of the config.csv file\n"))
    file_dir = input("Please input the path of the test file\n")

    # Create a dictionary containing the information inside the config file
    config_dict = read_config(config_dir)
    print(config_dict)
    config_dict["2006"] = ["ECU", "8", "2222", "%i %i %i %i", "x10-Degrees x10-Degrees x10-Percentage milliVolts"]
    config_dict["2007"] = ["ECU", "6", "222", "%i %i %i", "Percentage x10-Percentage x10-Percentage"]

    # Create a dictionary containing the information inside a test file
    file_dict = read_file(file_dir, config_dict)

    # Create csv files from the file dictionary
    create_files(file_dict, config_dict, file_dir)


if __name__ == '__main__':
    main()
