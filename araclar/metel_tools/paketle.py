# -*- coding: utf-8 -*-
"""paketle.py -- iki haritanin (krasnoye + metel) kendi urettigimiz dosyalarini
GitHub deposu klasorune kopyalar. Oyunun kendi dosyalari (iwd, stok betikler)
DAHIL EDILMEZ."""
import os, shutil, glob

OYUN = r'F:\Activision\Call of Duty 2'
DEPO = r'F:\Activision\cod2-sovyet-haritalari'

def kopya(kaynak, hedef):
    os.makedirs(os.path.dirname(hedef), exist_ok=True)
    shutil.copy2(kaynak, hedef)

for h in ('krasnoye', 'metel', 'burya', 'kumtepe', 'kasrelbab', 'sidirezegh'):
    for f in glob.glob(os.path.join(OYUN, 'main', 'maps', h + '*')):
        ad = os.path.basename(f)
        if ad.endswith(('.d3dprt', '.d3dpoly', '.lin')) or '.bak' in ad or 'duman' in ad:
            continue
        kopya(f, os.path.join(DEPO, 'main', 'maps', ad))
    for alt, uz in (('soundaliases', '.csv'), ('localizedstrings', '.str'), ('sun', '.sun')):
        kopya(os.path.join(OYUN, 'main', alt, h + uz), os.path.join(DEPO, 'main', alt, h + uz))
    plat = os.path.join(OYUN, 'main', 'localizedstrings', h + '_platform.str')
    if os.path.exists(plat):
        kopya(plat, os.path.join(DEPO, 'main', 'localizedstrings', h + '_platform.str'))
    kopya(os.path.join(OYUN, 'map_source', h + '.map'), os.path.join(DEPO, 'map_source', h + '.map'))
    arac = os.path.join(OYUN, h + '_tools')
    for f in glob.glob(os.path.join(arac, '*')):
        if os.path.isfile(f) and f.endswith(('.py', '.ps1', '.bat')):
            kopya(f, os.path.join(DEPO, 'araclar', h + '_tools', os.path.basename(f)))
print('kopyalandi ->', DEPO)
