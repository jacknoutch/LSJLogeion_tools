import os, sys
from lxml import etree
from add_moralia_references.add_moralia_references import *
from amend_moralia_references.amend_moralia_references import *
from find_and_wrap_id_instances.find_and_wrap_id_instances import *

def main():

    arguments = sys.argv[1:]
    mode = arguments[0]
    path_from = arguments[1] if len(arguments) > 1 else "../../LSJLogeion/"
    path_to = arguments[2] if len(arguments) > 2 else "../../LSJLogeionNew/"

    files = load_xml_files(path_from)
    
    error_checking = False

    new_elements = []
    new_elements_counter = 0

    for file in files:

        # Reset the collector for each file
        new_elements[:] = []

        with open(path_from + file, "r") as f1:

            print(f"{file} in progress...")
            
            file_string = f1.read().encode("utf-8") # encoding required for lxml
            root = etree.fromstring(file_string)
            
            if error_checking:
                starting_text = "".join(root.itertext())
            
            if mode == "add":
                plutarch_elements = get_plutarch_elements(root)
        
                # Wrap the references in <bibl> elements
                for element in plutarch_elements:
                    new_elements[:] = []
                    new_elements = wrap_references(element)
                    # TODO: does wrap_reference return False if it fails? it needs to for the following conditional...
                    if new_elements:
                        new_elements_counter += len(new_elements)

            elif mode == "amend":
                moralia_bibls = get_moralia_bibls(root)
                new_elements = process_moralia_bibls(moralia_bibls)
                new_elements_counter += len(new_elements)

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
            print(f"{new_elements_counter} elements added/changed")

def load_xml_files(path):
    
    xml_files = os.listdir(path)

    re_file_match = "greatscott\d{2}\.xml"
    xml_files = [x for x in xml_files if re.match(re_file_match, x)]
    
    xml_files.sort()

    return xml_files

if __name__ == "__main__":
    main()