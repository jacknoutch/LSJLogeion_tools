# This script searches LSJ to find all Plu. Moralia references and wrap them in an appropriate <bibl> XML element.
#
# LSJ refers to Plutarch's Moralia according to the 2 volume Wyttenbach edition.
#
# Wyttenbach references are of the following kind: 2.1234a, composed of the volumn of Wyttenbach, a period, a stephanus
# page number and a section letter.
#
# If LSJ refers to several references in the Moralia, it first uses a Wyttenbach reference, followed by stephanus
# numbers alone. e.g. 2.1234a, 1000b.
#
# The TLG and Wyttenbach references for Plutarch's Moralia can be found in plutarch_stephanus_tlg_references.csv


# Examples of references to be caught:
# 2.510f, 625b, 693a;
# cf. <author>Plu.</author> 2.961e
# <author>Plu.</author> <title>Crass.</title> 8</bibl></cit>; <cit><quote lang="greek">οἰκέτας ὠνίους ἐξάγειν</quote> <author>Id.</author> 2.680e</cit>
# <author>Plu.</author> <title>Agis</title> 4</bibl>; <i>refinement,</i> <author>Id.</author> 2.972d;

# Examples of references not to be caught:
# <bibl n="Perseus:abo:tlg,0007,069:38c"><author>Plu.</author> <title>[Aud.phil.]</title> 2.38c</bibl></cit>, cf. 145b
# <author>Plu.</author> l.c.

# Prepatory work for this script:
# - Make sure all "Id." references are surrounded by <author> tags

import os, sys
from lxml import etree
from add_moralia_references import *

# MAIN

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