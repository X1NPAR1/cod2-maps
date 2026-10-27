# -*- coding: utf-8 -*-
"""
gen_sidirezegh.py -- CoD2 SP 'sidirezegh' (Ingiliz, Kuzey Afrika kasabasi, savunma).

Duzen (dunya birimi, kuzey = +Y):
  Orta : meydan (brush taban ZK+1, +/-1400) ve iki katli KARARGAH (ici iki kat girilir,
         ic merdiven + AI rampasi, her yonde pencere, duz cati). Oyuncu, Price ve 6 Ingiliz
         burayi savunur.
  Cevre: meydana bakan 8 stok libyatown/toujane prefab bina (misc_prefab; katalogdaki
         'front' tarafi meydana doner), sokak agizlari K / D / G (dusman) ve B (takviye).
  Disari: dort gizli yol -- harita disindaki kanyonlarda kivrilir, baslari/sonlari gorunmez.
Skill kurallari: stock-map-anatomy (prefab sehir, yol kenari, yogunluk), prefab-catalog
(zemin 0, front + yaw), terrain-borders (sirt halkasi, kanyon), ai-paths (sik dugum).
"""
import os, sys, math, random, zipfile, glob, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kmap import Harita, OLCEK

KOK = r'F:\Activision\Call of Duty 2'
HARITA = 'sidirezegh'

# ---------------------------------------------------------------- malzemeler
KUM = 'egypt_roughdirt_04'
YOL = 'egypt_roughdirt_05'
MEYDAN = 'egypt_sandblown01'
KAYA = 'egypt_rock_1'
DIS = 'egypt_plaster_exteriorwall03'
IC = 'egypt_plaster_interiorwall2'
TABAN = 'egypt_concrete_floor2'
CATI = 'egypt_gravel_roof1'
TAS = 'egypt_sandstone_generic1'
TRIM = 'egypt_wood_generic1'
KIRIS = 'egypt_wood_beam'
KAPI_M = 'egypt_wood_door2'
TAVAN = 'egypt_wood_ceiling1'
GOK = 'sky_elalamein'
TAS_YOL = 'toujane_cobblestone1'        # meydan ortasi: arnavut kaldirimi
YOL_DY = 'egypt_roughdirt_05'           # caddeler: dis yollarla ayni toprak yol (olculdu: toujane_road1 brushta BEYAZ)
YOL_KG = 'egypt_roughdirt_05'
ZEMIN1 = KUM                            # meydan toprak = arazi dokusu (kare sinir yok)
ZEMIN2 = 'toujane_ground2'              # catlak toprak lekeleri
DIS = 'egypt_plaster_exteriorwall02'    # karargah dis siva (onizlendi)
CAULK = 'caulk'
SINIR = 'clip_player'
for m_, o_ in ((KUM, (512, 512)), (YOL, (256, 256)), (MEYDAN, (512, 512)), (DIS, (256, 256)), (IC, (256, 256)),
               (TABAN, (256, 256)), (CATI, (256, 256)), (TAS, (512, 256)), (TRIM, (64, 128)), (KIRIS, (128, 128)),
               (TAVAN, (256, 256)), (KAYA, (256, 256)), (TAS_YOL, (256, 256)), (YOL_DY, (512, 512)),
               (YOL_KG, (512, 512)), (ZEMIN1, (512, 512)), (ZEMIN2, (512, 512))):
    OLCEK[m_] = o_

H = Harita()
H.ws.update({'_color': '1 .86 .70', 'ambient': '.24', 'sunlight': '1.3',
             'sundirection': '-40 -130 0', 'sundiffusecolor': '1 .85 .66',
             'suncolor': '1 .82 .60', 'diffusefraction': '.5', 'northyaw': '90'})

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

def chaikin(nok, n=3):
    for _ in range(n):
        y_ = [nok[0]]
        for i in range(len(nok) - 1):
            (ax, ay), (bx, by) = nok[i][:2], nok[i + 1][:2]
            y_ += [(ax * .75 + bx * .25, ay * .75 + by * .25), (ax * .25 + bx * .75, ay * .25 + by * .75)]
        y_.append(nok[-1])
        nok = y_
    return nok

# ---------------------------------------------------------------- sinir
SX0, SX1, SY0, SY1 = -7168, 7168, -7168, 7168
ZTAVAN = 3072
POLI = [(-4600, -2800), (-4200, -4300), (-2400, -4700), (0, -4800), (2600, -4600), (4300, -3800),
        (4800, -1600), (4700, 1400), (4200, 3600), (2200, 4600), (-300, 4800), (-2800, 4500),
        (-4400, 3200), (-4800, 800)]

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

# ---------------------------------------------------------------- kasaba ve yollar
ZK = 40.0
MY = 1400                      # meydan yari genisligi
KOY_R = 1700
# Yollar: sokak agzindan cikip sirti asar, harita disindaki kanyonda 90+ derece kivrilir
YOL_K = [(0, 430), (-70, 950), (0, 1400), (60, 2300), (-250, 3300), (-900, 4300), (-2100, 5100), (-3600, 5700), (-5400, 6200), (-6800, 6600)]
YOL_D = [(450, 0), (950, 70), (1400, 0), (2300, 80), (3300, -200), (4300, -800), (5200, -1900), (5800, -3300), (6300, -4900), (6700, -6600)]
YOL_G = [(0, -430), (70, -950), (0, -1400), (-80, -2300), (250, -3300), (900, -4300), (2100, -5100), (3600, -5700), (5300, -6200), (6800, -6700)]
YOL_B = [(-450, 0), (-950, -70), (-1400, 0), (-2300, -80), (-3300, 200), (-4300, 900), (-5200, 2000), (-5800, 3500), (-6300, 5100), (-6700, 6700)]
YOLLAR = {'kuzey': (YOL_K, 230), 'dogu': (YOL_D, 230), 'guney': (YOL_G, 230), 'bati': (YOL_B, 230)}

