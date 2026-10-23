# -*- coding: utf-8 -*-
"""
gen_kasrelbab.py -- CoD2 SP 'kasrelbab' (Operation Silent Dawn, Kasr el-Bab, Misir, 2 Kasim 1942, safak).

Duzen (dunya birimi, kuzey = +Y; gok kutusu 20480 x 16384):
  GB  : baslangic sirti -- tek agac + cali obegi (oyuncu gizlenir); arkasinda takviye vadisi
  G   : konvoy yolu (bati vadisinden girer, dogu-guneyde harita disina kivrilir)
  Orta: gozetleme kulubesi (2 Alman, telsiz)
  KD  : surlu kasaba (3200 x 2600): bati buyuk kapi, dogu cikis kapisi, 10 bina
        (4 girilebilir), meydan, minare, 3 flak88; cikis yolu doguya kivrilir
Skill kurallari (cod2-map-maker): uc katman sinir, kivrik gizli yollar, kapi 64x88,
pencere 46..88 '+' kasa, esyalara clip, dugum >= 40 aralik, yikilir parcalar gok kutusu
icinde (aydinlik) ayri brushmodel; her doku/model iwd'de dogrulanir (onizleme: kb_atlas).
Bu dosya _bas.py + kumtepe yardimcilari + _govde.py birlestirilerek URETILIR (birlestir.py).
"""
import os, sys, math, random, zipfile, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kmap import Harita, OLCEK

KOK = r'F:\Activision\Call of Duty 2'
HARITA = 'kasrelbab'

# ---------------------------------------------------------------- malzemeler (onizlendi)
KUM = 'egypt_roughdirt_04'
YOL = 'duhoc_dirt_road'
KAYA = 'egypt_rock_1'
DIS = 'egypt_plaster_exteriorwall03'
DIS2 = 'egypt_plaster_stucco1'
DIS3 = 'egypt_brick_sand_generic1'
IC = 'egypt_plaster_interiorwall2'
TABAN = 'egypt_concrete_floor2'
CATI = 'egypt_gravel_roof1'
TAS = 'egypt_sandstone_generic1'
SUR = 'egypt_sandstone_wall2'
SUR_BANT = 'egypt_sandstone_towerwalltrim'
TRIM = 'egypt_wood_generic1'
KIRIS = 'egypt_wood_beam'
KAPI_M = 'egypt_wood_door2'
BUYUK_KAPI = 'egypt_wood_door1'
KAPAK = 'egypt_wood_shutters1'
TAVAN = 'egypt_wood_ceiling1'
GOK = 'sky_elalamein'
CAULK = 'caulk'
SINIR = 'clip_player'
for m_, o_ in ((KUM, (512, 512)), (YOL, (256, 256)), (DIS, (256, 256)), (DIS2, (256, 256)), (DIS3, (256, 256)),
               (IC, (256, 256)), (TABAN, (256, 256)), (CATI, (256, 256)), (TAS, (512, 256)), (SUR, (256, 256)),
               (SUR_BANT, (256, 32)), (TRIM, (64, 128)), (KIRIS, (128, 128)), (TAVAN, (256, 256)), (KAYA, (256, 256))):
    OLCEK[m_] = o_

H = Harita()
# safak: alcak, pembe-turuncu gunes, hafif kum sisi
H.ws.update({'_color': '1 .82 .70', 'ambient': '.24', 'sunlight': '1.15',
             'sundirection': '-12 70 0', 'sundiffusecolor': '1 .76 .62',
             'suncolor': '1 .70 .52', 'diffusefraction': '.55',
             '-contrastgain': '.4', 'northyaw': '90'})

# ---------------------------------------------------------------- yardimcilar
def _seg(px, py, a, b):
    ax, ay = a[:2]; bx, by = b[:2]
    dx, dy = bx - ax, by - ay
    L = float(dx * dx + dy * dy) or 1.0
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - (ax + dx * t), py - (ay + dy * t))

def ss(e0, e1, x):
    if e0 == e1:
        return 1.0 if x >= e1 else 0.0
    t = max(0.0, min(1.0, (x - e0) / float(e1 - e0)))
    return t * t * (3 - 2 * t)

def lerp(a, b, t):
    return a + (b - a) * t

def hat_uzunluk(hat):
    return sum(math.hypot(hat[i + 1][0] - hat[i][0], hat[i + 1][1] - hat[i][1]) for i in range(len(hat) - 1))

def hat_nokta(hat, m):
    kalan = m
    for i in range(len(hat) - 1):
        (ax, ay), (bx, by) = hat[i][:2], hat[i + 1][:2]
        L = math.hypot(bx - ax, by - ay)
        if kalan <= L:
            t = kalan / L if L else 0
            return (ax + (bx - ax) * t, ay + (by - ay) * t)
        kalan -= L
    return tuple(hat[-1][:2])

