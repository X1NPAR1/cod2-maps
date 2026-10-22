# -*- coding: utf-8 -*-
"""
gen_kumtepe.py -- CoD2 SP 'kumtepe' (Operation Sandstorm, El Alamein, Ekim 1942).

Duzen (dunya birimi, kuzey = +Y):
  Orta   : 4 binali kerpic koy + avlu + kuyu (ZK duz zemin, r ~1100)
             KD 'kapali'   : kapali bina (kapak/kapilar kapali)
             KB 'ikikat'   : iki katli, yalniz zemin kat girilir (ust kat kapakli)
             GB 'cati'     : tek kat, duz cati; dogu duvarinda EL MERDIVENI (ladder)
             GD 'ev'       : tek kat, girilebilir
  Dogu   : konvoy yolu (harita disindaki kum tepesinin arkasindan doner) --
           Crusader'lar ve 20 Ingiliz de buradan gelir
  Bati   : 4 Panzer seridi (harita disindan)
  K/G/B  : Alman dalgalari tepelerin arkasindan
Skill kurallari: uc katman (gok kutusu, sirt halkasi, clip_player cokgeni); her
yol harita disinda kivrilir; kapi 64x88, pencere denizligi 46 ust 88 '+' kasa;
esyalara clip; dugumler >= 40 aralik; malzeme/model iwd'de dogrulanir.
"""
import os, sys, math, random, zipfile, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kmap import Harita, OLCEK

KOK = r'F:\Activision\Call of Duty 2'
HARITA = 'kumtepe'

# ---------------------------------------------------------------- malzemeler (onizlendi: kum_atlas.png)
KUM = 'egypt_roughdirt_04'
YOL = 'egypt_roughdirt_05'
KAYA = 'egypt_rock_1'
DIS = 'egypt_plaster_exteriorwall03'
DIS2 = 'egypt_plaster_exteriorwall02'
IC = 'egypt_plaster_interiorwall2'
TABAN = 'egypt_concrete_floor2'
CATI = 'egypt_gravel_roof1'
TAS = 'egypt_sandstone_generic1'
TRIM = 'egypt_wood_generic1'
KIRIS = 'egypt_wood_beam'
KAPI_M = 'egypt_wood_door2'
KAPAK = 'egypt_wood_shutters1'
TAVAN = 'egypt_wood_ceiling1'
GOK = 'sky_elalamein'
CAULK = 'caulk'
SINIR = 'clip_player'
for m_, o_ in ((KUM, (512, 512)), (YOL, (256, 256)), (DIS, (256, 256)), (DIS2, (256, 256)), (IC, (256, 256)),
               (TABAN, (256, 256)), (CATI, (256, 256)), (TAS, (512, 256)), (TRIM, (64, 128)), (KIRIS, (128, 128)),
               (TAVAN, (256, 256)), (KAYA, (256, 256))):
    OLCEK[m_] = o_

