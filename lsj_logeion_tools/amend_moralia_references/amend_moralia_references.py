import os, re
import pandas as pd
from lxml import etree
from utilities.utilities import *
from copy import deepcopy

def get_plutarch_bibls(root: etree.Element) -> list[etree.Element]:
    return [e for e in root.iter() if is_valid(e)]

def is_valid(element: etree.Element) -> bool:
    if not element.tag == "bibl":
        return False
    
    n_attribute = element.get("n")

    if not n_attribute:
        return False
    
    re_author = r".*tlg,(0007|0094),.*"
    if not re.fullmatch(re_author, n_attribute):
        return False

    return True

def process_plutarch_bibls(bibls: list[etree.Element]) -> list[etree.Element]:
    
    return [e for e in bibls if process_plutarch_bibl(e) is not False]

def process_plutarch_bibl(bibl: etree.Element) -> bool:
    old_bibl = deepcopy(bibl)
    amendments = []
    
    global moralia_abbreviations

    moralia_works = moralia_abbreviations["work"].unique()

    n_attribute = bibl.get("n")
    re_n_attribute = r"Perseus:abo:tlg,(?P<author>0007|0094),(?P<work>\d{3}):(?P<stephanus>\d{1,4}[abcdef])"

    matches = re.fullmatch(re_n_attribute, n_attribute)

    # Does the bibl have a valid "n" attribute?
    if not matches:
        # TODO: Check that there aren't Moralia references in here?
        return False
    
    n_author = matches["author"]
    n_work = int(matches["work"])
    
    # Is this a Moralia work?
    if not n_work in moralia_works:
        return False
    
    # Does the "n" stephanus match the one in the text?
    bibl_text = "".join(bibl.itertext())
    re_stephanus = r"\b([1-9]\d{0,3}[a-f])\b"
    text_stephanus = re.search(re_stephanus, bibl_text).group()
    n_stephanus = matches["stephanus"]

    if n_stephanus != text_stephanus:
        n_stephanus = text_stephanus
        bibl.attrib["n"] = f"Perseus:abo:tlg,{n_author},{n_work:03}:{n_stephanus}"
        amendments.append("fixed_n_stephanus")
    
    # Is the n reference's stephanus within the work's stephanus range?
    df_work = moralia_abbreviations.query(f"work == {n_work}")
    n_abbreviation = df_work["abbreviation"].iloc[0]

    n_work_start = df_work["start"].iloc[0]
    n_work_end = df_work["end"].iloc[0]
    
    if is_larger_stephanus(n_work_start, n_stephanus) or is_larger_stephanus (n_stephanus, n_work_end):
        n_author, n_work, n_abbreviation = get_tlg_reference(n_stephanus, moralia_abbreviations)
        bibl.attrib["n"] = f"Perseus:abo:tlg,{n_author:04},{n_work:03}:{n_stephanus}"
        amendments.append("fixed_n_work")

    # Test author element
    author_element = bibl.find("author")
    valid_author_text = ["Plu.", "Id.", "id.", "Ps.-Plu."]
    
    if author_element is not None:
        if author_element.text not in valid_author_text:
            print(author_element)
            

    # Test title element
    # Is the abbreviation in <title> correct?
    title_element = bibl.find("title")

    if title_element is not None:
        title = title_element.text
        title = title.replace("[","")
        title = title.replace("]","")
        if n_abbreviation != title:
            title_element.text = f"[{n_abbreviation}]"
            amendments.append("title_element_text_fixed")

    else:
        new_title_element = etree.SubElement(bibl, "title")
        new_title_element.text = f"[{n_abbreviation}]"    

        if author_element is not None:
                
            new_title_element.tail = author_element.tail
            author_element.tail = " "
            amendments.append("title_element_added_post_author")

        else:
            new_title_element.tail = f" {bibl.text}"
            bibl.text = ""
            amendments.append("title_element_added_no_author")

    if len(amendments) > 0:
        # etree_print(old_bibl)
        # etree_print(bibl)
        return bibl
    
    return False