def meydan_mes(x, y):
    return math.hypot(max(abs(x) - MY, 0), max(abs(y) - MY, 0))

def yol_mes_ham(x, y, ad):
    h, _ = YOLLAR[ad]
    return min(_seg(x, y, h[i], h[i + 1]) for i in range(len(h) - 1))

def giris_mes(x, y):
    return min(yol_mes_ham(x, y, ad) for ad in YOLLAR)

TEPE = [((-2600, 2900), 900, 240), ((2700, 3000), 950, 260), ((-2800, -3000), 950, 230), ((2900, -2900), 900, 250),
        ((-3600, 600), 700, 170), ((3700, 900), 750, 190), ((-3500, -1300), 650, 160), ((3600, -1700), 700, 180),
        # dalga dogus yerleri / yol basi saklayan tumsekler
        ((-1300, 3700), 650, 240), ((1300, 3600), 650, 230), ((3800, 2100), 600, 220), ((3700, -2700), 600, 220),
        ((1500, -3700), 650, 240), ((-1400, -3600), 650, 230), ((-3700, -2400), 600, 210), ((-3800, 2200), 600, 210)]

def zemin_ham(x, y):
    z = 0.0
    for ((cx, cy), r, hh) in TEPE:
        z += hh * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / float(r * r))
    z += 30 * math.sin(x / 1100.0 + 1.3) * math.cos(y / 1300.0) + 9 * math.sin((x + y) / 520.0)
    if not icinde(x, y):
        o = kenar_mes(x, y)
        dis = 200 + 900 * ss(0, 2000, o) + 220 * math.sin(x / 1600.0 + 0.7) * math.cos(y / 1900.0) * ss(300, 1300, o)
        z += dis * (0.15 + 0.85 * ss(220, 760, giris_mes(x, y))) + 380 * ss(600, 2200, o)
    else:
        z += 110 * ss(700, 0, kenar_mes(x, y))
    km = meydan_mes(x, y)
    if km < 600:
        z = lerp(ZK, z, ss(200, 600, km))
    return z

YOL_HAT = {}
for ad, (pts, gen) in YOLLAR.items():
    YOL_HAT[ad] = ([(x, y, float(zemin_ham(x, y))) for (x, y) in pts], gen)

def yol_bilgi(x, y):
    en = (1e9, 0.0, 0)
    for ad, (hat, gen) in YOL_HAT.items():
        for i in range(len(hat) - 1):
            (ax, ay, az), (bx, by, bz) = hat[i], hat[i + 1]
            dx, dy = bx - ax, by - ay
            L = float(dx * dx + dy * dy) or 1.0
            t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / L))
            d = math.hypot(x - (ax + dx * t), y - (ay + dy * t))
            if d < en[0]:
                en = (d, lerp(az, bz, t), gen / 2.0)
    return en

def yol_mesafe(x, y):
    return yol_bilgi(x, y)[0]

def yukseklik(x, y):
    z = zemin_ham(x, y)
    if meydan_mes(x, y) < 200:
        return ZK
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
    hat = [(x, y, 0) for (x, y) in chaikin([p[:2] for p in hat])]
    orn = []
    for i in range(len(hat) - 1):
        (ax, ay, _), (bx, by, _) = hat[i], hat[i + 1]
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
for ad_ in YOLLAR:
    yol_mesh(*YOL_HAT[ad_])

# ---------------------------------------------------------------- kayitlar
MODELLER = []
KAYALAR = []
YAPILAR = {}
AGAC = []

def model(m, x, y, z=None, yaw=0, kayit=True, sinif='misc_model', **kv):
    if m.startswith('tree_'):
        AGAC.append((x, y))
    if kayit:
        MODELLER.append((m, x, y))
    if z is None:
        z = yukseklik(x, y)
    return H.ent(sinif, model='xmodel/' + m, origin=(round(x, 1), round(y, 1), round(z, 1)), angles=(0, yaw, 0), **kv)

def isik(x, y, z, r=260, i=.6, renk='1 0.85 0.62'):
    H.ent('light', origin=(x, y, z), radius=r, intensity=i, _color=renk, **{'def': 'light_point_linear_nocenter'})

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

def kutu6(x0, y0, z0, x1, y1, z1, m, detay=False, olcek=None, hedef=None):
    if x1 - x0 > 0.01 and y1 - y0 > 0.01 and z1 - z0 > 0.01:
        H.kutu6(x0, y0, z0, x1, y1, z1, m, olcek=olcek, detay=detay, hedef=hedef)

