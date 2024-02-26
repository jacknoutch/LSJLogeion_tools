import re

regex = r"(a|b)"

text = "123abc456"

splits = re.split(regex, text)

print(splits)
