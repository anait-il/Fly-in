import re

pattern = re.compile(r'(\w+)@(\w+)\.\w(\w+)$')
print(re.match(pattern, "name@yahoo.ma"))