# ---------------------------------------------------------------- oynanabilir sinir
for i in range(len(POLI)):
    a, b = POLI[i], POLI[(i + 1) % len(POLI)]
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    n = max(1, int(L // 48))
    for k in range(n):
        p0 = (lerp(a[0], b[0], k / float(n)), lerp(a[1], b[1], k / float(n)))
        p1 = (lerp(a[0], b[0], (k + 1) / float(n)), lerp(a[1], b[1], (k + 1) / float(n)))
        dikey_levha(p0, p1, -600, 2400, SINIR)
ENGEL_KAYDIR_S = 4000

# =========================================================================
# BINA YAPICI (kumtepe/burya: kapi 64x88, pencere 52 genis 46..88 '+' kasa)
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

def duz_cati(x0, y0, x1, y1, z, korkuluk=32):
    kutu6(x0 - 8, y0 - 8, z, x1 + 8, y1 + 8, z + 14, {'*': DIS, '+z': CATI, '-z': TAVAN})
    zc = z + 14
    for (a, b, c, d) in ((x0 - 8, y0 - 8, x1 + 8, y0 + 4), (x0 - 8, y1 - 4, x1 + 8, y1 + 8),
                         (x0 - 8, y0 + 4, x0 + 4, y1 - 4), (x1 - 4, y0 + 4, x1 + 8, y1 - 4)):
        kutu6(a, b, zc, c, d, zc + korkuluk, {'*': DIS, '+z': TAS})
    return zc

def kapi_kanati(eksen, c0, c1, da, db, z0):
    """kapali ahsap kapi: duvar kalinliginin ortasinda, doku kanada oturtulur"""
    cm = (c0 + c1) / 2.0
    m = {'*': TRIM}
    if eksen == 'x':
        m.update({'-y': KAPI_M, '+y': KAPI_M})
        kutu6(da, cm - 4, z0, db, cm + 4, z0 + KAPI_H, m, olcek=(db - da, KAPI_H, da, -z0))
    else:
        m.update({'-x': KAPI_M, '+x': KAPI_M})
        kutu6(cm - 4, da, z0, cm + 4, db, z0 + KAPI_H, m, olcek=(db - da, KAPI_H, da, -z0))

def duvarlar(x0, y0, x1, y1, z0, h, acikliklar, pencere_kasali=True):
    """Dort duvar; acikliklar: {'g'/'k'/'b'/'d': [('kapi'|'pen', merkez), ...]}"""
    z1 = z0 + h
    M = lambda ic, dis: {'*': DIS, ic: IC, dis: DIS}
    duvar = {'g': ('x', x0, x1, y0, y0 + K, '+y', '-y'), 'k': ('x', x0, x1, y1 - K, y1, '-y', '+y'),
             'b': ('y', y0 + K, y1 - K, x0, x0 + K, '+x', '-x'), 'd': ('y', y0 + K, y1 - K, x1 - K, x1, '-x', '+x')}
    for yon, (eks, a, b, c0, c1, ic, dis) in duvar.items():
        dl = []
        for (tur, m) in acikliklar.get(yon, []):
            if tur in ('kapi', 'kapali'):
                dl.append((m - KAPI_G / 2.0, m + KAPI_G / 2.0, z0, z0 + KAPI_H))
                if tur == 'kapali':
                    kapi_kanati(eks, c0, c1, m - KAPI_G / 2.0, m + KAPI_G / 2.0, z0)
            else:
                dl.append((m - PEN_G / 2.0, m + PEN_G / 2.0, z0 + PEN_ALT, z0 + PEN_UST))
                if pencere_kasali:
                    pencere_kasa(eks, c0, c1, m - PEN_G / 2.0, m + PEN_G / 2.0, z0 + PEN_ALT, z0 + PEN_UST)
        delikli_duvar(eks, a, b, c0, c1, z0, z1, dl, M(ic, dis))

# =========================================================================
# MEYDAN (brush taban ZK+1; yol agi dersi: mesh -> 16'lik brush tabana bag yok)
# =========================================================================
# (kullanici) meydan: kare karolar / tas doseme / kenar taslari YOK -- arazi mesh'i + yol seritleri
BZ = ZK + 3                                     # bina tabani: avlu ZK+1, esik 2 (rampa yok)
EV_H = 128
# ---------------------------------------------------------------- KARARGAH
KX0, KY0, KX1, KY1 = -320, -240, 320, 240
UZ = BZ + EV_H + 14                             # ust kat taban ust yuzu
kutu6(KX0, KY0, BZ - 40, KX1, KY1, BZ, {'*': TAS, '+z': TABAN})
# zemin kat: kapi guney (meydan), kapi kuzey (arka); bati duvarinda merdiven -> bati zemin penceresi yok
duvarlar(KX0, KY0, KX1, KY1, BZ, EV_H,
         {'g': [('kapi', 0), ('pen', -190), ('pen', 190)], 'k': [('kapali', 150), ('pen', -40), ('pen', -200)],
          'd': [('pen', -130), ('pen', 110)], 'b': [('pen', 160)]})
# ara doseme (merdiven boslugu x[-304,-216] y[-200,60])
MD = (KX0 + K, -140, KX0 + K + 88, 60)          # merdiven boslugu (onunde 80 birim zemin: AI onden girer)
_dm = {'*': DIS, '-z': TAVAN, '+z': TABAN}
kutu6(KX0, KY0, BZ + EV_H, KX1, MD[1], UZ, _dm)
kutu6(KX0, MD[3], BZ + EV_H, KX1, KY1, UZ, _dm)
kutu6(KX0, MD[1], BZ + EV_H, MD[0], MD[3], UZ, _dm)
kutu6(MD[2], MD[1], BZ + EV_H, KX1, MD[3], UZ, _dm)
# merdiven: 9 basamak, guneyden kuzeye yukselir; altinda AI rampasi (caulk kama)
NB = 12                                         # 145/12 ~ 12 birim: AI yukari bag kurar, gorunmez rampa yok
for k_ in range(NB):
    ya = MD[1] + (MD[3] - MD[1]) * k_ / float(NB)
    yb = MD[1] + (MD[3] - MD[1]) * (k_ + 1) / float(NB)
    zt_ = BZ + (UZ - BZ) * (k_ + 1) / float(NB)
    kutu6(MD[0], ya, BZ, MD[2], yb, zt_, {'*': IC, '+z': 'egypt_sandstone_stair1top', '-y': 'egypt_sandstone_stair1side'})
RUN = (MD[3] - MD[1]) / float(NB)
# AI rampasi (stok kural, skill ai-paths): yalniz basamak BURUNLARINDAN gecer, ilk basamagin
# onunden ileri tasmaz -> ayak alti farki <= 6 birim (kullanici: merdivende gorunmez duvar hissi)
H.kama(MD[0] + 2, MD[1] - RUN, MD[2] - 2, MD[3] - RUN, BZ - 1, BZ, UZ, '+y', 'clip_ai', 'clip_ai', alt='clip_ai')   # yalniz AI: gorunmez, basamak yuzlerini silmez (caulk silip bosluk gosteriyordu)   # kullanici: caulk bosluk gibi gorunuyordu -> dokulu
# limonluk: acik (dogu) yanda, basamak burun cizgisi boyunca egik ust kenarli duvar
_ys = MD[1] + 70                                 # ilk basamaklar acik: AI yandan rampaya biner (olculdu)
_zs = BZ + (UZ - BZ) * (_ys - (MD[1] - RUN)) / float(MD[3] - MD[1])
# yan duvar: basamak burun cizgisini izleyen duz, kesintisiz korkuluk duvari (stok ic merdiven gorunumu)
# (yan duvar kaldirildi -- kullanici: tahta merdiven duvari ve ust kattaki ucgen istenmiyor)
# ust kat korkulugu (bosluk kenari)
kutu6(MD[2], MD[1], UZ, MD[2] + 6, MD[3] - 40, UZ + 40, {'*': TRIM}, detay=True)
kutu6(MD[0], MD[1], UZ, MD[2], MD[1] + 6, UZ + 40, {'*': TRIM}, detay=True)
# ust kat: her yonde pencere (savunma)
duvarlar(KX0, KY0, KX1, KY1, UZ, EV_H,
         {'g': [('pen', -190), ('pen', 0), ('pen', 190)], 'k': [('pen', -190), ('pen', 0), ('pen', 190)],
          'b': [('pen', -110), ('pen', 120)], 'd': [('pen', -130), ('pen', 0), ('pen', 130)]})
CZ = duz_cati(KX0, KY0, KX1, KY1, UZ + EV_H)
YAPILAR['karargah'] = (KX0, KY0, KX1, KY1, True)
KAPI_YUK = 4000
_kp = []
_cm = KY0 + K / 2.0
kutu6(-KAPI_G / 2.0, _cm - 4, BZ + KAPI_YUK, KAPI_G / 2.0, _cm + 4, BZ + KAPI_H + KAPI_YUK,
      {'*': TRIM, '-y': KAPI_M, '+y': KAPI_M}, olcek=(KAPI_G, KAPI_H, -KAPI_G / 2.0, -(BZ + KAPI_YUK)), hedef=_kp)
# mentese: oda tarafi duvar yuzu kosesi (skill: duvar kalinligina gomulmez)
H.kutu(-KAPI_G / 2.0 - 4, KY0 + K - 4, BZ + KAPI_YUK, -KAPI_G / 2.0 + 4, KY0 + K + 4, BZ + 8 + KAPI_YUK, 'origin', 'origin', alt='origin', hedef=_kp)
H.ent('script_brushmodel', brushlar=_kp, targetname='karargah_kapi', spawnflags=1)
def denizlik(yon, m, z0):
    if yon == 'g': kutu6(m - 32, KY0 - 6, z0 + PEN_ALT - 6, m + 32, KY0, z0 + PEN_ALT, {'*': TAS}, detay=True)
    if yon == 'k': kutu6(m - 32, KY1, z0 + PEN_ALT - 6, m + 32, KY1 + 6, z0 + PEN_ALT, {'*': TAS}, detay=True)
    if yon == 'b': kutu6(KX0 - 6, m - 32, z0 + PEN_ALT - 6, KX0, m + 32, z0 + PEN_ALT, {'*': TAS}, detay=True)
    if yon == 'd': kutu6(KX1, m - 32, z0 + PEN_ALT - 6, KX1 + 6, m + 32, z0 + PEN_ALT, {'*': TAS}, detay=True)
for (yon, ms, z0) in (('g', (-190, 190), BZ), ('k', (-40, -200), BZ), ('d', (-130, 110), BZ), ('b', (160,), BZ),
                      ('g', (-190, 0, 190), UZ), ('k', (-190, 0, 190), UZ), ('b', (-110, 120), UZ), ('d', (-130, 0, 130), UZ)):
    for m_ in ms:
        denizlik(yon, m_, z0)
# tenteler: stok libyatown (awning_2x4-5_3: dis yuzde, z = taban + 88, yaw = disa bakan normal)
for (x_, y_, yaw_) in ((0, KY0, 270), (150, KY1, 90), (-190, KY0, 270), (190, KY0, 270)):
    model('awning_2x4-5_3', x_, y_, BZ + 88, yaw_, kayit=False)
# kapi esikleri ve tavan kirisleri
for xx in range(KX0 + 110, KX1 - 50, 150):
    kutu6(xx, KY0 + K, BZ + EV_H - 10, xx + 10, KY1 - K, BZ + EV_H, {'*': KIRIS}, detay=True)
# ic esyalar (clip; kapilardan uzak) + panzerschreck duvari
PS_YER = (210, KY1 - K - 7, BZ + 34)            # kuzey ic duvar, kapinin batisinda degil (kapi 150 -> 250'de)
PS_YER = (-120, KY1 - K - 14, BZ + 32)
EV_ESYA = [('furniture_northafrica_longtable', 120, -90, 0), ('furniture_northafrica_woodchair', 120, -30, 90),
           ('furniture_northafrica_armoire_tall', KX1 - K - 30, -170, 180), ('prop_crate_dak4', 220, 170, 15),
           ('prop_crate_dak2', 270, 175, 40), ('egypt_prop_vase2', KX1 - K - 18, 200, 0),
           ('egypt_prop_vase4_interior', 40, KY1 - K - 16, 0), ('furniture_northafrica_woodchair', 180, -90, 180)]
ESYA_KUTU = {'furniture_northafrica_longtable': (40, 34), 'furniture_northafrica_woodchair': (12, 40),
             'furniture_northafrica_armoire_tall': (26, 90), 'prop_crate_dak4': (26, 44), 'prop_crate_dak2': (26, 44),
             'egypt_prop_vase2': (10, 30), 'egypt_prop_vase4_interior': (10, 30)}
UST_ESYA = [('prop_crate_dak6', 200, -150, 0), ('furniture_northafrica_coffeetable', 150, 110, 0),
            ('egypt_prop_vase3_interior', 270, 190, 0), ('prop_crate_dak4', -60, 170, 20)]
for (m, x, y, yaw) in EV_ESYA:
    model(m, x, y, BZ, yaw)
    r_, h_ = ESYA_KUTU[m]
    H.kutu(x - r_, y - r_, BZ, x + r_, y + r_, BZ + h_, 'clip', 'clip', alt='clip')
for (m, x, y, yaw) in UST_ESYA:
    model(m, x, y, UZ, yaw)
    H.kutu(x - 26, y - 26, UZ, x + 26, y + 26, UZ + 40, 'clip', 'clip', alt='clip')
for (x, y, z) in ((0, 0, BZ + EV_H - 24), (0, 0, UZ + EV_H - 24), (-200, 120, BZ + EV_H - 24)):
    isik(x, y, z, 330, .85)
# kum torbasi siperleri karargah onunde
# kullanici: kamyon ve Panzer kum torbalarinin ustunden geciyordu -> arac yollarinin icinde, karargaha yakin
KUM_TORBA = ((60, 640, 'military_sandbag_desert_longsection', 0), (330, 630, 'military_sandbag_desert_curvedsection', 45),
             (790, -60, 'military_sandbag_desert_longsection', 90), (-790, 130, 'military_sandbag_desert_longsection', 90),
             (-230, 640, 'military_sandbag_desert_curvedsection', 135))
for (x, y, m, yaw) in KUM_TORBA:
    model(m, x, y, ZK + 1, yaw)

# =========================================================================
# CEVRE BINALARI: stok prefablar (prefab-catalog.md; zemin 0, 'front' meydana)
# =========================================================================
KAT = {r['path']: r for r in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'prefab-catalog.json')))}
ON_ACI = {'+x': 0, '+y': 90, '-x': 180, '-y': 270}
def _kutu(path, x, y, yaw):
    b = KAT[path]['bounds']
    c, s_ = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    w, d = (b[3] - b[0]) / 2.0, (b[4] - b[1]) / 2.0
    ex = abs(w * c) + abs(d * s_); ey = abs(w * s_) + abs(d * c)
    return (x - ex, y - ey, x + ex, y + ey)

