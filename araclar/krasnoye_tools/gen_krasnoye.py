# -*- coding: utf-8 -*-
"""
gen_krasnoye.py v3 -- CoD2 SP 'krasnoye' (karli kolhoz koyu).

Kuzey = +Y.  OYNANABILIR ALAN  x -2816..2816, y -3328..3328  (kenarda gorunmez
clip_player duvari). Gokyuzu kutusu daha genis (x +-4096, y +-4608); aradaki
bant yumusak tepelerle ve sik cam ormaniyla dolar -> "dunya devam ediyor".

  y  2600..3100  TAKVIYE ALANI (kuzey sirti arkasi, gorus disi)
  y  2330        KUZEY SIRTI
  y  1650..2000  SOVYET BASLANGIC SIPERI
  y  -700..1500  KOLHOZ KOYU
  y  -860        SAVUNMA HATTI
  ALMAN YOLU     BATIDA harita disinda (x -3950) orman arkasindaki S
                 kivrimindan dogar, guney tarlasindan kivrilip koyun guney
                 agzina (0,-440) gelir. Baslangici oyuncu goremez.

Malzemeler iwd'de GERCEK goruntusu olcuelenlerden secildi ('case*' yer tutucu
goruntulu stalingrad_interiorwall01 / dawnville2_wood_door01 / *_shutters01
ELENDI -- oyunda numarali izgara cikti).
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kmap import Harita

KOK = r'F:\Activision\Call of Duty 2'

KAR = 'stalingradwinter_snow01'
YOL = 'stalingradwinter_slush1'
DIS = 'stalingradwinter_woodplank01'
DIS2 = 'stalingradwinter_woodplank02'
DIS3 = 'stalingradwinter_woodplank03'
GRI = 'stalingradwinter_woodplank03'      # greywood: oyunda gerilip bulaniklasti (c1 tur)
TRIM = 'stalingradwinter_wood_trim'
IC = 'stalingradwinter_plaster01'
TABAN = 'stalingradwinter_wood_floor'
CATI = 'stalingradwinter_roof_slate01'
TEMEL = 'stalingradwinter_brick02'
TUGLA = 'stalingradwinter_brick03'
KIRIS = 'stalingrad_beam_side'
PERVAZ = 'dawnville2_windowframe01'
KASA = 'dawnville2_doorframe01'
KAPI_M = 'mtl_caen_door_wood_02'
KEPENK = 'v_shutter_01'
CAM_M = 'mtl_caen_window_brown_1'
GOK = 'sky_tankhunt'
CAULK = 'caulk'
SINIR = 'clip_player'

H = Harita()
H.ws.update({'_color': '1 .97 1', 'ambient': '.20', 'sunlight': '1.35',
             'sundirection': '-42 -43 0', 'sundiffusecolor': '.9 .9 .96',
             'suncolor': '1 .97 .98', 'diffusefraction': '.55',
             '-contrastgain': '.4', 'northyaw': '90'})

PX0, PX1, PY0, PY1 = -2816, 2816, -3328, 3328          # oynanabilir
SX0, SX1, SY0, SY1 = -4096, 4096, -4608, 4608          # gokyuzu kutusu
ZTAVAN = 2560

# =========================================================================
# 1. GOKYUZU KUTUSU (taban caulk; tavanin ALT yuzu de gokyuzu)
# =========================================================================
H.oda_kabugu(SX0, SY0, -192, SX1, SY1, ZTAVAN, 16, CAULK, GOK, GOK)

# =========================================================================
# 2. ALMAN YOLU (batidan, harita disindan)
# =========================================================================
YOL_HAT = [(0, -440), (0, -900), (-120, -1250), (-500, -1560), (-1100, -1800),
           (-1800, -1760), (-2400, -1950), (-3000, -2180), (-3500, -2000),
           (-3850, -1700), (-3990, -1520)]

def _seg(px, py, a, b):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / float(dx * dx + dy * dy)))
    return math.hypot(px - (ax + dx * t), py - (ay + dy * t))

def yol_mesafe(x, y):
    return min(_seg(x, y, YOL_HAT[i], YOL_HAT[i + 1]) for i in range(len(YOL_HAT) - 1))

def ss(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / float(e1 - e0)))
    return t * t * (3 - 2 * t)

def disari(x, y):
    """oynanabilir alanin disina tasma mesafesi (iceride 0)."""
    dx = max(PX0 - x, x - PX1, 0); dy = max(PY0 - y, y - PY1, 0)
    return math.hypot(dx, dy)

TUMSEK = [(-1400, -1250, 260, 55), (1350, -1650, 300, 65), (-650, -2300, 240, 45),
          (750, -1250, 200, 35), (-2050, -900, 320, 80), (2000, -1100, 300, 70),
          (-1700, 1900, 300, 60), (1800, 2000, 320, 70), (-2150, 300, 300, 90),
          (2150, 400, 320, 85), (900, -2100, 260, 50), (-2300, -2600, 380, 90)]
# harita disi tepeler (yolun S kivrimini ve dogus yerini gizler)
DIS_TEPE = [(-3400, -1350, 520, 260), (-3300, -2700, 500, 220), (-3600, 900, 700, 240),
            (3500, -1500, 700, 260), (3400, 1500, 700, 240), (-1500, 4000, 800, 230),
            (1500, 4000, 800, 230), (0, -4100, 900, 220)]

def yukseklik(x, y):
    z = 0.0
    # ic tumsekler ALCALTILDI (kullanici istegi): sirtlar 230/190 -> 130/105,
    # tumsekler %45. Harita kenari (asagidaki disari bandi) DEGISMEDI.
    z += 130 * math.exp(-((y - 2330) / 260.0) ** 2) * ss(0, 400, PX1 + 400 - abs(x))
    z += 105 * math.exp(-((y + 2480) / 230.0) ** 2) * ss(0, 400, PX1 + 400 - abs(x))
    for (cx, cy, r, hh) in TUMSEK:
        z += 0.45 * hh * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / float(r * r))
    dx = max(-1900 - x, x - 1950, 0); dy = max(-760 - y, y - 1980, 0)
    z *= ss(0, 320, math.hypot(dx, dy))                 # koy + siper duz
    # harita disi: yumusak yukselen, dalgali tepeler
    o = disari(x, y)
    z += 280 * ss(0, 1300, o) + 60 * math.sin(x / 610.0) * math.cos(y / 730.0) * ss(0, 500, o)
    for (cx, cy, r, hh) in DIS_TEPE:
        z += hh * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / float(r * r))
    z *= ss(140, 380, yol_mesafe(x, y))                  # yol seridi duz
    return z

# --- arazi mesh'i: 128 aralik, 8x8 parca ---
A = 128
xs = list(range(SX0, SX1 + 1, A)); ys = list(range(SY0, SY1 + 1, A))
def parcala(n, k):
    adim = (n - 1) // k
    return [(i * adim, (i + 1) * adim if i < k - 1 else n - 1) for i in range(k)]
for (i0, i1) in parcala(len(xs), 8):
    for (j0, j1) in parcala(len(ys), 8):
        H.mesh([[(xs[i], ys[j], round(yukseklik(xs[i], ys[j]), 2)) for j in range(j0, j1 + 1)]
                for i in range(i0, i1 + 1)], KAR, doku=4.0)

def yol_ornek(adim=96):
    o = []
    for i in range(len(YOL_HAT) - 1):
        (ax, ay), (bx, by) = YOL_HAT[i], YOL_HAT[i + 1]
        n = max(1, int(math.hypot(bx - ax, by - ay) // adim))
        for k in range(n):
            t = k / float(n); o.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    o.append(YOL_HAT[-1])
    return o

def yol_mesh():
    ornek = yol_ornek()
    satirlar = []
    for k, (px, py) in enumerate(ornek):
        a = ornek[max(0, k - 1)]; b = ornek[min(len(ornek) - 1, k + 1)]
        ux, uy = b[0] - a[0], b[1] - a[1]; L = math.hypot(ux, uy); ux, uy = ux / L, uy / L
        qx, qy = -uy, ux
        s = []
        for w in (-176, 0, 176):
            x, y = px + qx * w, py + qy * w
            s.append((round(x, 2), round(y, 2), round(yukseklik(x, y) + 3, 2)))
        satirlar.append(s)
    for s in range(0, len(satirlar) - 1, 23):
        H.mesh(satirlar[s:s + 24], YOL, doku=4.0, detay=True)
yol_mesh()

# =========================================================================
# 3. GORUNMEZ SINIR (clip_player): oyuncu disari cikamaz
# =========================================================================
for (a, b, c, d) in [(PX0 - 16, PY0 - 16, PX0, PY1 + 16), (PX1, PY0 - 16, PX1 + 16, PY1 + 16),
                     (PX0, PY0 - 16, PX1, PY0), (PX0, PY1, PX1, PY1 + 16)]:
    H.kutu(a, b, -192, c, d, 1600, SINIR, SINIR, alt=SINIR)

# =========================================================================
# 4. YAPILAR
# =========================================================================
TEMEL_Z = 24
DUVAR_Z = 184
K = 16
YAPILAR = {}
ISIKLAR = []

def kapi_d(m):  return ('kapi', m - 28, m + 28, TEMEL_Z, TEMEL_Z + 104)
def pen_d(m):   return ('pen', m - 28, m + 28, TEMEL_Z + 56, TEMEL_Z + 104)

def fit(gen, yuk, a, b):
    """Dokuyu acikliga TAM oturt: tekrar boyu = aciklik olcusu, kaydirma = baslangic."""
    return (gen, yuk, -a, -b)

AGAC = []
MODELLER = []          # (model, x, y) -- yol dugumleri carpismadan kacinsin
def model(m, x, y, z=None, yaw=0):
    if m.startswith('tree_'):
        AGAC.append((x, y))
    MODELLER.append((m, x, y))
    if z is None:
        z = yukseklik(x, y)
    H.ent('misc_model', model='xmodel/' + m, origin=(round(x, 1), round(y, 1), round(z, 1)),
          angles=(0, yaw, 0))

def isik(x, y, z, r=230, i=.55, renk='1 0.78 0.45'):
    H.ent('light', origin=(x, y, z), radius=r, intensity=i, _color=renk,
          **{'def': 'light_point_linear_nocenter'})

def acik_ekleri(eksen, ic, c0, c1, tur, da, db, za, zb, kapali):
    """pervaz/esik/kepenk/kapi. kapali=True: aciklik fit dokulu kapi/pencere ile dolar."""
    dis_c = c0 if ic > 0 else c1
    sgn = -ic
    lo, hi = (dis_c - 4, dis_c) if sgn < 0 else (dis_c, dis_c + 4)
    def box(p0, p1, z0, z1, mat, olc=None):
        if eksen == 'x': H.kutu(p0, lo, z0, p1, hi, z1, mat, olcek=olc, detay=True)
        else: H.kutu(lo, p0, z0, hi, p1, z1, mat, olcek=olc, detay=True)
    fm = KASA if tur == 'kapi' else PERVAZ
    box(da - 6, da, za, zb + 6, fm, (8, 128))
    box(db, db + 6, za, zb + 6, fm, (8, 128))
    box(da - 6, db + 6, zb, zb + 8, fm, (128, 8))
    if tur == 'pen':
        box(da - 8, db + 8, za - 6, za, fm, (128, 8))
    if kapali:
        mat = KAPI_M if tur == 'kapi' else KEPENK
        # aciklik icini dolduran fit dokulu kapak (duvar kalinliginin ortasina)
        orta0, orta1 = (c0 + 4, c1 - 4)
        if eksen == 'x':
            H.kutu(da, orta0, za, db, orta1, zb, mat, olcek=fit(db - da, zb - za, da, za))
        else:
            H.kutu(orta0, da, za, orta1, db, zb, mat, olcek=fit(db - da, zb - za, da, za))
    if tur == 'pen' and not kapali:
        klo, khi = (lo - 2, lo) if sgn < 0 else (hi, hi + 2)
        o1 = fit(28, zb - za, da - 34, za); o2 = fit(28, zb - za, db + 6, za)
        if eksen == 'x':
            H.kutu(da - 34, klo, za, da - 6, khi, zb, KEPENK, olcek=o1, detay=True)
            H.kutu(db + 6, klo, za, db + 34, khi, zb, KEPENK, olcek=o2, detay=True)
        else:
            H.kutu(klo, da - 34, za, khi, da - 6, zb, KEPENK, olcek=o1, detay=True)
            H.kutu(klo, db + 6, za, khi, db + 34, zb, KEPENK, olcek=o2, detay=True)
    elif not kapali:
        ic_c = c1 if ic > 0 else c0
        ilo, ihi = (ic_c, ic_c + 3) if ic > 0 else (ic_c - 3, ic_c)
        o = fit(56, 102, db + 2, TEMEL_Z)
        if eksen == 'x': H.kutu(db + 2, ilo, TEMEL_Z, db + 58, ihi, TEMEL_Z + 102, KAPI_M, olcek=o, detay=True)
        else: H.kutu(ilo, db + 2, TEMEL_Z, ihi, db + 58, TEMEL_Z + 102, KAPI_M, olcek=o, detay=True)
    if tur == 'kapi':
        # esik basamagi yerine RAMPA: motor yokus yukari basamakta yol bagi
        # kurmuyordu (metel yol_denetim olcumu) -> ev ici disaridan ulasilamaz adaydi
        if eksen == 'x':
            if sgn < 0: H.kama(da - 8, lo - 72, db + 8, lo, -16, 0, TEMEL_Z, '+y', GRI, GRI)
            else:       H.kama(da - 8, hi, db + 8, hi + 72, -16, 0, TEMEL_Z, '-y', GRI, GRI)
        else:
            if sgn < 0: H.kama(lo - 72, da - 8, lo, db + 8, -16, 0, TEMEL_Z, '+x', GRI, GRI)
            else:       H.kama(hi, da - 8, hi + 72, db + 8, -16, 0, TEMEL_Z, '-x', GRI, GRI)

def duvar(eksen, a, b, sabit, ic, delikler, dis_mat, ic_mat=IC, kapali=False):
    c0, c1 = (sabit, sabit + K) if ic > 0 else (sabit - K, sabit)
    if eksen == 'x':
        ic_yuz, dis_yuz = ('+y', '-y') if ic > 0 else ('-y', '+y')
    else:
        ic_yuz, dis_yuz = ('+x', '-x') if ic > 0 else ('-x', '+x')
    m = {'*': GRI, ic_yuz: ic_mat, dis_yuz: dis_mat}
    mt = {'*': TEMEL, ic_yuz: TEMEL if ic_mat != CAULK else CAULK}
    def parca(p0, p1, z0, z1, mats):
        if p1 <= p0 or z1 <= z0: return
        if eksen == 'x': H.kutu6(p0, c0, z0, p1, c1, z1, mats)
        else: H.kutu6(c0, p0, z0, c1, p1, z1, mats)
    p = a
    for d in sorted(delikler, key=lambda d: d[1]):
        if d[0] == 'kapi' and not kapali:
            parca(p, d[1], 0, TEMEL_Z, mt); p = d[2]
    parca(p, b, 0, TEMEL_Z, mt)
    p = a
    for (tur, da, db, za, zb) in sorted(delikler, key=lambda d: d[1]):
        parca(p, da, TEMEL_Z, DUVAR_Z, m)
        if tur == 'pen': parca(da, db, TEMEL_Z, za, m)
        parca(da, db, zb, DUVAR_Z, m)
        p = db
    parca(p, b, TEMEL_Z, DUVAR_Z, m)
    for (tur, da, db, za, zb) in delikler:
        acik_ekleri(eksen, ic, c0, c1, tur, da, db, za, zb, kapali)

def cati(x0, y0, x1, y1, z_alt, mat_yan, sacak=28, yuk=None):
    d = y1 - y0
    ust = z_alt + 8 + (yuk if yuk else min(120, d // 2))
    ym = (y0 + y1) / 2.0
    H.kama(x0 - sacak, y0 - sacak, x1 + sacak, ym, z_alt, z_alt + 8, ust, '+y', CATI, mat_yan, alt=GRI)
    H.kama(x0 - sacak, ym, x1 + sacak, y1 + sacak, z_alt, z_alt + 8, ust, '-y', CATI, mat_yan, alt=GRI)
    H.kutu(x0 - sacak, ym - 6, ust - 4, x1 + sacak, ym + 6, ust + 6, TRIM, detay=True)     # mahya
    # sacak alin tahtalari
    H.kutu(x0 - sacak, y0 - sacak - 2, z_alt - 6, x1 + sacak, y0 - sacak + 2, z_alt + 10, TRIM, detay=True)
    H.kutu(x0 - sacak, y1 + sacak - 2, z_alt - 6, x1 + sacak, y1 + sacak + 2, z_alt + 10, TRIM, detay=True)
    return ust

def kose_direkleri(x0, y0, x1, y1, z1):
    for (a, b) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        H.kutu(a - 10, b - 10, 0, a + 10, b + 10, z1, TRIM, detay=True)

def izba(ad, cx, cy, w, d, kapilar, pencereler, dis=DIS, esya=(), baca=True, acik=True, isikli=True):
    x0, x1 = cx - w // 2, cx + w // 2
    y0, y1 = cy - d // 2, cy + d // 2
    YAPILAR[ad] = (x0, y0, x1, y1, acik)
    dl = lambda yon: [kapi_d(m) for m in kapilar.get(yon, [])] + [pen_d(m) for m in pencereler.get(yon, [])]
    icm = IC if acik else CAULK
    H.kutu6(x0 + K, y0 + K, 0, x1 - K, y1 - K, TEMEL_Z, {'*': TEMEL, '+z': TABAN if acik else CAULK})
    duvar('x', x0, x1, y0, +1, dl('g'), dis, icm, not acik)
    duvar('x', x0, x1, y1, -1, dl('k'), dis, icm, not acik)
    duvar('y', y0 + K, y1 - K, x0, +1, dl('b'), dis, icm, not acik)
    duvar('y', y0 + K, y1 - K, x1, -1, dl('d'), dis, icm, not acik)
    H.kutu6(x0, y0, DUVAR_Z, x1, y1, DUVAR_Z + 8, {'*': GRI, '+z': CAULK, '-z': GRI if acik else CAULK})
    if acik:
        for kx in range(x0 + 96, x1 - 64, 112):
            H.kutu(kx, y0 + K, DUVAR_Z - 12, kx + 12, y1 - K, DUVAR_Z, KIRIS, detay=True)
    kose_direkleri(x0, y0, x1, y1, DUVAR_Z)
    ust = cati(x0, y0, x1, y1, DUVAR_Z + 8, dis)
    if baca:
        bx, by = x0 + K + 8, y1 - K - 56
        H.kutu(bx, by, TEMEL_Z if acik else DUVAR_Z, bx + 40, by + 40, ust + 40, TUGLA, detay=True)
    if acik:
        for (m, dx, dy, yaw) in esya:
            model(m, cx + dx, cy + dy, TEMEL_Z, yaw)
        if isikli:
            isik(cx, cy, DUVAR_Z - 30)
    return (x0, y0, x1, y1)

# ACIK evler (Alman savunuculari icin): ev1, ev3, ev4.  KAPALI (cephe): ev2, ev6.
izba('ev1', -1100, 700, 448, 320, {'g': [-1100]}, {'g': [-1260, -940], 'b': [700], 'd': [700]}, DIS,
     [('prop_potbelly_stove', -175, 100, 0), ('furniture_duhoc_table', 60, 30, 0),
      ('furniture_plainchair', 15, -10, 90), ('furniture_plainchair', 105, 75, 270),
      ('furniture_bed', 165, -90, 0), ('crate01_snow', -175, -100, 20)])
izba('ev3', -1350, -100, 384, 352, {'d': [-100]}, {'g': [-1350], 'k': [-1350], 'b': [-100]}, DIS3,
     [('prop_potbelly_stove', -145, 125, 0), ('furniture_sidetable1', 110, 135, 0),
      ('furniture_armchair', 110, -100, 200), ('furniture_bed', -120, -110, 0)])
izba('ev4', 950, 300, 416, 320, {'b': [300]}, {'g': [850, 1050], 'k': [950], 'd': [300]}, DIS,
     [('prop_stove02', -150, 105, 0), ('furniture_duhoc_table', 40, 0, 90),
      ('furniture_plainchair', 0, -45, 0), ('crate02_snow', 160, 105, 0),
      ('prop_barrel_black_snow', 165, -105, 0)])
izba('ev2', 250, 950, 384, 320, {'g': [250]}, {'g': [120, 380], 'd': [950], 'b': [950]}, DIS2, acik=False)
izba('ev6', 1350, 1000, 352, 288, {'g': [1350]}, {'b': [1000], 'g': [1450], 'd': [1000]}, DIS2, acik=False)

# --- kolhoz ambari: temiz ic (rampa/platform/at arabasi kaldirildi) ---
def ambar(cx, cy, w, d):
    x0, x1 = cx - w // 2, cx + w // 2
    y0, y1 = cy - d // 2, cy + d // 2
    YAPILAR['ambar'] = (x0, y0, x1, y1, True)
    yuksek = 256
    H.kutu6(x0 + K, y0 + K, 0, x1 - K, y1 - K, 8, {'*': TEMEL, '+z': TABAN})
    genis = lambda m: ('kapi', m - 88, m + 88, 8, 200)
    pen = lambda m: ('pen', m - 32, m + 32, 120, 176)
    def gduvar(eksen, a, b, sabit, ic, delikler):
        c0, c1 = (sabit, sabit + K) if ic > 0 else (sabit - K, sabit)
        if eksen == 'x': ic_yuz, dis_yuz = ('+y', '-y') if ic > 0 else ('-y', '+y')
        else: ic_yuz, dis_yuz = ('+x', '-x') if ic > 0 else ('-x', '+x')
        def bx(p0, p1, z0, z1, dis_m):
            if p1 <= p0 or z1 <= z0: return
            mm = {'*': GRI, ic_yuz: GRI, dis_yuz: dis_m}
            if eksen == 'x': H.kutu6(p0, c0, z0, p1, c1, z1, mm)
            else: H.kutu6(c0, p0, z0, c1, p1, z1, mm)
        p = a
        for (tur, da, db, za, zb) in sorted(delikler, key=lambda q: q[1]):
            for (z0, z1, mat) in ((0, 96, TUGLA), (96, yuksek, GRI)):
                bx(p, da, z0, z1, mat)
                if tur == 'pen' and min(z1, za) > z0: bx(da, db, z0, min(z1, za), mat)
                if z1 > max(z0, zb): bx(da, db, max(z0, zb), z1, mat)
            p = db
        for (z0, z1, mat) in ((0, 96, TUGLA), (96, yuksek, GRI)):
            bx(p, b, z0, z1, mat)
        for (tur, da, db, za, zb) in delikler:
            acik_ekleri(eksen, ic, c0, c1, tur, da, db, za, zb, False) if tur == 'pen' else None
    # genis kapilarin onune rampa (taban 8; yokus yukari yol bagi icin)
    H.kama(cx - 88, y0 - 72, cx + 88, y0, -16, 0, 8, '+y', GRI, GRI)
    H.kama(cx - 88, y1, cx + 88, y1 + 72, -16, 0, 8, '-y', GRI, GRI)
    gduvar('x', x0, x1, y0, +1, [genis(cx), pen(x0 + 130), pen(x1 - 130)])
    gduvar('x', x0, x1, y1, -1, [genis(cx), pen(x0 + 130), pen(x1 - 130)])
    gduvar('y', y0 + K, y1 - K, x0, +1, [pen(cy)])
    gduvar('y', y0 + K, y1 - K, x1, -1, [pen(cy)])
    H.kutu6(x0, y0, yuksek, x1, y1, yuksek + 8, {'*': GRI, '+z': CAULK})
    for kx in range(x0 + 96, x1 - 64, 128):
        H.kutu(kx, y0 + K, yuksek - 14, kx + 14, y1 - K, yuksek, KIRIS, detay=True)
    kose_direkleri(x0, y0, x1, y1, yuksek)
    cati(x0, y0, x1, y1, yuksek + 8, GRI, yuk=150)
    # genis kapi kanatlari: DISARIDA duvara yaslanmis (ici bos kalir)
    for (yy0, yy1) in ((y0 - 6, y0 - 2), (y1 + 2, y1 + 6)):
        H.kutu(cx + 96, yy0, 8, cx + 272, yy1, 200, KAPI_M, olcek=fit(176, 192, cx + 96, 8), detay=True)
        H.kutu(cx - 272, yy0, 8, cx - 96, yy1, 200, KAPI_M, olcek=fit(176, 192, cx - 272, 8), detay=True)
    # duzenli esya: samanlar kuzeydogu kosede istif, kasalar guneybatida
    for (m, dx, dy, yaw) in [('prop_haybale', 290, 150, 0), ('prop_haybale', 290, 95, 0),
                             ('prop_haybale', 230, 150, 0), ('prop_haybale', 290, 150, 90),
                             ('crate01_snow', -320, -150, 0), ('crate02_snow', -270, -150, 0),
                             ('crate01_snow', -320, -100, 0), ('prop_barrel_benzin_snow', -330, 150, 0),
                             ('prop_barrel_benzin_snow', -300, 165, 0)]:
        model(m, cx + dx, cy + dy, 8, yaw)
    isik(cx - 200, cy, yuksek - 40, 320, .5)
    isik(cx + 200, cy, yuksek - 40, 320, .5)

ambar(-250, -150, 768, 448)

# --- takviye deposu (acik; kapi KUZEYE, savunma hattindan gorulmez) ---
izba('depo', 1650, 1650, 352, 256, {'k': [1650]}, {}, GRI,
     [('crate01_snow', 130, 70, 0), ('crate02_snow', 130, 20, 15),
      ('prop_crate_dak3_russian', -130, 70, 0)], baca=False)

def kulube(x0, y0, w, d, h, mat):
    H.kutu(x0, y0, 0, x0 + w, y0 + 8, h, mat)
    H.kutu(x0, y0 + d - 8, 0, x0 + w, y0 + d, h, mat)
    H.kutu(x0, y0 + 8, 0, x0 + 8, y0 + d - 8, h, mat)
    H.kama(x0 - 12, y0 - 12, x0 + w + 12, y0 + d + 12, h, h + 6, h + 40, '+y', CATI, mat, alt=GRI)
kulube(-1700, 1150, 160, 128, 120, GRI)
kulube(700, 1250, 96, 96, 112, DIS3)
YAPILAR['odunluk'] = (-1700, 1150, -1540, 1278, False)
YAPILAR['hela'] = (700, 1250, 796, 1346, False)
YAPILAR['kuyu'] = (-64, 238, 64, 358, False)

# =========================================================================
# 5. CITLER, KUYU
# =========================================================================
CITLER = []
def cit(xa, ya, xb, yb):
    CITLER.append((xa, ya, xb, yb))
    L = math.hypot(xb - xa, yb - ya); n = max(1, int(L // 128))
    for i in range(n + 1):
        t = i / float(n); px, py = xa + (xb - xa) * t, ya + (yb - ya) * t
        H.kutu(px - 4, py - 4, 0, px + 4, py + 4, 64, GRI, detay=True)
    if xa == xb:
        y0, y1 = sorted((ya, yb))
        for z in (22, 46): H.kutu(xa - 2, y0, z, xa + 2, y1, z + 8, DIS3, detay=True)
    else:
        x0, x1 = sorted((xa, xb))
        for z in (22, 46): H.kutu(x0, ya - 2, z, x1, ya + 2, z + 8, DIS3, detay=True)

for c in [(-1600, 400, -700, 400), (-1600, 400, -1600, 1100), (-50, 620, 600, 620),
          (600, 620, 600, 1300), (-1750, -520, -1000, -520), (1100, -220, 1700, -220),
          (1700, -220, 1700, 600)]:
    cit(*c)

for (a, b, c, d) in [(-48, 250, 48, 266), (-48, 330, 48, 346), (-48, 266, -32, 330), (32, 266, 48, 330)]:
    H.kutu(a, b, 0, c, d, 40, TEMEL, detay=True)
H.kutu(-44, 294, 0, -36, 302, 128, GRI, detay=True)
H.kutu(36, 294, 0, 44, 302, 128, GRI, detay=True)
H.kutu(-44, 294, 104, 44, 302, 112, GRI, detay=True)
H.kama(-64, 238, 64, 298, 128, 134, 158, '+y', CATI, GRI, alt=GRI, detay=True)
H.kama(-64, 298, 64, 358, 128, 134, 158, '-y', CATI, GRI, alt=GRI, detay=True)

# =========================================================================
# 6. ORMAN: sinirin icinde bir sira + disinda sik bant (dunya devam ediyor)
# =========================================================================
random.seed(11)
CAM = ['tree_snow_pine_xl_c', 'tree_snow_pine_lg_c', 'tree_snow_pine_lg_c']
def halka(icerde, adim, sapma=80):
    """icerde > 0: sinirin icinde, < 0: disinda."""
    x0, x1, y0, y1 = PX0 + icerde, PX1 - icerde, PY0 + icerde, PY1 - icerde
    pts = []
    for x in range(int(x0), int(x1) + 1, adim): pts += [(x, y0), (x, y1)]
    for y in range(int(y0), int(y1) + 1, adim): pts += [(x0, y), (x1, y)]
    for (x, y) in pts:
        x += random.randint(-sapma, sapma); y += random.randint(-sapma, sapma)
        if yol_mesafe(x, y) < 300: continue
        if not (SX0 + 64 < x < SX1 - 64 and SY0 + 64 < y < SY1 - 64): continue
        model(random.choice(CAM), x, y, None, random.randint(0, 359))
halka(140, 340, 110)
for dis in (-200, -480, -780, -1080):
    halka(dis, 300, 120)
# yolun S kivrimini kapatan ek koru (harita disi)
for (cx, cy) in [(-3350, -1250), (-3250, -1500), (-3550, -1450), (-3150, -2600), (-3450, -2550)]:
    for k in range(5):
        model(random.choice(CAM), cx + random.randint(-160, 160), cy + random.randint(-160, 160),
              None, random.randint(0, 359))
for x in range(-2300, 2301, 220):
    for yy in (2330, 2480):
        model(random.choice(CAM + ['tree_snow_pine_sm_c']), x + random.randint(-60, 60),
              yy + random.randint(-70, 70), None, random.randint(0, 359))
for x in range(-2300, 2301, 240):
    px, py = x + random.randint(-60, 60), -2480 + random.randint(-90, 90)
    if yol_mesafe(px, py) > 300:
        model(random.choice(CAM), px, py, None, random.randint(0, 359))

for (x, y, m) in [(-1000, -1300, 'tree_destoyed_snow_trunk_a'), (900, -2000, 'tree_destoyed_snow_trunk_b'),
                  (-300, -2000, 'tree_destroyed_snow_stump_a'), (1500, -1400, 'tree_destroyed_snow_stump_a'),
                  (-1700, -2400, 'tree_destroyed_snow_fallen_log_a'), (600, -1600, 'brush_snowbushweed01'),
                  (-900, -800, 'brush_snowbushweed02'), (1200, -900, 'brush_snowbushweed01')]:
    model(m, x, y, None, random.randint(0, 359))
for x in range(-1300, -200, 112):
    model('military_sandbag_snow_longsection', x, -860, None, 0)
for x in range(260, 1400, 112):
    model('military_sandbag_snow_longsection', x, -860, None, 0)
for x in range(-1800, 1801, 400):
    if yol_mesafe(x, -1150) > 280:
        model('military_hedgehog', x, -1150, None, random.randint(0, 90))
# yol boyu telgraf direkleri (yolun kuzey kenari)
for (x, y) in [(-260, -1250), (-900, -1560), (-1600, -1600), (-2300, -1760)]:
    model('powerpole01', x, y, None, 0)
for x in range(-860, 861, 112):
    model('military_sandbag_snow_longsection', x, 1740, None, 180)
for (m, x, y, yaw) in [('haycart', -720, 170, 30), ('prop_haybale', -640, 280, 0),
                       ('prop_haybale', -580, 250, 40), ('crate01_snow', 520, 120, 0),
                       ('crate02_snow', 560, 60, 20), ('prop_barrel_benzin_snow', 600, 200, 0),
                       ('prop_barrel_black_snow', 640, 170, 0), ('powerpole01', -150, 1350, 0),
                       ('prop_firebarrel', 120, 1500, 0), ('crate01_snow', -1650, 1180, 0),
                       ('crate01_snow', -1620, 1230, 0)]:
    model(m, x, y, None, yaw)

# =========================================================================
# 7. BASLANGICIN SAGI: BOZUK, BARIKATLI YOL (gecilmez)
# Kullanici: "spawn olunca bizim sagimizda kalan yere gidilemesin, bozuk yol
# olsun". Toplanma cemberi (0,2780); oyuncu cemberin guneyinde kuzeye bakar
# -> sagi DOGU. x=420 hattinda barikat + clip_player.
# =========================================================================
BX = 420
H.kutu(BX + 40, 2860, 0, PX1, 3020, 3, YOL, detay=True)            # dogu'ya giden eski yol
for y in range(2380, PY1, 150):                                      # yikik barikat hatti
    m = ['tree_destroyed_snow_fallen_log_a', 'military_hedgehog', 'caen_barbedwire_3',
         'military_hedgehog', 'caen_barbedwire_5'][(y // 150) % 5]
    model(m, BX + random.randint(-30, 30), y + random.randint(-30, 30), None, random.randint(0, 179))
for (x, y, m) in [(BX + 160, 2940, 'vehicle_opel_blitz_snow_static'), (BX + 120, 2700, 'prop_rubble_rock_01'),
                  (BX + 200, 3120, 'prop_rubble_rock_03'), (BX + 90, 2560, 'tree_destoyed_snow_trunk_b')]:
    model(m, x, y, None, random.randint(0, 359))
H.kutu(BX - 8, 2350, -192, BX + 8, PY1, 1600, SINIR, SINIR, alt=SINIR)  # gorunmez duvar

# =========================================================================
# 8. GUNEYBATI DARALTMA (kullanici: "tankin kamyonun geldigi yolun o
# tarafina gecemeyelim"). x=-1500 / y=-600 L-seklinde gorunmez duvar;
# araclar ve Alman piyadesi gecer (clip_player yalniz oyuncuyu durdurur).
# Duvar boyunca dikenli tel + kirpi engel ki sinir dogal gorunsun.
# =========================================================================
H.kutu(-1508, PY0, -192, -1492, -600, 1600, SINIR, SINIR, alt=SINIR)
H.kutu(PX0, -608, -192, -1500, -592, 1600, SINIR, SINIR, alt=SINIR)
for y in range(-3150, -650, 170):
    if yol_mesafe(-1500, y) > 260:
        model(['caen_barbedwire_3', 'military_hedgehog', 'caen_barbedwire_5'][(y // 170) % 3],
              -1500 + random.randint(-20, 20), y, None, random.randint(0, 179))
for x in range(-2700, -1520, 170):
    model(['caen_barbedwire_5', 'military_hedgehog', 'caen_barbedwire_3'][(x // 170) % 3],
          x, -600 + random.randint(-20, 20), None, random.randint(0, 179))

# Kum torbasi + tank tuzagi hattinin otesine gecilmez (kullanici): kirpi
# engel sirasinin (y=-1150) hemen guneyinde haritayi boydan boya kesen
# gorunmez duvar. Tank y=-900'de durur -> duvarin KUZEYINDE, ulasilabilir.
H.kutu(PX0, -1268, -192, PX1, -1252, 1600, SINIR, SINIR, alt=SINIR)

H.ent('info_player_start', origin=(0, 2700, 8), angles=(0, 90, 0))

import ent_krasnoye
ent_krasnoye.yerlestir(sys.modules[__name__])

if __name__ == '__main__':
    r = H.yaz(os.path.join(KOK, 'map_source', 'krasnoye.map'))
    print('dunya brush/mesh: %(dunya_brush)d  entity: %(entity)d  bayt: %(bayt)d' % r)
    print('malzemeler:', r['malzeme'])
    n_model = sum(1 for d, _ in H.ents if d['classname'] == 'misc_model')
    print('misc_model: %d  light: %d' % (n_model, sum(1 for d, _ in H.ents if d['classname'] == 'light')))
    print('yol basi (dogus) z=%.0f  sinir disi ornek (-3400,-1350) z=%.0f' % (
        yukseklik(-3990, -1520), yukseklik(-3400, -1350)))
