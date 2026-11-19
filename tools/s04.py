import sys; sys.path.insert(0, "/home/claude/tools")
from playtest import *
import walker
def go(g, rec):
    g.handle(rec)
    g.go(['ROUTE1'], rec)
    g.go(['VIRIDIAN_CITY'], rec)
    g.go(['VIRIDIAN_CITY_MART'], rec); g.handle(rec)
    for i in range(6): g.tap('A'); g.run(30); g.handle(rec)
    print(g.k,'mart',g.pos(),flush=True)
    g.go(['VIRIDIAN_CITY'], rec); g.go(['ROUTE1'], rec); g.go(['PALLET_TOWN'], rec)
    g.go(['PALLET_TOWN_PROFESSOR_OAKS_LAB'], rec); g.handle(rec)
    g.interact(6, 3, 'oak parcel', rec, key='A')
    for i in range(12): g.handle(rec); g.tap('A'); g.run(30)
    print(g.k,'end',g.pos(),'dex',g.getflag(0x829),flush=True)
    sb1=g.sb1(); key=g.u16(g.u32(g.R['sb1']+4)+0xF20)
    ki=[ (g.u16(sb1+0x3B8+4*i)) for i in range(10)]
    print(g.k,'key items',ki,flush=True)
run_segment('s04_parcel', 's03_starter', go)
