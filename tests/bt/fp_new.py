import sys; sys.path.insert(0, "/home/claude/tools")
from walker import *
g=Game('fp'); 
for i in range(400):
    g.run(20); g.tap('A' if i%3 else 'S')
    if g.in_overworld() and i>50:
        g.run(120)
        if g.in_overworld() and g.idle(): break
print(i, g.pos(), hex(g.cb2())); g.snap('fpnew'); g.save('/tmp/walkst/fp_new.ss'); g.close()
