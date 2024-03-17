import types
from lxml import etree

from lsj_logeion_tools.amend_moralia_references.amend_moralia_references import *
from lsj_logeion_tools.utilities.utilities import *

div2 = etree.Element("div2")

bibl1 = etree.Element("bibl", {"n": "Perseus:abo:tlg,0007,069:37b"})
bibl1.text = "2.37b"

bibl_wrong_author_tlg_ref = etree.Element("bibl", {"n": "Perseus:abo:tlg,0094,069:37b"})
bibl_wrong_author_tlg_ref.text = "37b"

div2.append(bibl1)
div2.append(bibl_wrong_author_tlg_ref)

def test_process_moralia_bibl():
    assert process_moralia_bibl(bibl1)
    assert not process_moralia_bibl(bibl_wrong_author_tlg_ref)