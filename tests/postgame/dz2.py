import sys, struct, os; sys.path.insert(0, "/home/claude/tools")
exec(open('/tmp/pg_cmp.py').read().split("rec = []")[0].replace("K = sys.argv[1]","K=sys.argv[1]"))
print(g.teleport('CELADON_CITY_CONDOMINIUMS_3F', 3, 10)); g.step('U'); g.face('U')
g.tap('A'); g.run(40)
for i in range(30):
    g.shot(f'/tmp/pg/{K}_dd{i:02d}.png')
    if g.idle(): break
    g.tap('A' if g.cb2() != g.R['owcb'] else 'B'); g.run(40)
print(K,'idle',i, 'flags', g.getflag(0x840), 'ticketflag', g.getflag(0x2A8), 'navel', g.getflag(0x84A))
g.close()
