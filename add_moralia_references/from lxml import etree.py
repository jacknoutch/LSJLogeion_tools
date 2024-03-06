from lxml import etree

xml = "<bibl>text1<author>text2</author>tail1<id>text3<bibl>text4</bibl>tail2</id>tail3</bibl>tail4"

root = etree.fromstring(xml)

traversed_elements = [[e.text, e.tail] for e in root]

print(traversed_elements)