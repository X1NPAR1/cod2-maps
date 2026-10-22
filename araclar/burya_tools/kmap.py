# -*- coding: utf-8 -*-
"""
kmap.py -- CoD2 'iwmap 4' yazici. Yuz satiri bicimi newvillers_geo.map'ten
olculdu:
  ( p1 ) ( p2 ) ( p3 ) MALZEME G Y 0 0 0 0 lightmap_gray 16384 16384 0 0 0 0
G/Y = dokunun dunya biriminde tekrar boyu (ornek: v_corewalll01 256 32,
sky_* 128 128). Duzlem nokta sirasi CoD1 gen_overlord/gen_kessler'den
(Q3 kurali, normal disari) -- orada derlenip oynandi.
"""

CAULK = 'caulk'
LM = 'lightmap_gray 16384 16384 0 0 0 0'

# malzeme -> varsayilan tekrar boyu (dunya birimi)
OLCEK = {
    'caulk': (64, 64), 'clip': (64, 64), 'clip_player': (64, 64), 'clip_ai': (64, 64),
    'clip_full': (64, 64), 'clip_snow': (64, 64), 'clip_vehicle': (64, 64),
    'clip_nosight': (64, 64), 'portal': (64, 64), 'portal_nodraw': (64, 64),
    'nodraw': (64, 64), 'mantle_over': (64, 64), 'mantle_on': (64, 64),
}
VARSAYILAN = (128, 128)
# Olculen gorunus (b2 tur goruntuleri): 256'da ahsap/tugla gerilip bulaniklasti.
for _m in ('sky_tankhunt',):
    OLCEK[_m] = (128, 128)
# burya tur goruntusu: greywood (512x64) varsayilanda gerilip dalgali gorunuyordu
OLCEK['stalingradwinter_greywood'] = (256, 32)
OLCEK['mtl_fence_wood'] = (48, 192)