H = Harita()
H.ws.update({'_color': '1 .80 .62', 'ambient': '.26', 'sunlight': '1.25',
             'sundirection': '-16 -115 0', 'sundiffusecolor': '1 .78 .58',
             'suncolor': '1 .74 .48', 'diffusefraction': '.55',
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

# ---------------------------------------------------------------- sinir (oynanabilir cokgen)
SX0, SX1, SY0, SY1 = -7168, 7168, -6144, 6144            # gok kutusu (128 kati)
ZTAVAN = 3072
POLI = [(-5600, -2400), (-5300, -4100), (-3600, -4800), (-1000, -5000), (1800, -4900), (4200, -4500),
        (5500, -3300), (5700, -800), (5500, 2000), (4400, 4200), (1800, 4900), (-1200, 5000),
        (-3800, 4600), (-5300, 3500), (-5700, 600)]

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

# ---------------------------------------------------------------- koy ve yollar
ZK = 40.0
KOY_R = 1150
# KONVOY: doguda harita disindan (tepenin arkasindan kivrilir), koyun dogusunda durur
KONVOY = [(5600, -5700), (6300, -5000), (6600, -4000), (6450, -3100), (6050, -2350), (5400, -1700),
          (4400, -1100), (3300, -650), (2400, -200), (1750, 350), (1250, 800), (782, 1071)]
# PANZER SERITLERI: batidan, harita disindan
PANZER_VADI = [(-6300, 4400), (-6650, 3300), (-6500, 2200), (-6000, 1300), (-5300, 700)]
PANZER = [PANZER_VADI + [(-4600, 0.5 * y0 + 400), (-3200, y0 * 0.85), (xs_, y0 * 0.6)]
          for (y0, xs_) in ((-1500, -2350), (-500, -1650), (500, -2050), (1500, -1500))]
YOLLAR = {'konvoy': (KONVOY, 260)}
for i_, h_ in enumerate(PANZER):
    YOLLAR['panzer%d' % (i_ + 1)] = (h_, 0)            # gorunur yol yok (kum)

def koy_mes(x, y):
    return math.hypot(x, y)

def yol_mes_ham(x, y, ad='konvoy'):
    h, _ = YOLLAR[ad]
    return min(_seg(x, y, h[i], h[i + 1]) for i in range(len(h) - 1))

def giris_mes(x, y):
    """harita disina uzanan araç koridorlarina uzaklik (sirt orada alcak)."""
    return min(yol_mes_ham(x, y, ad) for ad in YOLLAR)

TEPE = [((-2600, 3200), 900, 230), ((2600, 3300), 1000, 260), ((-2900, -3300), 950, 220), ((2800, -3500), 900, 240),
        ((-4300, 400), 700, 160), ((4100, 1600), 800, 190), ((900, 3800), 600, 150), ((-900, -3900), 650, 170),
        ((4300, -2600), 700, 210), ((-4200, -2200), 600, 140), ((-4200, 2600), 650, 170), ((1900, 2000), 500, 90),
        ((-1900, -1900), 450, 70), ((-2000, 1700), 450, 80), ((2000, -2000), 500, 90),
        # kullanici: dalga dogus yerleri gorunuyordu -> onlerine tumsek
        ((-1500, 3300), 650, 230), ((200, 3450), 650, 240), ((1900, 3150), 600, 220), ((-2900, 3000), 600, 220),
        ((-3800, 1000), 520, 190), ((-3850, -800), 520, 190), ((-3300, -2500), 600, 210), ((-1500, -3400), 650, 230),
        ((500, -3500), 650, 240), ((2000, -3200), 600, 220), ((3000, 2500), 600, 200)]

def zemin_ham(x, y):
    z = 0.0
    for ((cx, cy), r, hh) in TEPE:
        z += hh * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / float(r * r))
    z += 34 * math.sin(x / 1100.0 + 1.3) * math.cos(y / 1300.0) + 10 * math.sin((x + y) / 520.0)
    if not icinde(x, y):
        o = kenar_mes(x, y)
        dis = 220 + 900 * ss(0, 1150, o) + 180 * math.sin(x / 1500.0 + 0.7) * math.cos(y / 1800.0) * ss(200, 900, o)
        z += dis * (0.10 + 0.90 * ss(200, 560, giris_mes(x, y)))
    else:
        z += 120 * ss(700, 0, kenar_mes(x, y))
    km = koy_mes(x, y)
    if km < KOY_R + 500:
        z = lerp(ZK, z, ss(KOY_R, KOY_R + 500, km))
    return z

YOL_HAT = {}
for ad, (pts, gen) in YOLLAR.items():
    YOL_HAT[ad] = ([(x, y, float(zemin_ham(x, y))) for (x, y) in pts], gen)

def yol_bilgi(x, y):
    en = (1e9, 0.0, 0)
    for ad, (hat, gen) in YOL_HAT.items():
        g = gen if gen else 200
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
    d, _, _ = yol_bilgi(x, y)
    return d

def yukseklik(x, y):
    z = zemin_ham(x, y)
    d, yz, yg = yol_bilgi(x, y)
    if d < yg + 220:
        z = lerp(z, yz, ss(yg + 220, yg + 30, d))
    return z

# ---------------------------------------------------------------- gokyuzu + arazi
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
        H.mesh([[(xs[i], ys[j], zh(xs[i], ys[j])) for j in range(j0, j1 + 1)] for i in range(i0, i1 + 1)],
               KUM, doku=1.0)

def yol_mesh(hat, gen):
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
        satir.append([(round(px + qx * w, 2), round(py + qy * w, 2), round(yukseklik(px + qx * w, py + qy * w) + 2, 2))
                      for w in (-gen / 2.0, 0, gen / 2.0)])
    for s0 in range(0, len(satir) - 1, 23):
        parca = satir[s0:s0 + 24]
        if len(parca) > 1:
            H.mesh(parca, YOL, doku=2.0, detay=True)
yol_mesh(*YOL_HAT['konvoy'])

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

# ---------------------------------------------------------------- gorunmez sinir
# Konvoy gecidi: derlemede +4000 (oyuncu kamyonla girer), GSC inince indirir.
SINIR_KAPI = []
ENGEL_KAYDIR_S = 4000
for i in range(len(POLI)):
    a, b = POLI[i], POLI[(i + 1) % len(POLI)]
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(L // 48))
    for k in range(n):
        p0 = (lerp(a[0], b[0], k / float(n)), lerp(a[1], b[1], k / float(n)))
        p1 = (lerp(a[0], b[0], (k + 1) / float(n)), lerp(a[1], b[1], (k + 1) / float(n)))
        mx, my = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0
        if yol_mes_ham(mx, my, 'konvoy') < 320:
            dikey_levha(p0, p1, -600 + ENGEL_KAYDIR_S, 2400 + ENGEL_KAYDIR_S, SINIR, hedef=SINIR_KAPI)
        else:
            dikey_levha(p0, p1, -600, 2400, SINIR)
H.ent('script_brushmodel', brushlar=SINIR_KAPI, targetname='sinir_kapi_konvoy')

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

# =========================================================================
# KOY: avlu (brush taban, ZK+1 -- yol agi dersi: mesh -> 16'lik brush tabana bag yok)
# =========================================================================
kutu6(-1000, -1000, ZK - 40, 1000, 1000, ZK + 1, {'*': TAS, '+z': KUM})
BZ = ZK + 3                                     # avlu ZK+1; esik 2 (rampa gerekmez)
EV_H = 128
# KD: kapali bina
KOSE = []
KB_ = (380, 500, 660, 760)                       # kose bolgesi (bati yonu, sol = kuzey); kullanici: tamamen yikilsin
BOLGE[0] = (KB_[0] - 8, KB_[1], KB_[2], KB_[3] + 8, KOSE)
ev('kapali', 380, 330, 860, 760, BZ, EV_H,
   {'g': [('kapali', 620), ('pen', 470), ('pen', 770)], 'b': [('pen', 545)], 'd': [('pen', 545)], 'k': [('pen', 620)]},
   girilir=False, cati=False)
# L bicimli duz cati: kose parcasi ayri
_z1 = BZ + EV_H
for (a_, b_, c_, d_) in ((380 - 8, 330 - 8, 860 + 8, KB_[1]), (KB_[2], KB_[1], 860 + 8, 760 + 8), (380 - 8, KB_[1], KB_[2], 760 + 8)):
    kutu6(a_, b_, _z1, c_, d_, _z1 + 14, {'*': DIS, '+z': CATI, '-z': TAVAN})
_zc = _z1 + 14
for (a_, b_, c_, d_) in ((380 - 8, 330 - 8, 860 + 8, 330 + 4), (860 - 4, 330 + 4, 860 + 8, 760 - 4),
                         (KB_[2], 760 - 4, 860 + 8, 760 + 8), (380 - 8, 760 - 4, KB_[2], 760 + 8),
                         (380 - 8, 330 + 4, 380 + 4, KB_[1]), (380 - 8, KB_[1], 380 + 4, 760 - 4)):
    kutu6(a_, b_, _zc, c_, d_, _zc + 32, {'*': DIS, '+z': TAS})
BOLGE[0] = None
KDX, KDZ = -5120, 2048                           # gok kutusu ici, aydinlik, dugumsuz (512 katlari)
H.ent('script_brushmodel', brushlar=[_kaydir(b, KDX, KDZ) for b in KOSE], targetname='kapali_kose')
# KB: iki katli -- zemin girilir; ust kat kapali (kepenkli), duz cati
ev('ikikat', -900, 300, -360, 820, BZ, EV_H,
   {'g': [('kapi', -630), ('pen', -800), ('pen', -460)], 'd': [('kapi', 560), ('pen', 420), ('pen', 720)],
    'b': [('pen', 450), ('pen', 680)], 'k': [('pen', -760), ('pen', -500)]}, cati=False)
UZ = BZ + EV_H + 14
# Olculdu: yerinde derlenen brushmodel evin icini yol agindan kopariyor; gok kutusu
# disinda derlenen ise isiksiz kaliyor -> gok kutusu ICINDE, aydinlik ve dugumsuz bir
# yerde (512 katlari), DOGRUDAN orada uretilir (oturtulan dokular orada hesaplanir);
# GSC baslangicta (UDX, UDZ) kadar geri indirir.
UDX, UDZ = -5120, 2048
def kayik(liste):
    AKTIF_HEDEF[0] = liste
# 1) ust kat BATI yarisi (ilk atista yikilir)
UST_BATI = []
kayik(UST_BATI)
ev('ikikat_ust_b', -900 + UDX, 300, -630 + UDX, 820, UZ + UDZ, EV_H,
   {'g': [('pen', -800)], 'b': [('pen', 450), ('pen', 680)], 'k': [('pen', -760)]}, girilir=False, taban=False)
kayik(None)
H.ent('script_brushmodel', brushlar=UST_BATI, targetname='ust_bati')
# 2) ara doseme + ust kat DOGU yarisi (ikinci atista evle birlikte coker)
UST_DOGU = []
kayik(UST_DOGU)
kutu6(-900 + UDX, 300, BZ + EV_H + UDZ, -360 + UDX, 820, UZ + UDZ, {'*': DIS, '-z': TAVAN, '+z': TABAN})
ev('ikikat_ust_d', -630 + UDX, 300, -360 + UDX, 820, UZ + UDZ, EV_H,
   {'g': [('pen', -460)], 'd': [('pen', 420), ('pen', 720)], 'k': [('pen', -500)]}, girilir=False, taban=False)
kayik(None)
H.ent('script_brushmodel', brushlar=UST_DOGU, targetname='ust_dogu')

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

# 3) ilk atistan sonra: bati yarinin dosemedeki kirik duvar diplari (ucgen uclu)
_r = random.Random(33)
_yk = []
kirik_duvar('x', -900 + UDX, -630 + UDX, 300, 316, UZ + UDZ, _r, _yk, 60)
kirik_duvar('x', -900 + UDX, -630 + UDX, 804, 820, UZ + UDZ, _r, _yk, 60)
kirik_duvar('y', 316, 804, -900 + UDX, -884 + UDX, UZ + UDZ, _r, _yk, 70)
for i in range(4):
    x_ = _r.uniform(-880, -760) + UDX; y_ = _r.uniform(340, 740)
    kutu6(x_, y_, UZ + UDZ, x_ + _r.randint(120, 200), y_ + 12, UZ + UDZ + 12, {'*': KIRIS}, hedef=_yk)
moloz_yigini(-760 + UDX, 560, UZ + UDZ, 70, 34, _r, _yk)
H.ent('script_brushmodel', brushlar=_yk, targetname='ust_bati_yikik')
# 4) HARABE (ikinci atis): zemin duvarlarinin ustunde ucgen kirik uclar, icte moloz
# yiginlari, yanik kirisler; kapilar molozla kapanir (gorunmez klip: icine girilmez)
_hb = []
ZT = BZ + EV_H + UDZ
kirik_duvar('x', -900 + UDX, -360 + UDX, 300, 316, ZT, _r, _hb, 46)
kirik_duvar('x', -900 + UDX, -360 + UDX, 804, 820, ZT, _r, _hb, 46)
kirik_duvar('y', 316, 804, -900 + UDX, -884 + UDX, ZT, _r, _hb, 46)
kirik_duvar('y', 316, 804, -376 + UDX, -360 + UDX, ZT, _r, _hb, 46)
for (cx, cy, r_, h_) in ((-760, 420, 110, 90), (-520, 470, 120, 110), (-700, 680, 120, 100), (-480, 700, 100, 80),
                         (-630, 560, 90, 120)):
    moloz_yigini(cx + UDX, cy, BZ + UDZ, r_, h_, _r, _hb)
for i in range(6):
    x_ = _r.uniform(-860, -560) + UDX; y_ = _r.uniform(340, 760)
    H.kama(x_, y_, x_ + _r.randint(160, 260), y_ + 14, BZ + UDZ, BZ + UDZ + _r.randint(10, 40), BZ + UDZ + _r.randint(60, 120),
           '+x', KIRIS, KIRIS, alt=KIRIS, hedef=_hb)
for (x_, y_, dx_, dy_) in ((-630, 300, 0, -1), (-360, 560, 1, 0)):        # kapi molozu + klip
    moloz_yigini(x_ - dx_ * 70 + UDX, y_ - dy_ * 70, BZ + UDZ, 70, 70, _r, _hb)      # kullanici: icerde
    H.kutu(x_ - 40 + UDX, y_ - 40, BZ + UDZ, x_ + 40 + UDX, y_ + 40, BZ + EV_H + UDZ, 'clip', 'clip', alt='clip', hedef=_hb)
H.ent('script_brushmodel', brushlar=_hb, targetname='ikikat_harabe')
_kh = []
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
# kuzey duvar: x 660 (saglam, tam boy) -> 380 (kose, alcak); bati duvar: y 500 -> 760
zikzak_duvar('x', KB_[2] + KDX, 380 + KDX, 744, 760, BZ + KDZ, EV_H - 6, 18, _r, _kh)
zikzak_duvar('y', KB_[1], 744, 380 + KDX, 396 + KDX, BZ + KDZ, EV_H - 6, 18, _r, _kh)
moloz_yigini(460 + KDX, 680, BZ + KDZ, 130, 80, _r, _kh)
moloz_yigini(580 + KDX, 600, BZ + KDZ, 90, 52, _r, _kh)
moloz_yigini(420 + KDX, 560, BZ + KDZ, 70, 40, _r, _kh)
H.kama(400 + KDX, 590, 640 + KDX, 606, BZ + KDZ, BZ + KDZ + 20, BZ + KDZ + 120, '+x', KIRIS, KIRIS, alt=KIRIS, hedef=_kh)
H.kama(560 + KDX, 520, 576 + KDX, 720, BZ + KDZ, BZ + KDZ + 30, BZ + KDZ + 110, '-y', KIRIS, KIRIS, alt=KIRIS, hedef=_kh)
H.kama(420 + KDX, 650, 600 + KDX, 700, BZ + KDZ, BZ + KDZ + 30, BZ + KDZ + 96, '-x', DIS, CATI, alt=DIS, hedef=_kh)   # devrik cati parcasi
# kirik cati kenari (saglam catinin yikik ucu): asagi sarkan parca
H.kama(KB_[2] - 60 + KDX, KB_[1] + 20, KB_[2] + KDX, 760, BZ + EV_H - 70 + KDZ, BZ + EV_H - 60 + KDZ, BZ + EV_H + 14 + KDZ, '+x', CATI, DIS, alt=TAVAN, hedef=_kh)
H.kutu(380 + KDX, 744, BZ + KDZ, KB_[2] + KDX, 760, BZ + KDZ + 220, 'clip', 'clip', alt='clip', hedef=_kh)
H.kutu(380 + KDX, KB_[1], BZ + KDZ, 396 + KDX, 760, BZ + KDZ + 220, 'clip', 'clip', alt='clip', hedef=_kh)
H.ent('script_brushmodel', brushlar=_kh, targetname='kapali_kose_harabe')
YAPILAR['ikikat'] = (-900, 300, -360, 820, True)
# GB: duz catili, catisina el merdiveni (dogu duvari); ici kapali
CATI_EV = (-860, -800, -400, -380)
CZ = ev('cati', CATI_EV[0], CATI_EV[1], CATI_EV[2], CATI_EV[3], BZ, EV_H,
        {'g': [('kapali', -630), ('pen', -770), ('pen', -490)], 'b': [('pen', -590)], 'k': [('pen', -630)],
         'd': [('pen', -700)]}, girilir=False, bosluk=-560)
# GD: girilebilir tek kat
ev('ev', 380, -820, 880, -380, BZ, EV_H,
   {'k': [('kapi', 520), ('pen', 760)], 'b': [('kapi', -520), ('pen', -700)], 'g': [('pen', 500), ('pen', 760)],
    'd': [('pen', -600)]})

# kullanici: MG'ler havada duruyordu -> ayaklar parapet ustunde (parapet ust yuzu CZ+32)
for (x_, y_, yaw_, ad_) in ((CATI_EV[2] + 2, -470, 0, 'dogu'), (CATI_EV[0] - 2, -620, 180, 'bati')):
    H.ent('misc_turret', model='xmodel/weapon_mg42', weaponinfo='mg42_bipod_stand', targetname='cati_mg',
          script_noteworthy=ad_, origin=(x_, y_, CZ + 32), angles=(0, yaw_, 0))
    gx_ = x_ - math.cos(math.radians(yaw_)) * 40; gy_ = y_ - math.sin(math.radians(yaw_)) * 40
    H.ent('script_origin', targetname='cati_mg_yer', script_noteworthy=ad_, origin=(round(gx_), round(gy_), CZ + 4))
# EL MERDIVENI: GB binanin dogu duvari, catiya (stok 'ladder' klibi + gorunur dikme/basamak)
LX = CATI_EV[2]                 # dogu dis yuz
LY = -560
lx0, lx1 = LX + 8, LX + 14
for sy in (-18, 14):
    kutu6(lx0, LY + sy, BZ - 4, lx1, LY + sy + 4, CZ + 18, {'*': TRIM}, detay=True)
for zz_ in range(int(BZ) + 14, int(CZ) + 10, 16):
    kutu6(lx0 + 1, LY - 14, zz_, lx1 - 1, LY + 14, zz_ + 3, {'*': TRIM}, detay=True)
H.kutu(lx0, LY - 18, BZ, lx1, LY + 18, CZ + 20, 'ladder', 'ladder', alt='ladder')
# parapette merdiven gecidi (oyuncu catiya adim atar)
MERDIVEN = (LX, LY, CZ)

# AVLU SIPERLERI (kullanici: hem oyuncu hem Ingilizler siper alsin, hep ayni yer olmasin)
for (m, x, y, yaw, r_, h_) in (('vehicle_opel_blitz_desert_static', 150, 660, 0, 0, 0), ('haycart', 300, -160, 70, 0, 0),
                               ('prop_crate_dak4', 480, 296, 10, 26, 44), ('prop_crate_dak2', 535, 292, 40, 26, 44),
                               ('prop_crate_dak6', -320, 60, 0, 26, 44), ('prop_barrel_tan', -350, 110, 0, 16, 46),
                               ('military_sandbag_desert_longsection', 300, -420, 0, 0, 0),
                               ('military_sandbag_desert_curvedsection', -200, 380, 180, 0, 0),
                               ('military_sandbag_desert_longsection', 600, 950, 0, 0, 0),
                               ('military_sandbag_desert_longsection', -620, 950, 0, 0, 0)):
    model(m, x, y, ZK + 1, yaw)
    if r_:
        H.kutu(x - r_, y - r_, ZK + 1, x + r_, y + r_, ZK + 1 + h_, 'clip', 'clip', alt='clip')
# kamyon ve araba carpisma kutulari (yonlu)
def yonlu_klip(x, y, yaw, uz, gen, h):
    c, s_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    pts = [(x + c * a - s_ * b, y + s_ * a + c * b) for (a, b) in ((-uz, -gen), (uz, -gen), (uz, gen), (-uz, gen))]
    z0, z1 = ZK + 1, ZK + 1 + h
    yuz = [((pts[0][0], pts[0][1], z0), (pts[1][0], pts[1][1], z0), (pts[2][0], pts[2][1], z0)),
           ((pts[0][0], pts[0][1], z1), (pts[1][0], pts[1][1], z1), (pts[2][0], pts[2][1], z1))]
    for k in range(4):
        a_, b_ = pts[k], pts[(k + 1) % 4]
        yuz.append(((a_[0], a_[1], z0), (b_[0], b_[1], z0), (a_[0], a_[1], z1)))
    H.konveks(yuz, ['clip'] * 6)
yonlu_klip(150, 660, 0, 150, 52, 110)
yonlu_klip(300, -160, 70, 80, 40, 60)
KAYALAR.append((150, 660, 150))
KAYALAR.append((300, -160, 80))
# KOY SINIRI (kullanici): kamyondan inince koyden cikilmaz -- koyun ~30 m disinda kare
# gorunmez duvar; derlemede +4000 (kamyon girerken), GSC inince indirir
KS = 1600
_ks = []
for (a_, b_) in (((-KS, -KS), (KS, -KS)), ((KS, -KS), (KS, KS)), ((KS, KS), (-KS, KS)), ((-KS, KS), (-KS, -KS))):
    dikey_levha(a_, b_, ZK - 300 + ENGEL_KAYDIR_S, ZK + 1800 + ENGEL_KAYDIR_S, SINIR, hedef=_ks)
H.ent('script_brushmodel', brushlar=_ks, targetname='koy_sinir')

# AVLU: kuyu, palmiyeler, kum torbalari, sandiklar
model('egypt_prop_well1', 0, 0, ZK + 1, 0)
H.kutu(-56, -56, ZK + 1, 56, 56, ZK + 46, 'clip', 'clip', alt='clip')
KAYALAR.append((0, 0, 70))
for (x, y, m, yaw) in ((-150, -560, 'military_sandbag_desert_longsection', 0), (180, 520, 'military_sandbag_desert_longsection', 0),
                       (-620, -120, 'military_sandbag_desert_curvedsection', 90), (650, 120, 'military_sandbag_desert_curvedsection', 270),
                       (1050, -150, 'military_sandbag_desert_longsection', 90), (-1050, 160, 'military_sandbag_desert_longsection', 90)):
    model(m, x, y, ZK + 1 if koy_mes(x, y) < 1000 else None, yaw)
for (x, y, m) in ((-330, 150, 'prop_crate_dak3'), (-330, 100, 'prop_crate_dak5'), (280, -250, 'prop_barrel_tan'),
                  (310, -220, 'prop_barrel_tan'), (345, 240, 'prop_crate_dak1')):
    model(m, x, y, ZK + 1, random.Random(x).randint(0, 90))
    H.kutu(x - 22, y - 22, ZK + 1, x + 22, y + 22, ZK + 44, 'clip', 'clip', alt='clip')
EV_ESYA = [('furniture_northafrica_longtable', -700, 450, 0), ('furniture_northafrica_woodchair', -700, 520, 270),
           ('furniture_northafrica_armoire_tall', -880 + 30, 760, 0), ('egypt_prop_vase2', -400, 340, 0),
           ('furniture_northafrica_coffeetable', 600, -600, 0), ('furniture_northafrica_egyptianchair', 650, -560, 180),
           ('egypt_prop_vase4', 840, -420, 0)]
ESYA_KUTU = {'furniture_northafrica_longtable': (40, 34), 'furniture_northafrica_woodchair': (12, 40),
             'furniture_northafrica_armoire_tall': (26, 90), 'egypt_prop_vase2': (10, 30),
             'furniture_northafrica_coffeetable': (26, 24), 'furniture_northafrica_egyptianchair': (14, 40),
             'egypt_prop_vase4': (10, 30)}
EV_ESYA.append(('furniture_northafrica_longtable', 660, -470, 0))
TELSIZ = (660, -470, BZ + 33)
H.ent('script_model', model='xmodel/military_german_fieldradio_green', origin=TELSIZ, angles=(0, 90, 0), targetname='telsiz',
      target='telsiz_tetik')
_tl = []
H.kutu(TELSIZ[0] - 60, TELSIZ[1] - 60, BZ, TELSIZ[0] + 60, TELSIZ[1] + 60, BZ + 80, 'trigger', 'trigger', alt='trigger', hedef=_tl)
H.ent('trigger_use', brushlar=_tl, targetname='telsiz_tetik')
for (m, x, y, yaw) in EV_ESYA:
    model(m, x, y, BZ, yaw)
    if m in ESYA_KUTU:
        r_, h_ = ESYA_KUTU[m]
        H.kutu(x - r_, y - r_, BZ, x + r_, y + r_, BZ + h_, 'clip', 'clip', alt='clip')
for (x, y, z) in ((-630, 560, BZ + EV_H - 30), (630, -600, BZ + EV_H - 30)):
    isik(x, y, z, 320, .9)

# =========================================================================
# DEKOR: palmiyeler, calilar, kayalar, yanmis araclar
# =========================================================================
rnd = random.Random(7)
for (x, y) in ((-1300, 900), (-1200, 1200), (1300, -900), (1250, 950), (-1350, -1000), (150, 1250),
               (-200, -1250), (1400, 300)):
    model(rnd.choice(('tree_desertpalm01', 'tree_desertpalm02', 'tree_desertpalm03')), x, y, None, rnd.randint(0, 359))
    KAYALAR.append((x, y, 30))
def duz_yer(x, y, yar=170):
    en, eb = None, 1e9
    for r_ in range(0, 900, 60):
        for k_ in range(max(1, r_ // 30)):
            a_ = 2 * math.pi * k_ / max(1, r_ // 30)
            px, py = x + math.cos(a_) * r_, y + math.sin(a_) * r_
            zs = [yukseklik(px + dx, py + dy) for dx in (-yar, 0, yar) for dy in (-yar, 0, yar)]
            fark = max(zs) - min(zs)
            if fark < eb:
                en, eb = (px, py, min(zs) + 2), fark
            if eb < 14:
                return en
    return en
for (x, y, m, yaw) in ((2600, 900, 'vehicle_crusader2_d_static', 40), (-2400, -1200, 'vehicle_opel_blitz_desert_d_static', 120),
                       (-3000, 1900, 'vehicle_panzer_ii_destroyed_static', 300), (3200, -2400, 'vehicle_opel_blitz_desert_d_static', 200)):
    # kullanici: Panzer enkazi havada duruyordu -> duz yere, en alcak koseye oturur
    px, py, pz = duz_yer(x, y)
    model(m, px, py, pz, yaw)
    KAYALAR.append((px, py, 190))
for (x, y, ad_) in ((-1150, 1150, 'obek'), (1150, 1250, 'obek'), (-1250, -1150, 'obek'), (1250, -1200, 'obek'),
                   (-1400, 300, 'obek'), (-500, 1300, 'obek'), (-600, -1350, 'obek')):
    for k_ in range(3):
        px, py = x + rnd.randint(-120, 120), y + rnd.randint(-120, 120)
        model(rnd.choice(('tree_desertpalm01', 'tree_desertpalm02', 'tree_desertpalm03')), px, py, None, rnd.randint(0, 359))
        KAYALAR.append((px, py, 30))
    for k_ in range(4):
        model(rnd.choice(('brush_desertshrubgroup01', 'brush_egypt_desert_1', 'brush_desertspikeyshrub')),
              x + rnd.randint(-220, 220), y + rnd.randint(-220, 220), None, rnd.randint(0, 359), kayit=False)
for (x, y, m) in ((880, 760, 'egypt_prop_vase2'), (900, 700, 'egypt_prop_vase4'), (-920, 830, 'egypt_prop_vase3'),
                  (-900, -820, 'egypt_prop_vase1'), (900, -840, 'egypt_prop_vase5'), (-880, -380, 'prop_barrel_tan'),
                  (-850, -360, 'prop_barrel_tan'), (880, 330, 'prop_crate_dak7'), (-380, 860, 'prop_crate_dak8')):
    model(m, x, y, ZK + 1, rnd.randint(0, 359))
    H.kutu(x - 18, y - 18, ZK + 1, x + 18, y + 18, ZK + 40, 'clip', 'clip', alt='clip')
    KAYALAR.append((x, y, 24))
# arac rotalari (ent_kumtepe kullanir): kaya/agac bu seritlerden uzak
CR_ROTA = [[(1500, -60), (900, -80), (535, -98)],                                       # koyun ici (kurban, kullanici viewpos)
           [(1900, 1300), (600, 1850), (-300, 1850), (-650, 1500)],                     # sag (kuzey) 1
           [(1900, 1450), (500, 2150), (-600, 2150), (-1000, 1700)],                    # sag (kuzey) 2
           [(1900, -1400), (500, -1850), (-500, -1850), (-750, -1450)]]                 # sol (guney)
YP_ROTA = {'kuzey': [(300, 4300), (250, 3000), (150, 2100), (60, 1350)],
           'guney': [(700, -4300), (500, -3000), (300, -2100), (150, -1350)],
           'bati':  [(-4800, -200), (-3300, -300), (-2300, -200), (-1400, -150)],
           'dogu':  [(4400, -1100), (3300, -650), (2400, -350), (1500, -350)]}
def rota_mes(x, y):
    en = 1e9
    for h_ in CR_ROTA + list(YP_ROTA.values()) + [[(2400, -200)] + CR_ROTA[1][:1], [(2400, -200)] + CR_ROTA[3][:1]]:
        for i_ in range(len(h_) - 1):
            en = min(en, _seg(x, y, h_[i_], h_[i_ + 1]))
    return en
for i in range(28):
    x, y = rnd.uniform(-5200, 5200), rnd.uniform(-4500, 4500)
    if icinde(x, y) and koy_mes(x, y) > 1600 and giris_mes(x, y) > 500 and kenar_mes(x, y) > 300 and rota_mes(x, y) > 350:
        kaya(x, y, rnd.randint(60, 140), rnd.randint(40, 110), 900 + i)
for i in range(260):
    x, y = rnd.uniform(-5300, 5300), rnd.uniform(-4700, 4700)
    if not icinde(x, y) or koy_mes(x, y) < 1800 or giris_mes(x, y) < 380 or kenar_mes(x, y) < 200 or rota_mes(x, y) < 300:
        continue
    if any(math.hypot(x - a, y - b) < r + 120 for (a, b, r) in KAYALAR):
        continue
    if any(math.hypot(x - a, y - b) < 260 for (a, b) in AGAC):
        continue
    m_ = rnd.choice(('tree_desertpalm01', 'tree_desertpalm02', 'tree_desertpalm03', 'tree_desertpalmgroup', 'tree_desertbushy'))
    model(m_, x, y, None, rnd.randint(0, 359))
    KAYALAR.append((x, y, 34))
CALI = ['brush_desertshrubbrownmid', 'brush_desertshrubgraymid', 'brush_desertshrubgroup01', 'brush_egypt_desert_1',
        'brush_egypt_desert_2', 'brush_desertspikeyshrub', 'brush_desertshrubbrowntall']
for x in range(SX0 + 300, SX1 - 299, 420):
    for y in range(SY0 + 300, SY1 - 299, 420):
        x2, y2 = x + rnd.randint(-160, 160), y + rnd.randint(-160, 160)
        if koy_mes(x2, y2) < 1250 or yol_mesafe(x2, y2) < 220:
            continue
        if any(math.hypot(x2 - a, y2 - b) < r + 40 for (a, b, r) in KAYALAR):
            continue
        if rnd.random() < (0.35 if icinde(x2, y2) else 0.55):
            model(rnd.choice(CALI), x2, y2, None, rnd.randint(0, 359), kayit=icinde(x2, y2))
for x in range(SX0 + 400, SX1 - 399, 900):                          # ufuk palmiyeleri (sinir disi)
    for y in range(SY0 + 400, SY1 - 399, 900):
        x2, y2 = x + rnd.randint(-300, 300), y + rnd.randint(-300, 300)
        if not icinde(x2, y2) and kenar_mes(x2, y2) > 400 and giris_mes(x2, y2) > 500 and rnd.random() < 0.3:
            model(rnd.choice(('tree_desertpalm01', 'tree_desertpalm02', 'tree_desertpalmgroup')), x2, y2, None,
                  rnd.randint(0, 359), kayit=False)

# ---------------------------------------------------------------- baslangic, guvenli noktalar
BASLANGIC = (6300, -3200)
H.ent('info_player_start', origin=(BASLANGIC[0], BASLANGIC[1], round(yukseklik(*BASLANGIC) + 8, 1)), angles=(0, 150, 0))
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
    o = ['// kumtepe_sinir.gsc -- gen_kumtepe.py URETIR, elle duzenlemeyin.', 'cokgen()', '{', '\tp = [];']
    for (x, y) in POLI:
        o.append('\tp[p.size] = (%d, %d, 0);' % (round(x), round(y)))
    o += ['\treturn p;', '}', '']
    open(os.path.join(KOK, 'main', 'maps', HARITA + '_sinir.gsc'), 'w', newline='\r\n').write('\n'.join(o) + '\n')
sinir_gsc()

import ent_kumtepe
ent_kumtepe.yerlestir(sys.modules[__name__])

if __name__ == '__main__':
    eksik, eksik_m = dogrula()
    if eksik or eksik_m:
        raise SystemExit('EKSIK VARLIK! malzeme: %s model: %s' % (eksik, eksik_m))
    r = H.yaz(os.path.join(KOK, 'map_source', HARITA + '.map'))
    print('dunya brush/mesh: %(dunya_brush)d  entity: %(entity)d  bayt: %(bayt)d' % r)
    print('misc_model: %d  kaya: %d' % (sum(1 for d, _ in H.ents if d['classname'] == 'misc_model'), len(KAYALAR)))
    print('konvoy yolu: %d birim' % hat_uzunluk(KONVOY))
