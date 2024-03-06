from lxml import etree

xml = "<xml><bibl>text1<cit>some<author>Plu.</author>tail1</cit>123a<id>text3<bibl>text4</bibl>tail2</id>tail3</bibl>tail4</xml>"

root = etree.fromstring(xml)

traversed_elements = [[e.text, e.tail] for e in root.iterdescendants()]

print(traversed_elements)

def post_order_traversal(node):
    if node is not None:
        for child in node:
            post_order_traversal(child)
        print(node.text, node.tail)

# post_order_traversal(root)

# if the stephanus reference is in the tail of an element with children, those children must be processed before 

def custom_traversal(node):
    if node is not None:
        print(node.tag, node.text)
        for child in node:
            custom_traversal(child)
        print(node.tail)        

custom_traversal(root)