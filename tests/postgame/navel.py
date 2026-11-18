import sys; sys.path.insert(0, "/home/claude/tools")
src=open('/tmp/pg_cmp.py').read().split("for f in list(range")[0].replace("K = sys.argv[1]","K='jp'").replace("ST = {'jp': '/tmp/walkst/s21_postgame_jp.ss', 'fp': '/tmp/walkst/fp_new.ss'}[K]","ST='/tmp/walkst/pg_end_jp.ss'")
exec(src)
sh=[]
for i in range(20):
    if g.idle(): break
    g.tap('B'); g.run(30)
print('idle', g.idle(), g.pos())
def S(t): f=f'/tmp/pg/nv_{len(sh):03d}_{t}.png'; g.shot(f); sh.append(f)
g.face('D'); g.tap('A'); g.run(60); S('a')
g.tap('A'); g.run(60); S('menu1'); g.tap('A'); g.run(60); S('b')
g.tap('D'); g.run(10); S('menu2'); g.tap('A'); g.run(60)
m0=g.pos()[2:]
for i in range(60):
    g.tap('A'); g.run(40)
    if i % 5 == 0: S('ferry')
    if g.pos()[2:] != m0 and g.idle(): break
S('arrive'); print('arrive', g.pos(), flush=True)
p=g.teleport('NAVEL_ROCK_SUMMIT', 9, 14); print('summit', p); S('summit')
g.goto(9, 12); g.run(10)
for i in range(30):
    if g.in_battle(): break
    g.tap('A'); g.run(30)
S('hooh'); print('hooh battle', g.in_battle(), g.u16(g.R['bmons']+0x58), g.u8(g.R['bmons']+0x58+0x2A), flush=True)
if g.in_battle(): print('outcome', cheat_battle())
for i in range(20): g.tap('B'); g.run(20)
S('after_hooh')
p=g.teleport('NAVEL_ROCK_BASE', 10, 17); print('base', p); g.goto(10, 16); g.face('U'); g.tap('A'); g.run(40)
for i in range(30):
    if g.in_battle(): break
    g.tap('A'); g.run(30)
S('lugia'); print('lugia battle', g.in_battle(), g.u16(g.R['bmons']+0x58), g.u8(g.R['bmons']+0x58+0x2A), flush=True)
if g.in_battle(): print('outcome', cheat_battle())
for i in range(20): g.tap('B'); g.run(20)
S('after_lugia'); g.close()