def _bos(k, pay=40):
    for ad_, v in YAPILAR.items():
        if k[0] < v[2] + pay and k[2] > v[0] - pay and k[1] < v[3] + pay and k[3] > v[1] - pay:
            return False
    lim = SUR - SUR_K - 20
    return k[0] > -lim and k[2] < lim and k[1] > -lim and k[3] < lim

def prefab(path, x, y, bakis=None, yaw=None):
    """bina merkezi (x,y); on yuzu 'bakis' acisina (derece) cevrilir; taban ZK+1.
    Baska bina/sur ile cakisirsa (>= 40 aralik) merkeze dogru ya da yana kaydirilir."""
    r = KAT[path]
    b = r['bounds']
    if yaw is None:
        yaw = (bakis - ON_ACI.get(r['front'], 0)) % 360 if bakis is not None else 0
    if not _bos(_kutu(path, x, y, yaw)):
        L = math.hypot(x, y) or 1
        ux, uy = x / L, y / L
        for adim in range(40, 900, 40):
            ok = None
            for (dx, dy) in ((-ux, -uy), (-uy, ux), (uy, -ux), (ux, uy)):
                if _bos(_kutu(path, x + dx * adim, y + dy * adim, yaw)):
                    ok = (x + dx * adim, y + dy * adim)
                    break
            if ok:
                print('prefab kaydirildi: %s (%d,%d) -> (%d,%d)' % (path.split('/')[-1], x, y, ok[0], ok[1]))
                x, y = ok
                break
        else:
            raise SystemExit('PREFAB YERI YOK: %s' % path)
    cx, cy = (b[0] + b[3]) / 2.0, (b[1] + b[4]) / 2.0
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    ox, oy = x - (cx * c - cy * s), y - (cx * s + cy * c)
    oz = ZK + 1 - min(0, b[2])
    H.ent('misc_prefab', model=path, origin=(round(ox), round(oy), round(oz)), angles=(0, round(yaw), 0))
    # kapladigi alan (donmus bbox): dugum/esya engeli
    w, d = (b[3] - b[0]) / 2.0, (b[4] - b[1]) / 2.0
    ex = abs(w * c) + abs(d * s); ey = abs(w * s) + abs(d * c)
    YAPILAR[path.split('/')[-1] + '_%d_%d' % (x, y)] = (x - ex, y - ey, x + ex, y + ey, False)
    # girilmez kabuk: oyuncu ve AI icine giremez (stok libyatown binalari ici bos)
    H.kutu(x - ex + 6, y - ey + 6, ZK + 1, x + ex - 6, y + ey - 6, ZK + 1 + r['size'][2] * 0.9, 'clip', 'clip', alt='clip')
