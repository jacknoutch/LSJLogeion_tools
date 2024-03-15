import os, sys
from lxml import etree

def main():

    arguments = sys.argv[1:]
    
    # Load XML files
    path_from = arguments[0] if arguments else "../../LSJLogeion/"
    path_to = arguments[1] if len(arguments) > 1 else "../../LSJLogeionNew/"
    files = load_xml_files(path_from)
    
    error_checking = False

    # Initialise the collector
    plutarch_elements = []
    new_elements = []
    
    references_added = 0
    
    for file in files[:]:

        # Reset the collector for each file
        plutarch_elements[:] = []

        with open(path_from + file, "r") as f1:

            print(f"{file} in progress...")
            
            file_string = f1.read().encode("utf-8") # encoding required for lxml
            
            root = etree.fromstring(file_string)
            starting_text = "".join(root.itertext()) # for error checking
            plutarch_elements += get_plutarch_elements(root)
    
            # Wrap the references in <bibl> elements
            for element in plutarch_elements:
                new_elements[:] = []
                new_elements = wrap_references(element)
                # TODO: does wrap_reference return False if it fails? it needs to for the following conditional...
                if new_elements:
                    references_added += len(new_elements)

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
            print(f"{references_added} references added")

def load_xml_files(path):
    
    xml_files = os.listdir(path)

    re_file_match = "greatscott\d{2}\.xml"
    xml_files = [x for x in xml_files if re.match(re_file_match, x)]
    
    xml_files.sort()

    return xml_files

if __name__ == "__main__":
    main()