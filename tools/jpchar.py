import re
def load(path='/home/claude/gunk/charmap.txt'):
    enc={}; 
    for line in open(path,encoding='utf-8'):
        m=re.match(r"^'(.)'\s*=\s*([0-9A-Fa-f]{2})\s*$",line.split('@')[0].strip())
        if m: enc.setdefault(m.group(1),int(m.group(2),16))
    return enc
