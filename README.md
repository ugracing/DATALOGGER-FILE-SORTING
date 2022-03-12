# UGR-DATALOGGER-FILE-SORTING
Script that sorts the data from a test file into separate .csv files for each device, according to the CONFIG.CSV file.


# REMINDER ON PYTHON: RUNNING A PYTHON SCRIPT

Steps:

1.- Open the command prompt (a terminal window on MACOS)

2.- Check that you are using python3 and not python2

Enter python -V

If you are using python2, install the latest version and use it instead.

3.- Enter the following command. Substitute the brackets with the absolute path to the test_file_sorting.py file.

python \<absolute path to script\>


# USING THE PROGRAM

Run the test_file_sorting.py file.

Once the script is executed, a prompt should appear in the command line to enter the path of the config.csv file.

Please download the file, write the absolute path of the file in the terminal and click enter. Be careful not to add any leading spaces after the path.

Then, another prompt will appear asking for the absolute path of a test csv file. Enter the path and click enter.

After entering it and clicking enter, the required files will be created and added to the same directory as the test_file_sorting.py file.


# HOW THE CODE WORKS

The first step is putting the contents of the CONFIG file into a dictionary. The key is the ID of the device and the value associated is a list with all the other information. The CONFIG file is missing information about IDs 2006 and 2007 so they need to be added individually to the dictionary.

Then the test file is read and put into a data structure. Aero pressure data (ID = 585) is not put into the same dictionary as the rest. The pressure data also has a sepparate fucntion to create the files, since it needs extra processing.

The numbers in the file need to be converted from hex into dec. Also, every byte of data from the ECU needs to be flipped.
