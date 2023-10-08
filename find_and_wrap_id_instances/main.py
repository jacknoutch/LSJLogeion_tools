# This script finds all "Id." instances and wraps them in an <author> tag

import os, sys
from find_and_wrap_id_instances import *

def main():

    arguments = sys.argv[1:]

    # Load the XML files
    path_from = arguments[0] if arguments else "../LSJLogeion/"
    path_to = arguments[1] if len(arguments) > 1 else "../LSJLogeionNew/"
    files = load_files(path_from)

    # TODO: print out a running count of the number of elements added with each file
    new_elements_counter = 0

    # Loop through the XML files
    for file in files:

        with open(path_from + file, "r") as f1:

            print(f"{file} in progress...")
            file_string = f1.read().encode("utf-8")
            new_file_string = find_and_wrap_id_instances(file_string)
            print(f"{file} complete!")
            
            with open(path_to + file, "w") as f2:
                f2.write(new_file_string )

def load_files(path):
    
    # Load XML files
    lsj_xml_files = os.listdir(path) # all files in the file path
    lsj_xml_files = [x for x in lsj_xml_files if x[-4:] == ".xml"] # only XML files please
    lsj_xml_files.remove("greatscott01.xml") # front matter; not required for search
    lsj_xml_files.sort()

    return lsj_xml_files

main()