def hat_kes(hat, m0, m1, adim=240):
    n = max(1, int((m1 - m0) // adim))
    return [hat_nokta(hat, m0 + (m1 - m0) * k / float(n)) for k in range(n + 1)]


# ---------------------------------------------------------------- kayitlar
MODELLER = []      # (model, x, y)
KAYALAR = []       # (x, y, r)
YAPILAR = {}       # ad -> (x0, y0, x1, y1, girilir)
AGAC = []
DUVARLAR = []
DUVAR_KAPI = []

def model(m, x, y, z=None, yaw=0, kayit=True, sinif='misc_model', **kv):
    if m.startswith('tree_'):
        AGAC.append((x, y))
    if kayit:
        MODELLER.append((m, x, y))
    if z is None:
        z = yukseklik(x, y)
    return H.ent(sinif, model='xmodel/' + m, origin=(round(x, 1), round(y, 1), round(z, 1)),
                 angles=(0, yaw, 0), **kv)

def isik(x, y, z, r=260, i=.6, renk='1 0.85 0.62'):
    H.ent('light', origin=(x, y, z), radius=r, intensity=i, _color=renk,
          **{'def': 'light_point_linear_nocenter'})

def kaya(x, y, r, h, tohum, gom=40):
    rnd = random.Random(tohum)
    zt = min(yukseklik(x + dx, y + dy) for dx in (-r, 0, r) for dy in (-r, 0, r))
    zb = zt - gom
    alt, ust = [], []
    N = 11
    for k in range(N):
        a = math.radians(k * 360.0 / N + rnd.uniform(-12, 12))
        rr = r * rnd.uniform(0.75, 1.15)
        alt.append((x + math.cos(a) * rr, y + math.sin(a) * rr, zb))
        rt = rr * rnd.uniform(0.35, 0.6)
        ust.append((x + math.cos(a) * rt, y + math.sin(a) * rt, zt + h * rnd.uniform(0.75, 1.05)))
    zu = zt + h
    yuz = [((x, y, zb), (x + 10, y, zb), (x, y + 10, zb)), ((x, y, zu), (x + 10, y, zu), (x, y + 10, zu))]
    mats = [CAULK, KAYA]
    for k in range(N):
        yuz.append((alt[k], alt[(k + 1) % N], ust[k]))
        mats.append(KAYA)
    H.konveks(yuz, mats, olcek=(256, 256), detay=True)
    KAYALAR.append((x, y, r * 1.15))

def dikey_levha(a, b, z0, z1, mat, kalin=16, detay=False, hedef=None):
    (ax, ay), (bx, by) = a, b
    L = math.hypot(bx - ax, by - ay)
    nx, ny = -(by - ay) / L * kalin / 2.0, (bx - ax) / L * kalin / 2.0
    p = [(ax - nx, ay - ny), (bx - nx, by - ny), (bx + nx, by + ny), (ax + nx, ay + ny)]
    yuz = [((ax, ay, z0), (bx, by, z0), (ax + nx, ay + ny, z0)), ((ax, ay, z1), (bx, by, z1), (ax + nx, ay + ny, z1))]
    for k in range(4):
        q0, q1 = p[k], p[(k + 1) % 4]
        yuz.append(((q0[0], q0[1], z0), (q1[0], q1[1], z0), (q0[0], q0[1], z1)))
    H.konveks(yuz, [mat] * 6, detay=detay, hedef=hedef)

AKTIF_HEDEF = [None]
BOLGE = [None]          # (x0, y0, x1, y1, liste): tamamen icine dusen kutular listeye
BOLGE_KAYMA = (-5120, 2048)
def kutu6(x0, y0, z0, x1, y1, z1, m, detay=False, olcek=None, hedef=None):
    if x1 - x0 > 0.01 and y1 - y0 > 0.01 and z1 - z0 > 0.01:
        h_ = hedef if hedef is not None else AKTIF_HEDEF[0]
        if h_ is None and BOLGE[0] is not None:
            bx0, by0, bx1, by1, bl = BOLGE[0]
            if x0 >= bx0 - 0.5 and x1 <= bx1 + 0.5 and y0 >= by0 - 0.5 and y1 <= by1 + 0.5:
                h_ = bl
                if olcek is not None and len(olcek) >= 4:      # sonradan KDX/KDZ kaydirilacak
                    yatay_x = (x1 - x0) >= (y1 - y0)
                    olcek = (olcek[0], olcek[1], olcek[2] + (BOLGE_KAYMA[0] if yatay_x else 0), olcek[3] - BOLGE_KAYMA[1])
        H.kutu6(x0, y0, z0, x1, y1, z1, m, olcek=olcek, detay=detay, hedef=h_)

import re as _re
def _s2(v):
    return ('%.3f' % v).rstrip('0').rstrip('.') if v != int(v) else str(int(v))
def _kaydir(b, dx, dz):
    return _re.sub(r'\( (\S+) (\S+) (\S+) \)', lambda m: '( %s %s %s )' % (_s2(float(m.group(1)) + dx), m.group(2), _s2(float(m.group(3)) + dz)), b)
KAYMA = -9216          # burya dersi: doku tekrar boylarinin kati (hiza bozulmaz)


# =========================================================================
# BINA YAPICI (burya'dan; kullanici sartlari: kapi 64x88, pencere 46..88 '+' kasa)
# =========================================================================
K = 16
KAPI_G, KAPI_H = 64, 88
PEN_G, PEN_ALT, PEN_UST = 52, 46, 88

def delikli_duvar(eksen, a, b, c0, c1, z0, z1, delikler, m, hedef=None):
    def bx(p0, p1, q0, q1):
        if p1 - p0 > 0.01 and q1 - q0 > 0.01:
            if eksen == 'x': kutu6(p0, c0, q0, p1, c1, q1, m, hedef=hedef)
            else: kutu6(c0, p0, q0, c1, p1, q1, m, hedef=hedef)
    p = a
    for (da, db, za, zb) in sorted(delikler):
        za, zb = max(za, z0), min(zb, z1)
        if zb <= za:
            continue
        bx(p, da, z0, z1); bx(da, db, z0, za); bx(da, db, zb, z1)
        p = db
    bx(p, b, z0, z1)

def pencere_kasa(eksen, c0, c1, da, db, za, zb):
    cm = (c0 + c1) / 2.0
    xm, zm = (da + db) / 2.0, (za + zb) / 2.0
    def bx(p0, p1, q0, q1):
        if eksen == 'x': kutu6(p0, cm - 2, q0, p1, cm + 2, q1, {'*': TRIM}, detay=True)
        else: kutu6(cm - 2, p0, q0, cm + 2, p1, q1, {'*': TRIM}, detay=True)
    bx(xm - 1.5, xm + 1.5, za, zb)
    bx(da, xm - 1.5, zm - 1.5, zm + 1.5)
    bx(xm + 1.5, db, zm - 1.5, zm + 1.5)

def kapi_kanati(eksen, c0, c1, da, db, z0):
    cm = (c0 + c1) / 2.0
    m = {'*': TRIM}
    if eksen == 'x':
        m.update({'-y': KAPI_M, '+y': KAPI_M})
        kutu6(da, cm - 5, z0, db, cm + 5, z0 + KAPI_H, m, olcek=(db - da, KAPI_H, da, -z0))
    else:
        m.update({'-x': KAPI_M, '+x': KAPI_M})
        kutu6(cm - 5, da, z0, cm + 5, db, z0 + KAPI_H, m, olcek=(db - da, KAPI_H, da, -z0))

def kapak(yon, eks, c0, c1, m, z0):
    """kapali pencere: dis yuzde ahsap kepenk (doku pencereye oturtulur)."""
    a, b, za, zb = m - PEN_G / 2.0 - 2, m + PEN_G / 2.0 + 2, z0 + PEN_ALT - 2, z0 + PEN_UST + 2
    dis = c0 if yon in ('g', 'b') else c1
    lo, hi = (dis - 3, dis) if yon in ('g', 'b') else (dis, dis + 3)
    if eks == 'x':
        kutu6(a, lo, za, b, hi, zb, {'*': TRIM, '-y': KAPAK, '+y': KAPAK}, detay=True, olcek=(b - a, zb - za, a, -za))
    else:
        kutu6(lo, a, za, hi, b, zb, {'*': TRIM, '-x': KAPAK, '+x': KAPAK}, detay=True, olcek=(b - a, zb - za, a, -za))

def kapi_rampasi(yon, m, x0, y0, x1, y1, zt, boy=72):
    g = KAPI_G / 2.0 + 16
    za = zt - 18
    if yon == 'g': H.kama(m - g, y0 - boy, m + g, y0, za - 30, za, zt, '+y', TAS, TAS, alt=CAULK)
    elif yon == 'k': H.kama(m - g, y1, m + g, y1 + boy, za - 30, za, zt, '-y', TAS, TAS, alt=CAULK)
    elif yon == 'b': H.kama(x0 - boy, m - g, x0, m + g, za - 30, za, zt, '+x', TAS, TAS, alt=CAULK)
    else: H.kama(x1, m - g, x1 + boy, m + g, za - 30, za, zt, '-x', TAS, TAS, alt=CAULK)

def duz_cati(x0, y0, x1, y1, z, korkuluk=32, bosluk=None):
    """col evi duz cati: doseme + kenarda alcak parapet (cati siperi)."""
    kutu6(x0 - 8, y0 - 8, z, x1 + 8, y1 + 8, z + 14, {'*': DIS, '+z': CATI, '-z': TAVAN})
    zc = z + 14
    parca = [(x0 - 8, y0 - 8, x1 + 8, y0 + 4), (x0 - 8, y1 - 4, x1 + 8, y1 + 8), (x0 - 8, y0 + 4, x0 + 4, y1 - 4)]
    if bosluk is None:
        parca.append((x1 - 4, y0 + 4, x1 + 8, y1 - 4))
    else:                                         # dogu parapetinde merdiven gecidi
        parca += [(x1 - 4, y0 + 4, x1 + 8, bosluk - 26), (x1 - 4, bosluk + 26, x1 + 8, y1 - 4)]
    for (a, b, c, d) in parca:
        kutu6(a, b, zc, c, d, zc + korkuluk, {'*': DIS, '+z': TAS})
    return zc

def ev(ad, x0, y0, x1, y1, zt, h, acikliklar, girilir=True, taban=True, cati=True, kat_ici=True, bosluk=None):
    """Tek kat kerpic bina. acikliklar: {'g'/'k'/'b'/'d': [('kapi'|'kapali'|'pen', merkez), ...]}"""
    if taban:
        kutu6(x0, y0, zt - 40, x1, y1, zt, {'*': TAS, '+z': TABAN})
    z0, z1 = zt, zt + h
    M = lambda ic, dis: {'*': DIS, ic: IC if girilir else DIS, dis: DIS}
    duvar = {'g': ('x', x0, x1, y0, y0 + K, '+y', '-y'), 'k': ('x', x0, x1, y1 - K, y1, '-y', '+y'),
             'b': ('y', y0 + K, y1 - K, x0, x0 + K, '+x', '-x'), 'd': ('y', y0 + K, y1 - K, x1 - K, x1, '-x', '+x')}
    for yon, (eks, a, b, c0, c1, ic, dis) in duvar.items():
        dl = []
        for (tur, m) in acikliklar.get(yon, []):
            if tur in ('kapi', 'kapali'):
                dl.append((m - KAPI_G / 2.0, m + KAPI_G / 2.0, z0, z0 + KAPI_H))
                if tur == 'kapali':
                    kapi_kanati(eks, c0, c1, m - KAPI_G / 2.0, m + KAPI_G / 2.0, z0)
                # kullanici: kapi onundeki huni rampalar yapay duruyordu -> rampa yok;
                # taban avludan 2 yuksek (16 brush->brush tek yonlu degil, 2'lik esik iki yonlu)
            elif girilir:
                dl.append((m - PEN_G / 2.0, m + PEN_G / 2.0, z0 + PEN_ALT, z0 + PEN_UST))
                pencere_kasa(eks, c0, c1, m - PEN_G / 2.0, m + PEN_G / 2.0, z0 + PEN_ALT, z0 + PEN_UST)
            else:
                kapak(yon, eks, c0, c1, m, z0)
        delikli_duvar(eks, a, b, c0, c1, z0, z1, dl, M(ic, dis))
        # duvar ust bandi (kat ayirici kornis): dis yuzde ince tas serit
    if girilir and kat_ici:
        uzun_x = (x1 - x0) >= (y1 - y0)
        if uzun_x:
            for xx in range(int(x0) + 110, int(x1) - 50, 140):
                kutu6(xx, y0 + K, z1 - 10, xx + 10, y1 - K, z1, {'*': KIRIS}, detay=True)
        else:
            for yy in range(int(y0) + 110, int(y1) - 50, 140):
                kutu6(x0 + K, yy, z1 - 10, x1 - K, yy + 10, z1, {'*': KIRIS}, detay=True)
    zc = None
    if cati:
        zc = duz_cati(x0, y0, x1, y1, z1, bosluk=bosluk)
    YAPILAR[ad] = (x0, y0, x1, y1, girilir)
    return zc


# kirik duvar: ust kenari ucgen/egik parcalar (kullanici: kare kare degil, kare + ucgen)
def kirik_duvar(eksen, a, b, c0, c1, z, rnd, hedef, en_cok=70):
    p = a
    yuk = rnd.randint(8, en_cok)
    while p < b - 1:
        q = min(b, p + rnd.randint(36, 90))
        yeni_ = rnd.randint(4, en_cok)
        tur = rnd.random()
        if tur < 0.35:                                   # duz (kare) parca
            if eksen == 'x':
                kutu6(p, c0, z, q, c1, z + max(yuk, yeni_), {'*': DIS, '+z': TAS}, hedef=hedef)
            else:
                kutu6(c0, p, z, c1, q, z + max(yuk, yeni_), {'*': DIS, '+z': TAS}, hedef=hedef)
        else:                                            # egik/ucgen uclu parca
            lo, hi = sorted((yuk, yeni_))
            if hi - lo < 10:
                hi = lo + 22
            if eksen == 'x':
                H.kama(p, c0, q, c1, z, z + lo, z + hi, '+x' if yeni_ > yuk else '-x', TAS, DIS, alt=CAULK, hedef=hedef)
            else:
                H.kama(c0, p, c1, q, z, z + lo, z + hi, '+y' if yeni_ > yuk else '-y', TAS, DIS, alt=CAULK, hedef=hedef)
        yuk = yeni_
        p = q

def moloz_yigini(cx, cy, z, r, h, rnd, hedef):
    alt, ust = [], []
    for k in range(8):
        a = math.radians(k * 45 + rnd.uniform(-12, 12))
        rr = r * rnd.uniform(0.8, 1.1)
        alt.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr, z))
        ust.append((cx + math.cos(a) * rr * .35, cy + math.sin(a) * rr * .35, z + h * rnd.uniform(.8, 1.0)))
    yuz = [((cx, cy, z), (cx + 10, cy, z), (cx, cy + 10, z)), ((cx, cy, z + h), (cx + 10, cy, z + h), (cx, cy + 10, z + h))]
    mats = [CAULK, TAS]
    for k in range(8):
        yuz.append((alt[k], alt[(k + 1) % 8], ust[k])); mats.append(DIS)
    H.konveks(yuz, mats, olcek=(256, 256), hedef=hedef)


