import re
from lxml import etree
from utilities.utilities import *
from copy import deepcopy

def get_moralia_bibls(root: etree.Element) -> list[etree.Element]:
    """Returns a list of <bibl> elements referring to Plutarch's Moralia."""
    return [e for e in root.iter() if is_valid_moralia(e)]

def is_valid_moralia(element: etree.Element) -> bool:
    """Returns a boolean to test if an element is a valid <bibl> element for Plutarch's Moralia."""
    if not element.tag == "bibl":
        return False
    
    n_attribute = element.get("n")

    if not n_attribute:
        return False
    
    parsed_n_attribute = parse_n_attribute(n_attribute)

    if not parsed_n_attribute:
        return False
    
    author, work, stephanus = parsed_n_attribute
    if author not in ["0007", "0094"]:
        return False
    
    global moralia_abbreviations
    moralia_works = moralia_abbreviations["work"].unique()
    work = int(work)
    if work not in moralia_works:
        return False

    return True

def process_moralia_bibls(bibls: list[etree.Element]) -> list[etree.Element]:
    
    return [e for e in bibls if process_moralia_bibl(e) is not False]

def process_moralia_bibl(bibl: etree.Element) -> bool:
    """Tests various aspects of the <bibl> element and amends as necessary."""
    old_bibl = deepcopy(bibl)
    
    amendments = {
        "n_stephanus_doesnt_match": False,
        "n_stephanus_not_in_work_range": False,
        "title_element_abbrev_incorrect": False,
        "title_element_needed_post_author": False,
        "title_element_needed_no_author": False,
    }

    n_attribute = bibl.attrib["n"]
    n_author, n_work, n_stephanus = parse_n_attribute(n_attribute)
    n_work = int(n_work)
    
    # Does the "n" attribute's stephanus match the one in the text?
    bibl_text = "".join(bibl.itertext())
    re_stephanus = r"\b([1-9]\d{0,3}[a-f])\b"
    text_stephanus = re.search(re_stephanus, bibl_text).group()

    if n_stephanus != text_stephanus:
        n_stephanus = text_stephanus
        bibl.attrib["n"] = f"Perseus:abo:tlg,{n_author},{n_work:03d}:{n_stephanus}"
        amendments["n_stephanus_doesnt_match"] = True
    
    # Is the "n" attribute's stephanus within the work's stephanus range?
    df_work = get_moralia_info(n_work, n_author)
    
    if df_work.empty:
        # no matching author/work
        #TODO: how to handle this?
        return False

    n_start, n_end = get_stephanus_range(df_work)

    if not is_between(n_stephanus, n_start, n_end):
        n_author, n_work, n_abbreviation = get_tlg_reference(n_stephanus, moralia_abbreviations)
        bibl.attrib["n"] = f"Perseus:abo:tlg,{n_author:04},{n_work:03}:{n_stephanus}"
        amendments["n_stephanus_not_in_work_range"] = True

    # Test title element
    # Is the abbreviation in <title> correct?
    title_element = bibl.find("title")

    try:
        n_abbreviation = df_work["abbreviation"].iloc[0]
    except NameError:
        pass
    
    if title_element is not None:
        title = title_element.text
        title = "".join([char for char in title if char not in "[]"])

        if n_abbreviation != title:
            title_element.text = f"[{n_abbreviation}]"
            amendments["title_element_abbrev_incorrect"] = True

    else:
        previous_title = get_previous_tag("title", bibl, "div2")

        if previous_title is None or previous_title.text != f"[{n_abbreviation}]":
            new_title_element = etree.SubElement(bibl, "title")
            new_title_element.text = f"[{n_abbreviation}]"    

            author_element = bibl.find("author")
            if author_element is not None:
                    
                new_title_element.tail = author_element.tail
                author_element.tail = " "
                amendments["title_element_needed_post_author"] = True

            else:
                new_title_element.tail = f" {bibl.text}"
                bibl.text = ""
                amendments["title_element_needed_no_author"] = True

    for k, v in amendments.items():
        if v:
            # etree_print(old_bibl)
            # etree_print(bibl)
            return True
    
    return False    