# SUR (kullanici: koyun etrafi duvarla cevrili, giris yerleri araclar icin genis)
SUR = 1560
SUR_K = 32
SUR_H = 230
KAPI_GEN = 420
def sur_parca(eksen, sabit, a, b):
    if b - a < 8:
        return
    if eksen == 'x':
        kutu6(a, sabit - SUR_K / 2, ZK - 20, b, sabit + SUR_K / 2, ZK + SUR_H, {'*': DIS})
        for m_ in range(int(a) + 20, int(b) - 30, 64):                    # mazgal disleri
            kutu6(m_, sabit - SUR_K / 2 - 2, ZK + SUR_H, m_ + 34, sabit + SUR_K / 2 + 2, ZK + SUR_H + 26, {'*': DIS, '+z': TAS})
        YAPILAR['sur_x_%d_%d' % (sabit, a)] = (a, sabit - SUR_K / 2, b, sabit + SUR_K / 2, False)
    else:
        kutu6(sabit - SUR_K / 2, a, ZK - 20, sabit + SUR_K / 2, b, ZK + SUR_H, {'*': DIS})
        for m_ in range(int(a) + 20, int(b) - 30, 64):
            kutu6(sabit - SUR_K / 2 - 2, m_, ZK + SUR_H, sabit + SUR_K / 2 + 2, m_ + 34, ZK + SUR_H + 26, {'*': DIS, '+z': TAS})
        YAPILAR['sur_y_%d_%d' % (sabit, a)] = (sabit - SUR_K / 2, a, sabit + SUR_K / 2, b, False)