def zikzak_duvar(eksen, bas, son, c0, c1, z, h_bas, h_son, rnd, hedef):
    """bas'tan son'a: yukseklik h_bas'tan h_son'a duserken dis disli (ucgen) kirik ust kenar."""
    n = max(3, int(abs(son - bas) // 34))
    yon = 1 if son > bas else -1
    onceki = h_bas
    for i in range(n):
        a = bas + yon * abs(son - bas) * i / float(n)
        b = bas + yon * abs(son - bas) * (i + 1) / float(n)
        temel = h_bas + (h_son - h_bas) * (i + 1) / float(n)
        yeni_ = max(4, temel + (rnd.uniform(14, 30) if i % 2 == 0 else -rnd.uniform(6, 22)))
        lo, hi = sorted((onceki, yeni_))
        if hi - lo < 6:
            hi = lo + 10
        p0, p1 = min(a, b), max(a, b)
        artan = (yeni_ > onceki) == (b > a)
        if eksen == 'x':
            H.kama(p0, c0, p1, c1, z, z + lo, z + hi, '+x' if artan else '-x', TAS, DIS, alt=CAULK, hedef=hedef)
        else:
            H.kama(c0, p0, c1, p1, z, z + lo, z + hi, '+y' if artan else '-y', TAS, DIS, alt=CAULK, hedef=hedef)
        onceki = yeni_

# =========================================================================
# SINIR, ARAZI, YOLLAR
# =========================================================================
SX0, SX1, SY0, SY1 = -10240, 10240, -8192, 8192
ZTAVAN = 3584
POLI = [(-8600, -4200), (-8300, -6500), (-6000, -6900), (-2500, -6800), (1500, -6900), (5200, -6600), (8000, -5600),
        (8700, -2500), (8700, 1500), (8000, 4500), (6000, 5600), (2000, 5700), (-2500, 5500), (-6300, 5000),
        (-8300, 3600), (-8800, 600)]

def icinde(x, y, poli=POLI):
    c = False
    n = len(poli)
    for i in range(n):
        (x1, y1), (x2, y2) = poli[i], poli[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / float(y2 - y1) + x1:
            c = not c
    return c

def kenar_mes(x, y):
    return min(_seg(x, y, POLI[i], POLI[(i + 1) % len(POLI)]) for i in range(len(POLI)))

ZK = 40.0
# kasaba (surlu) ve kulube
TX0, TY0, TX1, TY1 = 2900, 1200, 6100, 3800
KAPI_Y0, KAPI_Y1 = 2370, 2630                 # bati buyuk kapi (x = TX0)
CKAPI_Y0, CKAPI_Y1 = 2470, 2730               # dogu cikis kapisi (x = TX1)
KULUBE = (-1950, -1330, -1650, -1070)
KULUBE_M = (-1800, -1200)
BASLANGIC = (-6350, -4780)
CALI_M = (-6350, -4800)                       # gizlenme calisi (GSC: r 260)

# yollar: ikisi de harita disinda kivrilir, basi gorunmez
KONVOY = [(-9900, 900), (-9500, -400), (-9400, -1500), (-9000, -2400), (-8642, -3026), (-7800, -3450), (-6800, -3600),
          (-5000, -3450), (-3200, -3550), (-1600, -3950), (-742, -4375), (-100, -5000), (300, -5900), (100, -6900), (-400, -7900)]
KONVOY_SON = (-742, -4375)                    # kullanici viewpos (2): iki kamyon buraya varinca kulube gorevi
TAKVIYE = [(-9900, -7800), (-8800, -7200), (-7600, -6650), (-6000, -6150), (-4600, -5350), (-3800, -4250),
           (-3300, -3500), (-2850, -2550), (-2300, -1750)]
CIKIS = [(6100, 2600), (7200, 2700), (8100, 2300), (8900, 1300), (9600, 0), (10000, -1200)]
PATIKA = [(-2050, -1500), (-1100, -300), (-300, 600), (900, 1700), (1900, 2400), (TX0 - 120, 2500)]
# kullanici: S ve E bos duruyordu -> guneyden dogu yoluna kivrilan eski kervan yolu (dekor; uclari kanyonda)
GUNEY = [(1800, -8000), (2300, -6900), (3400, -6000), (4300, -4600), (4600, -3200), (5600, -2000), (6900, -1300),
         (8000, -1100), (8900, -300), (9600, 0)]
YOLLAR = {'konvoy': (KONVOY, 260), 'takviye': (TAKVIYE, 0), 'cikis': (CIKIS, 240), 'patika': (PATIKA, 150), 'guney': (GUNEY, 200)}

def yol_mes_ham(x, y, ad='konvoy'):
    h, _ = YOLLAR[ad]
    return min(_seg(x, y, h[i], h[i + 1]) for i in range(len(h) - 1))

def giris_mes(x, y):
    return min(yol_mes_ham(x, y, ad) for ad in ('konvoy', 'takviye', 'cikis', 'guney'))

def kasaba_mes(x, y):
    return math.hypot(max(TX0 - x, x - TX1, 0), max(TY0 - y, y - TY1, 0))

TEPE = [((-6400, -4900), 1300, 430),                                    # baslangic sirti
        ((-8300, -1900), 700, 330), ((-8000, -2700), 500, 200),             # konvoy gelisini saklayan tepeler (bati)
        ((300, -4500), 650, 300), ((1000, -5500), 700, 320),                # konvoy gidisini saklayan tepeler
        ((-4300, -1800), 900, 180), ((-800, 1500), 1100, 210), ((1200, -2200), 900, 170), ((-3800, 2800), 1200, 260),
        ((3800, -2600), 1000, 220), ((-6500, 1500), 900, 230), ((6800, -1200), 800, 190), ((900, 4700), 900, 230),
        ((-1800, 5000), 900, 240), ((5600, 5200), 800, 210), ((7600, 4100), 700, 200)]

def zemin_ham(x, y):
    z = 0.0
    for ((cx, cy), r, hh) in TEPE:
        z += hh * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / float(r * r))
    z += 36 * math.sin(x / 1200.0 + 1.3) * math.cos(y / 1400.0) + 10 * math.sin((x + y) / 560.0)
    if not icinde(x, y):
        o = kenar_mes(x, y)
        # olculdu (tur kb1): 1300'de 1000 yukselen sirt dik beyaz duvar gibiydi, yol vadisinden gok gorunuyordu
        # -> daha genis/yumusak sirt; vadi tabani da uzaklastikca yukselir (gok gorunmez)
        dis = 200 + 950 * ss(0, 2300, o) + 260 * math.sin(x / 1700.0 + 0.7) * math.cos(y / 2100.0) * ss(300, 1400, o)
        z += dis * (0.18 + 0.82 * ss(230, 820, giris_mes(x, y))) + 420 * ss(600, 2400, o)
    else:
        z += 140 * ss(800, 0, kenar_mes(x, y))
    km = kasaba_mes(x, y)
    if km < 700:
        z = lerp(ZK, z, ss(250, 700, km))
    kk = math.hypot(x - KULUBE_M[0], y - KULUBE_M[1])
    if kk < 700:
        z = lerp(ZK + 10, z, ss(260, 700, kk))
    return z

YOL_HAT = {}
for ad, (pts, gen) in YOLLAR.items():
    YOL_HAT[ad] = ([(x, y, float(zemin_ham(x, y))) for (x, y) in pts], gen)

def yol_bilgi(x, y):
    en = (1e9, 0.0, 0)
    for ad, (hat, gen) in YOL_HAT.items():
        g = gen if gen else 220
        for i in range(len(hat) - 1):
            (ax, ay, az), (bx, by, bz) = hat[i], hat[i + 1]
            dx, dy = bx - ax, by - ay
            L = float(dx * dx + dy * dy) or 1.0
            t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L))
            d = math.hypot(x - (ax + dx * t), y - (ay + dy * t))
            if d < en[0]:
                en = (d, lerp(az, bz, t), g / 2.0)
    return en

