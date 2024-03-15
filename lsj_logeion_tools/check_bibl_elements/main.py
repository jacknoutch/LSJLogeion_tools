import os, re, sys
from lxml import etree
from check_bibl_elements import *

def main():

    arguments = sys.argv[1:]
    
    # Load XML files
    path_from = arguments[0] if arguments else "../../LSJLogeion/"
    path_to = arguments[1] if len(arguments) > 1 else "../../LSJLogeionNew/"
    files = load_xml_files(path_from)
    
    error_checking = False
    
    references_amended = 0
    plutarch_bibls = []
    amended_elements = []
    
    for file in files[:]:

        # Reset the collector for each file
        plutarch_bibls[:] = []
        amended_elements[:] = []

        with open(path_from + file, "r") as f1:

            print(f"{file} in progress...")
            
            file_string = f1.read().encode("utf-8") # encoding required for lxml
            
            root = etree.fromstring(file_string)
            starting_text = "".join(root.itertext()) # for error checking
            
            # Get elements
            plutarch_bibls += get_plutarch_bibls(root)
            # Process elements
            amended_elements = process_plutarch_bibls(plutarch_bibls)
            references_amended += len(amended_elements)


            # Error checking - has the text changed?
            if error_checking:
                ending_text = "".join(root.itertext())
                if starting_text != ending_text:
                    print("WARNING: text has been changed during the process!")
                    return

            # Save the new XML
            with open(path_to + file, "w") as f2:
                file_string = etree.tostring(root, encoding="unicode")
                f2.write(file_string)
                print(f"{file} done!")

            # output the file's added references
            print(f"{references_amended} references amended added")

def load_xml_files(path):
    
    xml_files = os.listdir(path)

    re_file_match = "greatscott\d{2}\.xml"
    xml_files = [x for x in xml_files if re.match(re_file_match, x)]
    
    xml_files.sort()

    return xml_files

if __name__ == "__main__":
    main()