class Harita:
    def __init__(self):
        self.ents = []          # her biri: (anahtarlar dict, brush listesi)
        self.dunya = []         # worldspawn brushlari
        self.ws = {}
        self.malzemeler = set()

    # ------------------------------------------------------------- brush
    def _yuz(self, a, b, c, mat, olcek=None):
        self.malzemeler.add(mat)
        o = olcek or OLCEK.get(mat, VARSAYILAN)
        if isinstance(o, dict):                    # yuz-ozel olcek: {'mat': (..)}
            o = o.get(mat, OLCEK.get(mat, VARSAYILAN))
        g, y = o[0], o[1]
        ox, oy = (o[2], o[3]) if len(o) >= 4 else (0, 0)    # FIT icin doku kaydirma
        f = lambda p: '( %s %s %s )' % tuple(_s(v) for v in p)
        return ' %s %s %s %s %s %s %s %s 0 0 %s' % (f(a), f(b), f(c), mat, _s(g), _s(y),
                                                   _s(ox), _s(oy), LM)

    def kutu(self, x0, y0, z0, x1, y1, z1, ust, yan=None, alt=CAULK, olcek=None, hedef=None, detay=False):
        assert x1 > x0 and y1 > y0 and z1 > z0, ('bos kutu', x0, y0, z0, x1, y1, z1)
        yan = yan or ust
        Y = self._yuz
        L = [
            Y((x1, y1, z0), (x0, y1, z0), (x0, y0, z0), alt, olcek),
            Y((x0, y0, z1), (x0, y1, z1), (x1, y1, z1), ust, olcek),
            Y((x0, y0, z1), (x1, y0, z1), (x1, y0, z0), yan, olcek),
            Y((x1, y0, z1), (x1, y1, z1), (x1, y1, z0), yan, olcek),
            Y((x1, y1, z1), (x0, y1, z1), (x0, y1, z0), yan, olcek),
            Y((x0, y1, z1), (x0, y0, z1), (x0, y0, z0), yan, olcek),
        ]
        b = '{\n' + ('  contents detail;\n' if detay else '') + '\n'.join(L) + '\n}'
        (hedef if hedef is not None else self.dunya).append(b)
        return b

    def kutu6(self, x0, y0, z0, x1, y1, z1, m, olcek=None, hedef=None, detay=False):
        """Yuz basina malzeme: m = {'-z','+z','-y','+y','-x','+x'} (eksik -> m['*'])."""
        assert x1 > x0 and y1 > y0 and z1 > z0, ('bos kutu', x0, y0, z0, x1, y1, z1)
        g = lambda k: m.get(k, m.get('*', CAULK))
        Y = self._yuz
        L = [
            Y((x1, y1, z0), (x0, y1, z0), (x0, y0, z0), g('-z'), olcek),
            Y((x0, y0, z1), (x0, y1, z1), (x1, y1, z1), g('+z'), olcek),
            Y((x0, y0, z1), (x1, y0, z1), (x1, y0, z0), g('-y'), olcek),
            Y((x1, y0, z1), (x1, y1, z1), (x1, y1, z0), g('+x'), olcek),
            Y((x1, y1, z1), (x0, y1, z1), (x0, y1, z0), g('+y'), olcek),
            Y((x0, y1, z1), (x0, y0, z1), (x0, y0, z0), g('-x'), olcek),
        ]
        b = '{\n' + ('  contents detail;\n' if detay else '') + '\n'.join(L) + '\n}'
        (hedef if hedef is not None else self.dunya).append(b)
        return b

    def mesh(self, satirlar, mat, doku=4.0, hedef=None, detay=False):
        """CoD2 mesh (newvillers_geo.map bicimi). satirlar: [[(x,y,z),...], ...]
        Stokta satirlar +x yonunde, satir ici noktalar +y yonunde ilerler
        (A x B = +z, yuz yukari). t = (x*doku, -y*doku), lightmap = (x/16, -y/16)."""
        self.malzemeler.add(mat)
        R, C = len(satirlar), len(satirlar[0])
        o = [' {', '  mesh', '  {']
        if detay:
            o.append('  contents detail;')
        o += ['   ' + mat, '   lightmap_gray', '   %d %d 0 1' % (R, C)]
        for s in satirlar:
            assert len(s) == C
            o.append('   (')
            for (x, y, z) in s:
                o.append('\tv %s %s %s t %s %s %s %s' % (
                    _s(x), _s(y), _s(z), _s(x * doku), _s(-y * doku), _s(x / 8.0), _s(-y / 8.0)))   # lightmap 2x: gölge kenarlari pikselli cikiyordu
            o.append('   )')
        o += ['  }', ' }']
        b = '\n'.join(o)
        (hedef if hedef is not None else self.dunya).append(b)
        return b

    def konveks(self, yuzler, mats, olcek=None, hedef=None, detay=False):
        """yuzler: her yuz icin duzlem uzerinde 3 nokta (sira onemsiz).
        Yon olculen kurala gore ayarlanir: kutu() alt yuzunde
        cross(b-a, c-a) brush ICINE bakiyor (+z). Bu yuzden her yuz,
        cross(b-a,c-a) . (merkez - a) > 0 olacak sekilde siralanir."""
        tum = [p for y in yuzler for p in y]
        m = tuple(sum(p[i] for p in tum) / len(tum) for i in range(3))
        L = []
        for (a, b, c), mat in zip(yuzler, mats):
            n = _capraz(_fark(b, a), _fark(c, a))
            if _nokta(n, _fark(m, a)) < 0:
                b, c = c, b
            L.append(self._yuz(a, b, c, mat, olcek))
        br = '{\n' + ('  contents detail;\n' if detay else '') + '\n'.join(L) + '\n}'
        (hedef if hedef is not None else self.dunya).append(br)
        return br

    def kama(self, x0, y0, x1, y1, z0, zalt, zust, yon, ust, yan=None, alt=CAULK, olcek=None, detay=False, hedef=None):
        """Tabani z0, ust yuzu egik (yon: '+x' => x0'da zalt, x1'de zust)."""
        yan = yan or ust
        if yon == '+x':
            t = ((x0, y0, zalt), (x0, y1, zalt), (x1, y1, zust))
        elif yon == '-x':
            t = ((x0, y0, zust), (x0, y1, zust), (x1, y1, zalt))
        elif yon == '+y':
            t = ((x0, y0, zalt), (x1, y0, zalt), (x1, y1, zust))
        else:
            t = ((x0, y0, zust), (x1, y0, zust), (x1, y1, zalt))
        yuz = [((x0, y0, z0), (x1, y0, z0), (x1, y1, z0)), t,
               ((x0, y0, z0), (x0, y1, z0), (x0, y0, z0 + 1)),
               ((x1, y0, z0), (x1, y1, z0), (x1, y0, z0 + 1)),
               ((x0, y0, z0), (x1, y0, z0), (x0, y0, z0 + 1)),
               ((x0, y1, z0), (x1, y1, z0), (x0, y1, z0 + 1))]
        return self.konveks(yuz, [alt, ust, yan, yan, yan, yan], olcek, hedef=hedef, detay=detay)

    def oda_kabugu(self, x0, y0, z0, x1, y1, z1, kalin, zemin, duvar, tavan):
        """Ici bos kapali kutu (skybox / oda). Duvarlar ust uste binmez."""
        k = kalin
        self.kutu(x0 - k, y0 - k, z0 - k, x1 + k, y1 + k, z0, zemin)            # taban
        # TAVAN: alt yuz de gokyuzu olmali. Onceki surumde alt yuz caulk kaliyordu;
        # oyunda tavan duz beyaz goruldu ve cod2rad gunes isinlarini burada kesip
        # koyun ustune dev bir golge dusurdu (b2 tur goruntuleri, olculdu).
        self.kutu(x0 - k, y0 - k, z1, x1 + k, y1 + k, z1 + k, tavan, tavan, alt=tavan)
        self.kutu(x0 - k, y0 - k, z0, x0, y1 + k, z1, duvar, duvar)              # bati
        self.kutu(x1, y0 - k, z0, x1 + k, y1 + k, z1, duvar, duvar)              # dogu
        self.kutu(x0, y0 - k, z0, x1, y0, z1, duvar, duvar)                      # guney
        self.kutu(x0, y1, z0, x1, y1 + k, z1, duvar, duvar)                      # kuzey

    # ------------------------------------------------------------- entity
    def ent(self, sinif, brushlar=None, **kv):
        d = {'classname': sinif}
        for k, v in kv.items():
            d[k.replace('__', ' ')] = v
        self.ents.append((d, brushlar or []))
        return d

    # ------------------------------------------------------------- yaz
    def yaz(self, yol):
        o = ['iwmap 4', '// entity 0', '{']
        ws = dict(self.ws); ws['classname'] = 'worldspawn'
        for k, v in ws.items():
            o.append('"%s" "%s"' % (k, _deger(v)))
        for i, b in enumerate(self.dunya):
            o.append('// brush %d' % i)
            o.append(b)
        o.append('}')
        for n, (d, bl) in enumerate(self.ents, 1):
            o.append('// entity %d' % n)
            o.append('{')
            for k, v in d.items():
                o.append('"%s" "%s"' % (k, _deger(v)))
            for i, b in enumerate(bl):
                o.append('// brush %d' % i)
                o.append(b)
            o.append('}')
        metin = '\r\n'.join(o) + '\r\n'
        veri = metin.encode('ascii')            # once kodla, sonra yaz
        with open(yol, 'wb') as f:
            f.write(veri)
        return {'entity': len(self.ents) + 1, 'dunya_brush': len(self.dunya),
                'entity_brush': sum(len(b) for _, b in self.ents),
                'malzeme': sorted(self.malzemeler), 'bayt': len(veri)}


def _fark(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _capraz(u, v):
    return (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])


def _nokta(u, v):
    return u[0] * v[0] + u[1] * v[1] + u[2] * v[2]


def _s(v):
    v = float(v)
    return str(int(v)) if v == int(v) else ('%.4f' % v).rstrip('0').rstrip('.')


def _deger(v):
    if isinstance(v, (tuple, list)):
        return ' '.join(_s(x) for x in v)
    return str(v)