def yol_mesafe(x, y):
    return yol_bilgi(x, y)[0]

def yukseklik(x, y):
    z = zemin_ham(x, y)
    d, yz, yg = yol_bilgi(x, y)
    if d < yg + 240:
        z = lerp(z, yz, ss(yg + 240, yg + 30, d))
    return z

H.oda_kabugu(SX0, SY0, -512, SX1, SY1, ZTAVAN, 16, CAULK, GOK, GOK)
A = 128
xs = list(range(SX0, SX1 + 1, A)); ys = list(range(SY0, SY1 + 1, A))
ZH = {}
def zh(x, y):
    k = (x, y)
    if k not in ZH:
        ZH[k] = round(yukseklik(x, y), 2)
    return ZH[k]
PAR = 4
for i0 in range(0, len(xs) - 1, PAR):
    i1 = min(i0 + PAR, len(xs) - 1)
    for j0 in range(0, len(ys) - 1, PAR):
        j1 = min(j0 + PAR, len(ys) - 1)
        H.mesh([[(xs[i], ys[j], zh(xs[i], ys[j])) for j in range(j0, j1 + 1)] for i in range(i0, i1 + 1)], KUM, doku=1.0)

def chaikin(nok, n=3):
    for _ in range(n):
        y_ = [nok[0]]
        for i in range(len(nok) - 1):
            (ax, ay), (bx, by) = nok[i][:2], nok[i + 1][:2]
            y_ += [(ax * 0.75 + bx * 0.25, ay * 0.75 + by * 0.25), (ax * 0.25 + bx * 0.75, ay * 0.25 + by * 0.75)]
        y_.append(nok[-1])
        nok = y_
    return nok