KULE = 70
for (eksen, sabit) in (('x', SUR), ('x', -SUR), ('y', SUR), ('y', -SUR)):
    sur_parca(eksen, sabit, -SUR - SUR_K / 2, -KAPI_GEN / 2 - KULE * 2)
    sur_parca(eksen, sabit, KAPI_GEN / 2 + KULE * 2, SUR + SUR_K / 2)
    for sgn in (-1, 1):                                                    # kapi kuleleri
        m_ = sgn * (KAPI_GEN / 2 + KULE)
        if eksen == 'x':
            kutu6(m_ - KULE, sabit - KULE, ZK - 20, m_ + KULE, sabit + KULE, ZK + 330, {'*': DIS, '+z': CATI})
            kutu6(m_ - KULE - 6, sabit - KULE - 6, ZK + 330, m_ + KULE + 6, sabit + KULE + 6, ZK + 346, {'*': TAS})
            YAPILAR['kule_%s_%d_%d' % (eksen, sabit, sgn)] = (m_ - KULE, sabit - KULE, m_ + KULE, sabit + KULE, False)
        else:
            kutu6(sabit - KULE, m_ - KULE, ZK - 20, sabit + KULE, m_ + KULE, ZK + 330, {'*': DIS, '+z': CATI})
            kutu6(sabit - KULE - 6, m_ - KULE - 6, ZK + 330, sabit + KULE + 6, m_ + KULE + 6, ZK + 346, {'*': TAS})
            YAPILAR['kule_%s_%d_%d' % (eksen, sabit, sgn)] = (sabit - KULE, m_ - KULE, sabit + KULE, m_ + KULE, False)
for (x_, y_) in ((SUR, SUR), (-SUR, SUR), (SUR, -SUR), (-SUR, -SUR)):           # kose burclari
    kutu6(x_ - 90, y_ - 90, ZK - 20, x_ + 90, y_ + 90, ZK + 300, {'*': DIS, '+z': CATI})
    kutu6(x_ - 96, y_ - 96, ZK + 300, x_ + 96, y_ + 96, ZK + 316, {'*': TAS})
# KAPI ENGELLERI (yalniz oyuncu; araclar durur kapi agzinin disinda). Bati kapisi brushmodel:
# finalde Ingiliz kamyonu girerken GSC kaldirir (clip_player araci da durdurur -- olculdu)
for (ad_, eksen, sabit) in (('kapi_k', 'x', SUR), ('kapi_d', 'y', SUR), ('kapi_g', 'x', -SUR), ('kapi_b', 'y', -SUR)):
    _e = []
    if eksen == 'x':
        H.kutu(-KAPI_GEN / 2, sabit - 8, ZK - 300 + ENGEL_KAYDIR_S, KAPI_GEN / 2, sabit + 8, ZK + 1800 + ENGEL_KAYDIR_S, SINIR, SINIR, alt=SINIR, hedef=_e)
    else:
        H.kutu(sabit - 8, -KAPI_GEN / 2, ZK - 300 + ENGEL_KAYDIR_S, sabit + 8, KAPI_GEN / 2, ZK + 1800 + ENGEL_KAYDIR_S, SINIR, SINIR, alt=SINIR, hedef=_e)
    H.ent('script_brushmodel', brushlar=_e, targetname='kapi_engel', script_noteworthy=ad_)
# FINAL KORIDORU (kullanici: kapi kirilinca evin koselerinden guney sur kapisina kadar saga sola gidilmesin)
_fk = []
for _x in (KX0 - 12, KX1 + 12):
    H.kutu(_x - 8, -1560, ZK - 300 + ENGEL_KAYDIR_S, _x + 8, KY0, ZK + 1800 + ENGEL_KAYDIR_S, SINIR, SINIR, alt=SINIR, hedef=_fk)
