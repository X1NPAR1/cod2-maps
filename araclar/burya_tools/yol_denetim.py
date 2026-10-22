# -*- coding: utf-8 -*-
"""
yol_denetim.py <harita> -- g_connectpaths'ten sonra d3dbsp'deki YOL AGINI cozer
ve YONLU ulasilabilirligi denetler.

Neden: "no connections 0" yetmiyor. Olculdu (metel): motor yokus yukari adimlarda
(16'lik sundurma, merdiven) bag kurmuyor -> baglar TEK YONLU kaliyor; bina ici ve
C tepesi disaridan ULASILAMAZ ada oluyordu, AI orada takiliyordu.

Bicim (olculdu): bolum 38 = [int 8][ushort dugum_sayisi] + her dugum icin
[ushort bag_sayisi] + bag_sayisi x [ushort hedef][float mesafe]. Dugum sirasi
bolum 37 (entity metni) icindeki node_* sirasidir.
Cikti: baslangica en yakin dugumden ulasilamayan ve oradan baslangica donemeyen
dugumler. Cikis kodu 1 = sorun var.
"""
import struct, re, sys, math, os

def coz(yol):
    d = open(yol, 'rb').read()
    lump = lambda i: struct.unpack('<ii', d[8 + i * 8:16 + i * 8])
    es, eo = lump(37)
    ent = d[eo:eo + es].decode('latin-1')
    dugum = []
    oyuncu = None
    for e in re.findall(r'\{([^{}]*)\}', ent):
        kv = dict(re.findall(r'"([^"]+)" "([^"]*)"', e))
        c = kv.get('classname', '')
        if c.startswith('node_'):
            dugum.append((c[5:], tuple(map(float, kv['origin'].split()))))
        if c == 'info_player_start':
            oyuncu = tuple(map(float, kv['origin'].split()))
    ps, po = lump(38)
    L = d[po:po + ps]
    n = struct.unpack('<H', L[4:6])[0]
    assert n == len(dugum), (n, len(dugum))
    off, bag = 6, []
    for i in range(n):
        c = struct.unpack('<H', L[off:off + 2])[0]; off += 2
        bag.append([struct.unpack('<H', L[off + k * 6:off + k * 6 + 2])[0] for k in range(c)])
        off += 6 * c
    return dugum, bag, oyuncu

def erisim(bag, kok, ters=False):
    n = len(bag)
    adj = bag
    if ters:
        adj = [[] for _ in range(n)]
        for i, l in enumerate(bag):
            for j in l:
                adj[j].append(i)
    gor = [False] * n; gor[kok] = True; st = [kok]
    while st:
        u = st.pop()
        for v in adj[u]:
            if not gor[v]:
                gor[v] = True; st.append(v)
    return gor

if __name__ == '__main__':
    h = sys.argv[1] if len(sys.argv) > 1 else 'metel'
    dugum, bag, oyuncu = coz(os.path.join(r'F:\Activision\Call of Duty 2\main\maps', h + '.d3dbsp'))
    kok = min(range(len(dugum)), key=lambda i: math.dist(dugum[i][1], oyuncu))
    ileri = erisim(bag, kok)
    geri = erisim(bag, kok, ters=True)
    sorun = [i for i in range(len(dugum)) if not (ileri[i] and geri[i])]
    print('dugum %d  bag %d  kok %s' % (len(dugum), sum(map(len, bag)), [round(v) for v in dugum[kok][1]]))
    print('ulasilamayan (gidilemez veya donulemez): %d' % len(sorun))
    for i in sorun[:60]:
        print('  %4d %-12s %s  git:%s don:%s' % (i, dugum[i][0], [round(v) for v in dugum[i][1]], ileri[i], geri[i]))
    sys.exit(1 if sorun else 0)