def yol_mesh(hat, gen):
    # kullanici: yolun dokusu bozuk -- keskin donemecte ic kenar noktalari ust uste binip ucgenler katlaniyordu
    hat = [(x, y, 0) for (x, y) in chaikin([p[:2] for p in hat])]
    orn = []
    for i in range(len(hat) - 1):
        (ax, ay, az), (bx, by, bz) = hat[i], hat[i + 1]
        n = max(1, int(math.hypot(bx - ax, by - ay) // 96))
        for k in range(n):
            t = k / float(n); orn.append((lerp(ax, bx, t), lerp(ay, by, t)))
    orn.append(hat[-1][:2])
    satir = []
    for k, (px, py) in enumerate(orn):
        a = orn[max(0, k - 1)]; b = orn[min(len(orn) - 1, k + 1)]
        ux, uy = b[0] - a[0], b[1] - a[1]; L = math.hypot(ux, uy) or 1; ux, uy = ux / L, uy / L
        qx, qy = -uy, ux
        satir.append([(round(px + qx * w, 2), round(py + qy * w, 2), round(yukseklik(px + qx * w, py + qy * w) + 3, 2))
                      for w in (-gen / 2.0, 0, gen / 2.0)])
    for s0 in range(0, len(satir) - 1, 23):
        parca = satir[s0:s0 + 24]
        if len(parca) > 1:
            H.mesh(parca, YOL, doku=1.0, detay=True)
yol_mesh(*YOL_HAT['konvoy'])
yol_mesh(*YOL_HAT['cikis'])
yol_mesh(*YOL_HAT['patika'])
yol_mesh(*YOL_HAT['guney'])

# gorunmez sinir (kenar); yol gecitleri: yalniz oyuncu icin (AI/araç gecer)
SINIR_KAPI = []
for i in range(len(POLI)):
    a, b = POLI[i], POLI[(i + 1) % len(POLI)]
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(L // 48))
    for k in range(n):
        p0 = (lerp(a[0], b[0], k / float(n)), lerp(a[1], b[1], k / float(n)))
        p1 = (lerp(a[0], b[0], (k + 1) / float(n)), lerp(a[1], b[1], (k + 1) / float(n)))
        dikey_levha(p0, p1, -600, 3000, SINIR)

# =========================================================================
# KASABA: zemin (brush, ZK+1), SUR, KAPILAR, KULELER
# =========================================================================
kutu6(TX0 - 300, TY0 - 300, ZK - 40, TX1 + 300, TY1 + 300, ZK + 1, {'*': TAS, '+z': KUM})
BZ = ZK + 3                                     # bina tabani: avludan 2 yuksek (rampa yok)
EV_H = 128
SUR_K = 24                                      # yarim kalinlik
SUR_H = 300
DUVARLAR = []

def sur_parca(eksen, a, b, sabit):
    if b - a < 1:
        return
    if eksen == 'x':
        kutu6(a, sabit - SUR_K, ZK - 30, b, sabit + SUR_K, ZK + SUR_H, {'*': SUR, '+z': TAS})
        kutu6(a, sabit - SUR_K - 4, ZK + SUR_H - 26, b, sabit + SUR_K + 4, ZK + SUR_H - 6, {'*': SUR_BANT}, detay=True)
        for p in range(int(a) + 20, int(b) - 40, 90):              # mazgal disleri
            kutu6(p, sabit - SUR_K, ZK + SUR_H, p + 46, sabit + SUR_K, ZK + SUR_H + 40, {'*': SUR, '+z': TAS}, detay=True)
        DUVARLAR.append((a, sabit, b, sabit))
    else:
        kutu6(sabit - SUR_K, a, ZK - 30, sabit + SUR_K, b, ZK + SUR_H, {'*': SUR, '+z': TAS})
        kutu6(sabit - SUR_K - 4, a, ZK + SUR_H - 26, sabit + SUR_K + 4, b, ZK + SUR_H - 6, {'*': SUR_BANT}, detay=True)
        for p in range(int(a) + 20, int(b) - 40, 90):
            kutu6(sabit - SUR_K, p, ZK + SUR_H, sabit + SUR_K, p + 46, ZK + SUR_H + 40, {'*': SUR, '+z': TAS}, detay=True)
        DUVARLAR.append((sabit, a, sabit, b))

def kule(cx, cy, w=170, h=430):
    kutu6(cx - w, cy - w, ZK - 30, cx + w, cy + w, ZK + h, {'*': SUR, '+z': TAS})
    kutu6(cx - w - 6, cy - w - 6, ZK + h - 30, cx + w + 6, cy + w + 6, ZK + h - 8, {'*': SUR_BANT}, detay=True)
    for (a_, b_, c_, d_) in ((cx - w, cy - w, cx + w, cy - w + 28), (cx - w, cy + w - 28, cx + w, cy + w),
                             (cx - w, cy - w + 28, cx - w + 28, cy + w - 28), (cx + w - 28, cy - w + 28, cx + w, cy + w - 28)):
        kutu6(a_, b_, ZK + h, c_, d_, ZK + h + 44, {'*': SUR, '+z': TAS}, detay=True)
    YAPILAR['kule_%d_%d' % (cx, cy)] = (cx - w, cy - w, cx + w, cy + w, False)

# guney/kuzey surlari tam; bati sur buyuk kapi ile, dogu sur cikis kapisi ile bolunur
sur_parca('x', TX0, TX1, TY0)
sur_parca('x', TX0, TX1, TY1)
sur_parca('y', TY0, KAPI_Y0 - 130, TX0)
sur_parca('y', KAPI_Y1 + 130, TY1, TX0)
sur_parca('y', TY0, CKAPI_Y0 - 110, TX1)
sur_parca('y', CKAPI_Y1 + 110, TY1, TX1)
for (cx, cy) in ((TX0, TY0), (TX1, TY0), (TX0, TY1), (TX1, TY1)):
    kule(cx, cy)
# bati kapi kuleleri (MG yuvalari ustte) + kemer
KAPI_KULE = [(TX0, KAPI_Y0 - 130 + 10), (TX0, KAPI_Y1 + 130 - 10)]
for (cx, cy) in KAPI_KULE:
    kule(cx, cy, w=120, h=400)
kutu6(TX0 - SUR_K - 10, KAPI_Y0 - 10, ZK + 270, TX0 + SUR_K + 10, KAPI_Y1 + 10, ZK + 400, {'*': SUR, '-z': TAS})   # kemer
kutu6(TX0 - SUR_K - 14, KAPI_Y0 - 10, ZK + 300, TX0 + SUR_K + 14, KAPI_Y1 + 10, ZK + 322, {'*': SUR_BANT}, detay=True)
# dogu cikis kapisi kemeri
kutu6(TX1 - SUR_K - 10, CKAPI_Y0 - 110, ZK + 280, TX1 + SUR_K + 10, CKAPI_Y1 + 110, ZK + 380, {'*': SUR, '-z': TAS})
for (cy_, ) in ((CKAPI_Y0 - 110 + 30,), (CKAPI_Y1 + 110 - 30,)):
    kutu6(TX1 - SUR_K - 20, cy_ - 30, ZK - 30, TX1 + SUR_K + 20, cy_ + 30, ZK + 280, {'*': SUR, '+z': TAS})

# KAPI ENGELLERI (yalniz oyuncu): kasabaya girince disari cikilmaz; derlemede +4000
# (yol agi kesilmesin), GSC indirir. Dogu engeli Panzer patlayinca kalkar (kamyon disarida)
for (ad_, x_, y0_, y1_) in (('kapi_engel_bati', TX0, KAPI_Y0 - 20, KAPI_Y1 + 20), ('kapi_engel_dogu', TX1, CKAPI_Y0 - 20, CKAPI_Y1 + 20)):
    _eb = []
    H.kutu(x_ - 8, y0_, ZK - 50 + 4000, x_ + 8, y1_, ZK + 600 + 4000, SINIR, SINIR, alt=SINIR, hedef=_eb)
    H.ent('script_brushmodel', brushlar=_eb, targetname=ad_)

# BUYUK KAPI (iki kanat): gok kutusu icinde (aydinlik, dugumsuz) uretilir, GSC yerine koyar;
# Crusader atisiyla parcalanir -> enkaz brushmodel'i
GDX, GDZ = -6656, 2048                           # 512 katlari; kasaba x 2900 -> -3756 (gok icinde)
_kh2 = (KAPI_Y1 - KAPI_Y0) / 2.0
for k_, (y0_, y1_) in enumerate(((KAPI_Y0, KAPI_Y0 + _kh2 - 2), (KAPI_Y0 + _kh2 + 2, KAPI_Y1))):
    _kapi = []
    kutu6(TX0 - 4 + GDX, y0_, ZK + GDZ, TX0 + 4 + GDX, y1_, ZK + 268 + GDZ,          # kullanici: kanat cok kalindi (20 -> 8)
          {'*': TRIM, '-x': BUYUK_KAPI, '+x': BUYUK_KAPI}, olcek=(y1_ - y0_, 268, y0_, -(ZK + GDZ)), hedef=_kapi)
    for zz_ in (ZK + 50, ZK + 210):
        kutu6(TX0 - 7 + GDX, y0_ + 6, zz_ + GDZ, TX0 + 7 + GDX, y1_ - 6, zz_ + 10 + GDZ, {'*': KIRIS}, detay=True, hedef=_kapi)
    ym_ = (y0_ + y1_) / 2.0
    H.kutu(TX0 - 18 + GDX, ym_ - 4, ZK - 4 + GDZ, TX0 - 10 + GDX, ym_ + 4, ZK + 4 + GDZ, 'origin', 'origin', alt='origin', hedef=_kapi)
    H.ent('script_brushmodel', brushlar=_kapi, targetname='buyuk_kapi', script_noteworthy=str(k_ + 1))

# =========================================================================
# KASABA BINALARI (10): 4 girilebilir, 6 kapali; DIS dokulari karisik
# =========================================================================
BINALAR = [
    # ad, x0, y0, x1, y1, girilir, acikliklar, dis
    ('konak', 3100, 1400, 3800, 2000, True, {'k': [('kapi', 3450), ('pen', 3220), ('pen', 3680)], 'd': [('kapi', 1700), ('pen', 1520), ('pen', 1880)],
                                             'b': [('pen', 1560), ('pen', 1840)], 'g': [('pen', 3300), ('pen', 3600)]}, DIS),
    ('han', 3100, 2950, 3800, 3600, True, {'g': [('kapi', 3450), ('pen', 3220), ('pen', 3680)], 'd': [('kapi', 3270), ('pen', 3460)],
                                           'b': [('pen', 3120), ('pen', 3420)], 'k': [('pen', 3300), ('pen', 3600)]}, DIS2),
    ('depo', 5200, 1400, 5900, 2050, True, {'k': [('kapi', 5550), ('pen', 5320), ('pen', 5780)], 'b': [('kapi', 1720), ('pen', 1540)],
                                            'd': [('pen', 1600), ('pen', 1850)], 'g': [('pen', 5400), ('pen', 5700)]}, DIS3),
    ('cami', 5200, 3150, 5750, 3550, True, {'g': [('kapi', 5480), ('pen', 5300), ('pen', 5660)], 'b': [('kapi', 3350)],
                                            'd': [('pen', 3260), ('pen', 3440)], 'k': [('pen', 5350), ('pen', 5600)]}, DIS2),
    ('k1', 4060, 1350, 4460, 1800, False, {'k': [('kapali', 4260), ('pen', 4130), ('pen', 4390)], 'b': [('pen', 1580)]}, DIS3),
    ('k2', 4650, 1350, 5050, 1750, False, {'k': [('kapali', 4850), ('pen', 4720)], 'd': [('pen', 1550)]}, DIS),
    ('k3', 3150, 2050, 3600, 2300, False, {'k': [('kapali', 3380), ('pen', 3220), ('pen', 3530)]}, DIS2),
    ('k4', 3150, 2700, 3600, 2900, False, {'g': [('kapali', 3380), ('pen', 3220), ('pen', 3530)]}, DIS),
    ('k5', 5250, 2150, 5650, 2380, False, {'k': [('kapali', 5450), ('pen', 5320)], 'b': [('pen', 2260)]}, DIS3),
    ('k6', 4950, 2750, 5300, 2980, False, {'g': [('kapali', 5120), ('pen', 5020)], 'b': [('pen', 2860)]}, DIS2),
]
_dis_yedek = DIS
for (ad, x0, y0, x1, y1, gir, ac, dm) in BINALAR:
    DIS = dm                                       # ev() dis dokusu (cesitlilik)
    ev(ad, x0, y0, x1, y1, BZ, EV_H, ac, girilir=gir)
DIS = _dis_yedek
# konagin ust kati (kapali, kepenkli; dekor)
kutu6(3100, 1400, BZ + EV_H + 14, 3800, 2000, BZ + EV_H + 28, {'*': DIS, '+z': TABAN})
ev('konak_ust', 3100, 1400, 3800, 2000, BZ + EV_H + 28, EV_H,
   {'k': [('pen', 3220), ('pen', 3450), ('pen', 3680)], 'd': [('pen', 1550), ('pen', 1850)], 'g': [('pen', 3300), ('pen', 3600)]},
   girilir=False, taban=False)
YAPILAR['konak'] = (3100, 1400, 3800, 2000, True)
# MINARE (dekor): caminin kuzeydogu kosesinde
MX, MY = 5820, 3600
for (z0_, z1_, w_) in ((ZK, ZK + 520, 70), (ZK + 520, ZK + 560, 86), (ZK + 560, ZK + 700, 56), (ZK + 700, ZK + 730, 70)):
    kutu6(MX - w_, MY - w_, z0_, MX + w_, MY + w_, z1_, {'*': DIS2, '+z': TAS})
H.kama(MX - 56, MY - 56, MX + 56, MY, ZK + 730, ZK + 730, ZK + 820, '+y', TAS, TAS, alt=TAS)
H.kama(MX - 56, MY, MX + 56, MY + 56, ZK + 730, ZK + 730, ZK + 820, '-y', TAS, TAS, alt=TAS)
YAPILAR['minare'] = (MX - 90, MY - 90, MX + 90, MY + 90, False)

# EV ICLERI (kullanici: profesyonel) -- her esyaya carpisma kutusu
ICERIK = {
    'konak': [('furniture_northafrica_longtable', 3450, 1700, 0, 40, 34), ('furniture_northafrica_woodchair', 3400, 1650, 90, 12, 40),
              ('furniture_northafrica_woodchair', 3500, 1760, 270, 12, 40), ('furniture_northafrica_armoire_tall', 3150, 1900, 0, 26, 90),
              ('prop_barrel_tan', 3750, 1440, 0, 10, 30), ('prop_barrel_tan', 3160, 1450, 0, 10, 30), ('furniture_northafrica_coffeetable', 3250, 1550, 0, 26, 24)],
    'han': [('furniture_northafrica_longtable', 3300, 3300, 90, 40, 34), ('furniture_northafrica_longtable', 3600, 3300, 90, 40, 34),
            ('furniture_northafrica_woodchair', 3360, 3250, 180, 12, 40), ('furniture_northafrica_egyptianchair', 3540, 3360, 0, 14, 40),
            ('prop_crate_dak3', 3150, 3550, 0, 10, 30), ('prop_crate_dak3', 3750, 3550, 0, 10, 30), ('furniture_northafrica_armoire_short', 3150, 3000, 0, 24, 60)],
    'depo': [('prop_crate_dak1', 5300, 1500, 0, 24, 44), ('prop_crate_dak3', 5350, 1500, 20, 24, 44), ('prop_crate_dak5', 5800, 1950, 0, 24, 44),
             ('prop_crate_dak7', 5750, 1500, 10, 24, 44), ('prop_barrel_tan', 5820, 1560, 0, 14, 46), ('prop_barrel_tan', 5820, 1620, 0, 14, 46),
             ('prop_crate_largeshipping1', 5300, 1950, 0, 40, 60)],
    'cami': [('egypt_prop_cloth1', 5480, 3350, 0, 0, 0), ('egypt_prop_cloth2', 5350, 3300, 0, 0, 0), ('prop_barrel_tan', 5700, 3500, 0, 14, 46),
             ('prop_crate_dak3', 5250, 3200, 0, 10, 30)],
}
for oda, liste in ICERIK.items():
    for (m, x, y, yaw, r_, h_) in liste:
        model(m, x, y, BZ, yaw)
        if r_:
            H.kutu(x - r_, y - r_, BZ, x + r_, y + r_, BZ + h_, 'clip', 'clip', alt='clip')
for (ad_, x0_, y0_, x1_, y1_) in (('konak', 3100, 1400, 3800, 2000), ('han', 3100, 2950, 3800, 3600), ('depo', 5200, 1400, 5900, 2050),
                                  ('cami', 5200, 3150, 5750, 3550)):
    isik((x0_ + x1_) / 2, (y0_ + y1_) / 2, BZ + EV_H - 30, 380, .9)
# PAZAR ve sokak esyalari (meydan cevresi, ana sokak)
for (x, y, m, yaw, r_, h_) in ((4050, 2150, 'prop_crate_dak2', 10, 24, 44), (4090, 2140, 'prop_crate_dak4', 40, 24, 44),
                               (4800, 2150, 'prop_barrel_tan', 0, 14, 46), (4830, 2190, 'prop_barrel_tan', 0, 14, 46),
                               (3700, 2400, 'egypt_prop_vase2', 0, 10, 30), (3740, 2420, 'egypt_prop_vase4', 0, 10, 30),
                               (5100, 2300, 'prop_crate_dak6', 20, 24, 44), (4150, 3000, 'prop_crate_smallshipping1', 0, 24, 40),
                               (4950, 3080, 'haycart', 120, 0, 0), (3400, 2350, 'prop_barrel_tan', 0, 14, 46)):
    model(m, x, y, ZK + 1, yaw)
    if r_:
        H.kutu(x - r_, y - r_, ZK + 1, x + r_, y + r_, ZK + 1 + h_, 'clip', 'clip', alt='clip')
    KAYALAR.append((x, y, max(r_, 40)))

# FLAK 88 yerleri (ent_kasrelbab kullanir) ve siper kum torbalari
FLAKLAR = [(4400, 2450, 200), (4550, 3420, 160), (5720, 2860, 30)]
for (fx_, fy_, yaw_) in FLAKLAR:
    pass                                     # kullanici: kare gorunmez duvar olmasin -- flak modelinin kendi carpismasi
for (fx_, fy_, yaw_) in FLAKLAR:
    for k_ in range(6):
        a_ = math.radians(k_ * 60 + 15)
        model('military_sandbag_desert_curvedsection', fx_ + math.cos(a_) * 260, fy_ + math.sin(a_) * 260, ZK + 1,
              (k_ * 60 + 15 + 90) % 360)
    YAPILAR['flak_%d' % fx_] = (fx_ - 150, fy_ - 150, fx_ + 150, fy_ + 150, False)

# kasaba ici dekor: tenteler yerine varil/sandik obekleri, palmiyeler, araba
for (x, y, m) in ((3000, 1350, 'prop_crate_dak3'), (3040, 1330, 'prop_crate_dak5'), (6000, 1330, 'prop_barrel_tan'),
                  (6000, 1380, 'prop_barrel_tan'), (3880, 3720, 'prop_crate_dak7'), (4950, 1300, 'prop_crate_dak1'),
                  (3020, 3700, 'egypt_prop_vase3'), (5950, 3700, 'egypt_prop_vase2'), (4000, 2050, 'egypt_prop_vase4')):
    model(m, x, y, ZK + 1, random.Random(int(x + y)).randint(0, 359))
    H.kutu(x - 20, y - 20, ZK + 1, x + 20, y + 20, ZK + 42, 'clip', 'clip', alt='clip')
    KAYALAR.append((x, y, 26))
for (x, y) in ((4100, 2250), (4800, 2200), (4650, 2850), (3900, 2800)):
    model(random.Random(x).choice(('tree_desertpalm01', 'tree_desertpalm02')), x, y, ZK + 1, random.Random(y).randint(0, 359))
    KAYALAR.append((x, y, 30))
model('haycart', 4700, 1950, ZK + 1, 30)
KAYALAR.append((4700, 1950, 90))
for (x, y, yaw) in ((3950, 2450, 90), (4870, 2560, 90)):              # meydan sokak barikatlari
    model('military_sandbag_desert_longsection', x, y, ZK + 1, yaw)

# =========================================================================
# KULUBE (gozetleme): masa + telsiz; disarida kum torbasi, varil
# =========================================================================
kx0, ky0, kx1, ky1 = KULUBE
kutu6(kx0 - 200, ky0 - 200, ZK - 30, kx1 + 200, ky1 + 200, ZK + 11, {'*': TAS, '+z': KUM})
_dis_yedek = DIS
DIS = DIS3
ev('kulube', kx0, ky0, kx1, ky1, ZK + 13, EV_H, {'g': [('kapi', -1800)], 'b': [('pen', -1200)], 'd': [('pen', -1200)],
                                                 'k': [('pen', -1860)]})
DIS = _dis_yedek
model('furniture_northafrica_longtable', -1760, -1150, ZK + 13, 0)
H.kutu(-1800, -1185, ZK + 13, -1720, -1115, ZK + 47, 'clip', 'clip', alt='clip')
TELSIZ = (-1760, -1150, ZK + 13 + 33)
H.ent('script_model', model='xmodel/military_german_fieldradio_green', origin=TELSIZ, angles=(0, 270, 0), targetname='telsiz',
      target='telsiz_tetik')
_tl = []
H.kutu(TELSIZ[0] - 60, TELSIZ[1] - 60, ZK + 13, TELSIZ[0] + 60, TELSIZ[1] + 60, ZK + 93, 'trigger', 'trigger', alt='trigger', hedef=_tl)
H.ent('trigger_use', brushlar=_tl, targetname='telsiz_tetik')
for (x, y, m, yaw) in ((-1800, -1480, 'military_sandbag_desert_longsection', 0), (-2050, -1250, 'military_sandbag_desert_curvedsection', 270),
                       (-1580, -1000, 'prop_barrel_tan', 0), (-1560, -960, 'prop_barrel_tan', 0), (-2000, -1000, 'prop_crate_dak2', 20)):
    model(m, x, y, ZK + 11, yaw)
model('tree_desertpalm02', -1500, -1500, None, 40)
KAYALAR.append((-1500, -1500, 30))

# =========================================================================
# BASLANGIC: tek agac + sik cali obegi (oyuncu gizlenir)
# =========================================================================
bx, by = CALI_M
model('tree_desertbushy', bx - 60, by - 90, None, 30)
_rc = random.Random(4)
for k_ in range(16):
    a_ = math.radians(k_ * 22.5 + _rc.uniform(-8, 8))
    r_ = _rc.uniform(70, 230)
    model(_rc.choice(('brush_desertshrubgroup01', 'brush_desertshrubgraytall', 'brush_desertshrubbrowntall', 'brush_egypt_desert_2')),
          bx + math.cos(a_) * r_, by + math.sin(a_) * r_, None, _rc.randint(0, 359), kayit=False)
for (dx, dy) in ((-180, 120), (200, 140), (40, 230)):
    model('brush_desertgreenfanshrub', bx + dx, by + dy, None, _rc.randint(0, 359), kayit=False)
H.ent('info_player_start', origin=(BASLANGIC[0], BASLANGIC[1], round(yukseklik(*BASLANGIC) + 8, 1)), angles=(0, 80, 0))

# =========================================================================
# DEKOR: palmiye vahalari, kayalar, yanmis araclar, calilar (rotalardan uzak)
# =========================================================================
CR_DURAK = [(1650, 1650), (1550, 2250), (1650, 2850), (1800, 3450), (1900, 1100)]
def rota_mes(x, y):
    en = giris_mes(x, y)
    for (cx, cy) in CR_DURAK:
        en = min(en, math.hypot(x - cx, y - cy))
    en = min(en, _seg(x, y, TAKVIYE[-1], (1600, 2300)))
    return en
rnd = random.Random(8)
for (x, y, m, yaw) in ((-500, -2400, 'vehicle_opel_blitz_desert_d_static', 40), (2200, -900, 'vehicle_crusader2_d_static', 120),
                       (-4200, 400, 'vehicle_panzer_ii_destroyed_static', 300), (6600, -3200, 'vehicle_opel_blitz_desert_d_static', 200)):
    if rota_mes(x, y) > 400:
        model(m, x, y, None, yaw)
        KAYALAR.append((x, y, 190))
for i in range(40):
    x, y = rnd.uniform(-8000, 8000), rnd.uniform(-6400, 6400)
    if icinde(x, y) and kasaba_mes(x, y) > 900 and rota_mes(x, y) > 450 and kenar_mes(x, y) > 300 and \
       math.hypot(x - bx, y - by) > 700 and math.hypot(x - KULUBE_M[0], y - KULUBE_M[1]) > 600:
        kaya(x, y, rnd.randint(60, 150), rnd.randint(40, 120), 700 + i)
for (vx, vy) in ((-2600, -900), (1500, 4300), (-5600, 2600), (6900, 4300), (2800, -4200),
                 (3600, -5200), (5300, -3600), (7400, -2600), (7600, 600), (6200, -5200), (8000, 3000)):           # vahalar
    for k_ in range(6):
        x, y = vx + rnd.randint(-380, 380), vy + rnd.randint(-380, 380)
        if icinde(x, y) and rota_mes(x, y) > 350 and kasaba_mes(x, y) > 500:
            model(rnd.choice(('tree_desertpalm01', 'tree_desertpalm02', 'tree_desertpalm03', 'tree_desertpalmgroup')), x, y, None, rnd.randint(0, 359))
            KAYALAR.append((x, y, 34))
for i in range(220):
    x, y = rnd.uniform(-8200, 8200), rnd.uniform(-6600, 6600)
    if not icinde(x, y) or kasaba_mes(x, y) < 500 or rota_mes(x, y) < 320 or kenar_mes(x, y) < 200:
        continue
    if any(math.hypot(x - a, y - b) < r + 100 for (a, b, r) in KAYALAR):
        continue
    if math.hypot(x - bx, y - by) < 600:
        continue
    model(rnd.choice(('tree_desertpalm01', 'tree_desertpalm02', 'tree_desertbushy', 'tree_desertpalmgroup')), x, y, None, rnd.randint(0, 359))
    KAYALAR.append((x, y, 34))
CALI = ['brush_desertshrubbrownmid', 'brush_desertshrubgraymid', 'brush_desertshrubgroup01', 'brush_egypt_desert_1',
        'brush_egypt_desert_2', 'brush_desertspikeyshrub', 'brush_desertshrubbrowntall']
for x in range(SX0 + 300, SX1 - 299, 480):
    for y in range(SY0 + 300, SY1 - 299, 480):
        x2, y2 = x + rnd.randint(-180, 180), y + rnd.randint(-180, 180)
        if kasaba_mes(x2, y2) < 400 or yol_mesafe(x2, y2) < 220:
            continue
        if rnd.random() < (0.35 if icinde(x2, y2) else 0.55):
            model(rnd.choice(CALI), x2, y2, None, rnd.randint(0, 359), kayit=False)
for x in range(SX0 + 500, SX1 - 499, 1000):                           # ufuk palmiyeleri
    for y in range(SY0 + 500, SY1 - 499, 1000):
        x2, y2 = x + rnd.randint(-300, 300), y + rnd.randint(-300, 300)
        if not icinde(x2, y2) and kenar_mes(x2, y2) > 400 and giris_mes(x2, y2) > 600 and rnd.random() < 0.3:
            model(rnd.choice(('tree_desertpalm01', 'tree_desertpalmgroup')), x2, y2, None, rnd.randint(0, 359), kayit=False)

# KULLANICI: harita disi cevre daha profesyonel -- sirtlarda kaya ciktilari, kuru agaclar, cali kumeleri
_dr = random.Random(91)
for x in range(SX0 + 400, SX1 - 399, 620):
    for y in range(SY0 + 400, SY1 - 399, 620):
        x2, y2 = x + _dr.randint(-240, 240), y + _dr.randint(-240, 240)
        if icinde(x2, y2) or giris_mes(x2, y2) < 420:
            continue
        o_ = kenar_mes(x2, y2)
        r_ = _dr.random()
        if o_ > 250 and r_ < 0.30:
            kaya(x2, y2, _dr.randint(110, 260), _dr.randint(70, 220), 9000 + x // 7 + y // 11)
            for c_ in range(3):
                model(_dr.choice(CALI), x2 + _dr.uniform(-260, 260), y2 + _dr.uniform(-260, 260), None, _dr.randint(0, 359), kayit=False)
        elif r_ < 0.48:
            model(_dr.choice(('tree_desertbushy', 'tree_desertpalm01', 'tree_desertpalmgroup', 'tree_desertpalm02')), x2, y2, None, _dr.randint(0, 359), kayit=False)
            model(_dr.choice(CALI), x2 + _dr.uniform(-140, 140), y2 + _dr.uniform(-140, 140), None, _dr.randint(0, 359), kayit=False)
        elif r_ < 0.75:
            for c_ in range(2):
                model(_dr.choice(CALI), x2 + _dr.uniform(-200, 200), y2 + _dr.uniform(-200, 200), None, _dr.randint(0, 359), kayit=False)

# KULLANICI: cevre bos durmasin -- yol kenari palmiye siralari, kapi onu ordugah, patika
def yol_kenari(hat, aralik, yan, olas):
    for i in range(len(hat) - 1):
        (ax, ay), (bx, by) = hat[i][:2], hat[i + 1][:2]
        L = math.hypot(bx - ax, by - ay)
        if L < 1:
            continue
        ux, uy = (bx - ax) / L, (by - ay) / L
        for k in range(int(L // aralik)):
            if rnd.random() > olas:
                continue
            m_ = k * aralik + rnd.uniform(-60, 60)
            for sgn in (-1, 1):
                x = ax + ux * m_ - uy * sgn * (yan + rnd.uniform(-40, 60))
                y = ay + uy * m_ + ux * sgn * (yan + rnd.uniform(-40, 60))
                if not icinde(x, y) or kasaba_mes(x, y) < 350 or math.hypot(x - bx_, y - by_) < 500:
                    continue
                if any(math.hypot(x - a, y - b) < r + 60 for (a, b, r) in KAYALAR):
                    continue
                model(rnd.choice(('tree_desertpalm01', 'tree_desertpalm02', 'tree_desertpalm03')), x, y, None, rnd.randint(0, 359))
                KAYALAR.append((x, y, 30))
                model(rnd.choice(CALI), x + rnd.uniform(-90, 90), y + rnd.uniform(-90, 90), None, rnd.randint(0, 359), kayit=False)
bx_, by_ = CALI_M
yol_kenari(PATIKA, 420, 170, 0.8)
yol_kenari(KONVOY, 700, 260, 0.6)
yol_kenari(CIKIS, 650, 240, 0.6)
yol_kenari(GUNEY, 560, 230, 0.75)
_kr = random.Random(77)
for ad_ in ('konvoy', 'takviye', 'cikis', 'guney'):
    hat_, gen_ = YOLLAR[ad_]
    g2_ = (gen_ or 220) / 2.0
    for i in range(len(hat_) - 1):
        (ax, ay), (bx2, by2) = hat_[i], hat_[i + 1]
        L = math.hypot(bx2 - ax, by2 - ay)
        ux, uy = (bx2 - ax) / L, (by2 - ay) / L
        for k in range(int(L // 380)):
            m_ = k * 380 + _kr.uniform(-80, 80)
            for sgn in (-1, 1):
                d_ = g2_ + _kr.uniform(250, 420)
                x = ax + ux * m_ - uy * sgn * d_
                y = ay + uy * m_ + ux * sgn * d_
                if icinde(x, y) and kenar_mes(x, y) > 150:
                    continue                                   # yalniz sinir disi kanyon
                if giris_mes(x, y) < g2_ + 200 or not (SX0 + 200 < x < SX1 - 200 and SY0 + 200 < y < SY1 - 200):
                    continue
                if _kr.random() < 0.55:
                    kaya(x, y, _kr.randint(90, 200), _kr.randint(60, 170), 5000 + i * 100 + k * 2 + (sgn > 0))
                for c_ in range(2):
                    model(_kr.choice(CALI), x + _kr.uniform(-160, 160), y + _kr.uniform(-160, 160), None, _kr.randint(0, 359), kayit=False)
# sur kapisi onu: Alman nobet yeri (kum torbalari, sandiklar, yanmis kamyon)
for (x, y, m, yaw) in ((2550, 2250, 'military_sandbag_desert_longsection', 90), (2550, 2760, 'military_sandbag_desert_longsection', 90),
                       (2420, 2150, 'prop_crate_dak4', 10), (2450, 2110, 'prop_crate_dak6', 40), (2400, 2880, 'prop_barrel_tan', 0),
                       (2440, 2900, 'prop_barrel_tan', 0), (2150, 3150, 'haycart_destroyed', 70)):
    model(m, x, y, (ZK + 1) if kasaba_mes(x, y) < 290 else None, yaw)
    KAYALAR.append((x, y, 40 if not m.startswith('military') else 80))
model('vehicle_opel_blitz_desert_d_static', 2250, 1650, None, 210)
KAYALAR.append((2250, 1650, 190))

H.ent('misc_turret', model='xmodel/weapon_mg42', weaponinfo='mg42_bipod_stand',
      origin=(SX0 + 400, SY0 + 400, round(yukseklik(SX0 + 400, SY0 + 400), 1)), angles=(0, 0, 0))

def dogrula():
    var = set()
    for p in glob.glob(os.path.join(KOK, 'main', '*.iwd')):
        for n_ in zipfile.ZipFile(p).namelist():
            var.add(n_.lower())
    eksik = [m for m in sorted(H.malzemeler) if m not in ('caulk', 'clip_player', 'clip', 'trigger', 'origin', 'ladder')
             and 'materials/' + m.lower() not in var]
    modeller = sorted({d['model'] for d, _ in H.ents if 'model' in d and d['classname'] in ('misc_model', 'script_model')})
    eksik_m = [m for m in modeller if m.lower() not in var]
    return eksik, eksik_m

def sinir_gsc():
    o = ['// kasrelbab_sinir.gsc -- gen_kasrelbab.py URETIR, elle duzenlemeyin.', 'cokgen()', '{', '\tp = [];']
    for (x, y) in POLI:
        o.append('\tp[p.size] = (%d, %d, 0);' % (round(x), round(y)))
    o += ['\treturn p;', '}', '']
    open(os.path.join(KOK, 'main', 'maps', HARITA + '_sinir.gsc'), 'w', newline='\r\n').write('\n'.join(o) + '\n')
sinir_gsc()

import ent_kasrelbab
ent_kasrelbab.yerlestir(sys.modules[__name__])

if __name__ == '__main__':
    eksik, eksik_m = dogrula()
    if eksik or eksik_m:
        raise SystemExit('EKSIK VARLIK! malzeme: %s model: %s' % (eksik, eksik_m))
    r = H.yaz(os.path.join(KOK, 'map_source', HARITA + '.map'))
    print('dunya brush/mesh: %(dunya_brush)d  entity: %(entity)d  bayt: %(bayt)d' % r)
    print('misc_model: %d  kaya: %d' % (sum(1 for d, _ in H.ents if d['classname'] == 'misc_model'), len(KAYALAR)))
    print('konvoy yolu: %d, takviye yolu: %d, cikis yolu: %d' % (hat_uzunluk(KONVOY), hat_uzunluk(TAKVIYE), hat_uzunluk(CIKIS)))