H.ent('script_brushmodel', brushlar=_fk, targetname='final_koridor')
CEVRE = [('prefabs/libyatown/building_brown2story.map', -1120, 1150), ('prefabs/libyatown/building_2storysquare.map', 1150, 1150),
         ('prefabs/mp_matmata/building_brown2story2.map', 1120, -1150), ('prefabs/libyatown/building_1n1halfstory.map', -1150, -1150),]
for (p, x, y) in CEVRE:
    prefab(p, x, y, bakis=math.degrees(math.atan2(-y, -x)))
# pazar ve meydan dekoru (toujane prefablari + modeller)
for (p, x, y, yaw) in (('prefabs/toujane/tj_merchant2.map', -700, 520, 330), ('prefabs/toujane/tj_merchant3.map', 720, 560, 210),
                       ('prefabs/toujane/crates/cratepile_med2.map', 760, -560, 20), ('prefabs/toujane/crates/cratepile_med5.map', -1180, -560, 70)):
    H.ent('misc_prefab', model=p, origin=(x, y, ZK + 1), angles=(0, yaw, 0))
    YAPILAR['pazar_%d_%d' % (x, y)] = (x - 90, y - 90, x + 90, y + 90, False)
    H.kutu(x - 70, y - 70, ZK + 1, x + 70, y + 70, ZK + 60, 'clip', 'clip', alt='clip')
model('egypt_prop_well1', -760, 260, ZK + 1, 0)
H.kutu(-706, -206, ZK + 1, -594, -94, ZK + 46, 'clip', 'clip', alt='clip')
KAYALAR.append((-650, -150, 70))
for (x, y, m) in ((250, 290, 'prop_crate_dak3'), (300, 290, 'prop_crate_dak5'), (-250, 290, 'prop_barrel_tan'),
                  (-290, 300, 'prop_barrel_tan'), (900, 260, 'prop_crate_dak1'), (-900, 300, 'prop_crate_dak7')):
    model(m, x, y, ZK + 1, random.Random(x).randint(0, 90))
    H.kutu(x - 22, y - 22, ZK + 1, x + 22, y + 22, ZK + 44, 'clip', 'clip', alt='clip')
model('vehicle_opel_blitz_desert_d_static', -1010, 430, None, 80)    # kullanici: final kamyonu yolundan uzak
KAYALAR.append((-1050, 120, 190))
model('haycart_destroyed', 1050, -260, ZK + 1, 20)
KAYALAR.append((1050, -260, 100))
for (x, y) in ((-260, -880), (300, -900), (-900, 560), (930, 420), (-300, 900), (330, 880), (-560, -1250), (560, -1260),
               (-1250, 260), (1260, -300), (-700, 1260), (760, 1240), (1300, 1300), (-1300, -1300)):
    model(random.Random(x * 7 + y).choice(('tree_desertpalm01', 'tree_desertpalm02', 'tree_desertpalm03')), x, y, ZK + 1,
          random.Random(y).randint(0, 359))
    KAYALAR.append((x, y, 30))

# =========================================================================
# DEKOR: yol kenari, kanyon kayalari, vahalar, calilar, harita disi
# =========================================================================
rnd = random.Random(11)
CALI = ['brush_desertshrubbrownmid', 'brush_desertshrubgraymid', 'brush_desertshrubgroup01', 'brush_egypt_desert_1',
        'brush_egypt_desert_2', 'brush_desertspikeyshrub', 'brush_desertshrubbrowntall']
def yol_kenari(hat, aralik, yan, olas):
    for i in range(len(hat) - 1):
        (ax, ay), (bx, by) = hat[i][:2], hat[i + 1][:2]
        L = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / L, (by - ay) / L
        for k in range(int(L // aralik)):
            if rnd.random() > olas:
                continue
            m_ = k * aralik + rnd.uniform(-60, 60)
            for sgn in (-1, 1):
                x = ax + ux * m_ - uy * sgn * (yan + rnd.uniform(-40, 60))
                y = ay + uy * m_ + ux * sgn * (yan + rnd.uniform(-40, 60))
                if not icinde(x, y) or meydan_mes(x, y) < 250:
                    continue
                if any(math.hypot(x - a, y - b) < r + 60 for (a, b, r) in KAYALAR):
                    continue
                model(rnd.choice(('tree_desertpalm01', 'tree_desertpalm02', 'tree_desertpalm03')), x, y, None, rnd.randint(0, 359))
                KAYALAR.append((x, y, 30))
                model(rnd.choice(CALI), x + rnd.uniform(-90, 90), y + rnd.uniform(-90, 90), None, rnd.randint(0, 359), kayit=False)
for ad_ in YOLLAR:
    yol_kenari(YOLLAR[ad_][0], 330, 240, 0.85)
for (vx, vy) in ((-2600, 1500), (2400, 2000), (2300, -1700), (-2200, -2000), (-1200, 3000), (3300, -900), (-2000, 2300),
                 (2000, 2600), (2600, -2400), (-2700, -2600), (-3300, 300), (3100, 600), (1000, -2800), (-900, -2700)):
    for k_ in range(5):
        x, y = vx + rnd.randint(-330, 330), vy + rnd.randint(-330, 330)
        if icinde(x, y) and giris_mes(x, y) > 300:
            model(rnd.choice(('tree_desertpalm01', 'tree_desertpalm02', 'tree_desertpalmgroup')), x, y, None, rnd.randint(0, 359))
            KAYALAR.append((x, y, 34))
for i in range(24):
    x, y = rnd.uniform(-4200, 4200), rnd.uniform(-4200, 4200)
    if icinde(x, y) and meydan_mes(x, y) > 700 and giris_mes(x, y) > 450 and kenar_mes(x, y) > 300:
        kaya(x, y, rnd.randint(60, 140), rnd.randint(40, 110), 900 + i)
for x in range(SX0 + 300, SX1 - 299, 430):
    for y in range(SY0 + 300, SY1 - 299, 430):
        x2, y2 = x + rnd.randint(-160, 160), y + rnd.randint(-160, 160)
        if meydan_mes(x2, y2) < 300 or yol_mesafe(x2, y2) < 210:
            continue
        if any(math.hypot(x2 - a, y2 - b) < r + 40 for (a, b, r) in KAYALAR):
            continue
        if rnd.random() < (0.4 if icinde(x2, y2) else 0.55):
            model(rnd.choice(CALI), x2, y2, None, rnd.randint(0, 359), kayit=icinde(x2, y2))
# harita disi: kanyon kayalari ve sirt dekoru (kasrelbab dersi)
for ad_ in YOLLAR:
    hat_, gen_ = YOLLAR[ad_]
    for i in range(len(hat_) - 1):
        (ax, ay), (bx, by) = hat_[i], hat_[i + 1]
        L = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L, (by - ay) / L
        for k in range(int(L // 380)):
            m_ = k * 380 + rnd.uniform(-80, 80)
            for sgn in (-1, 1):
                d_ = gen_ / 2.0 + rnd.uniform(260, 420)
                x = ax + ux * m_ - uy * sgn * d_; y = ay + uy * m_ + ux * sgn * d_
                if icinde(x, y) or giris_mes(x, y) < gen_ / 2.0 + 200 or not (SX0 + 200 < x < SX1 - 200 and SY0 + 200 < y < SY1 - 200):
                    continue
                if rnd.random() < 0.55:
                    kaya(x, y, rnd.randint(90, 200), rnd.randint(60, 170), 5000 + i * 100 + k * 2 + (sgn > 0))
for x in range(SX0 + 400, SX1 - 399, 640):
    for y in range(SY0 + 400, SY1 - 399, 640):
        x2, y2 = x + rnd.randint(-240, 240), y + rnd.randint(-240, 240)
        if icinde(x2, y2) or giris_mes(x2, y2) < 420:
            continue
        r_ = rnd.random()
        if kenar_mes(x2, y2) > 250 and r_ < 0.25:
            kaya(x2, y2, rnd.randint(110, 240), rnd.randint(70, 200), 9000 + x // 7 + y // 11)
        elif r_ < 0.45:
            model(rnd.choice(('tree_desertbushy', 'tree_desertpalm01', 'tree_desertpalmgroup')), x2, y2, None, rnd.randint(0, 359), kayit=False)

# ---------------------------------------------------------------- baslangic
BASLANGIC = (-200, 60)
H.ent('misc_turret', model='xmodel/weapon_mg42', weaponinfo='mg42_bipod_stand',
      origin=(SX0 + 500, SY0 + 500, round(yukseklik(SX0 + 500, SY0 + 500), 1)), angles=(0, 0, 0))
H.ent('info_player_start', origin=(BASLANGIC[0], BASLANGIC[1], BZ + 8), angles=(0, 270, 0))

def dogrula():
    var = set()
    for p in glob.glob(os.path.join(KOK, 'main', '*.iwd')):
        for n_ in zipfile.ZipFile(p).namelist():
            var.add(n_.lower())
    eksik = [m for m in sorted(H.malzemeler) if m not in ('caulk', 'clip_player', 'clip', 'trigger', 'origin', 'ladder')
             and 'materials/' + m.lower() not in var]
    modeller = sorted({d['model'] for d, _ in H.ents if 'model' in d and d['classname'] in ('misc_model', 'script_model')})
    eksik_m = [m for m in modeller if m.lower() not in var]
    eksik_p = sorted({d['model'] for d, _ in H.ents if d['classname'] == 'misc_prefab'
                      and not os.path.exists(os.path.join(KOK, 'map_source', d['model'].replace('/', os.sep)))})
    return eksik, eksik_m, eksik_p

def sinir_gsc():
    o = ['// sidirezegh_sinir.gsc -- gen_sidirezegh.py URETIR, elle duzenlemeyin.', 'cokgen()', '{', '\tp = [];']
    for (x, y) in POLI:
        o.append('\tp[p.size] = (%d, %d, 0);' % (round(x), round(y)))
    o += ['\treturn p;', '}', '']
    open(os.path.join(KOK, 'main', 'maps', HARITA + '_sinir.gsc'), 'w', newline='\r\n').write('\n'.join(o) + '\n')
sinir_gsc()

import ent_sidirezegh
ent_sidirezegh.yerlestir(sys.modules[__name__])

if __name__ == '__main__':
    eksik, eksik_m, eksik_p = dogrula()
    if eksik or eksik_m or eksik_p:
        raise SystemExit('EKSIK VARLIK! malzeme: %s model: %s prefab: %s' % (eksik, eksik_m, eksik_p))
    r = H.yaz(os.path.join(KOK, 'map_source', HARITA + '.map'))
    print('dunya brush/mesh: %(dunya_brush)d  entity: %(entity)d  bayt: %(bayt)d' % r)
    print('misc_model: %d  misc_prefab: %d  kaya: %d' % (sum(1 for d, _ in H.ents if d['classname'] == 'misc_model'),
                                                       sum(1 for d, _ in H.ents if d['classname'] == 'misc_prefab'), len(KAYALAR)))
