# -*- coding: utf-8 -*-
"""
gen_burya.py -- CoD2 SP 'burya' (Operation Snowstorm / Kar Firtinasi, 2 Subat 1943).

Kroki (Desktop/Newmap/kroki.png, 1536x1024) BIREBIR: yerlesim kroki pikseliyle
yazilir, W(px, py) dunya birimine cevirir (1 px = 8 birim, kuzey = +Y).

  Guneybati : baslangic -- konvoy yolu harita disindaki vadiden gelir
  Orta      : uzun kivrimli orman yolu, dere + kopru, gozetleme kulesi (dekor)
  KD        : arac patlama noktasi (pusu), kamp girisi, buyuk Alman kampi
  Dogu      : kucuk karakol (dekor), takviye yolu (harita disindan, gizli)

Skill kurallari (cod2-map-maker): uc katman (gok kutusu, 650-750 sirt halkasi,
clip_player cokgeni); her yol harita disinda kivrilip tepenin arkasinda biter
(gok kutusuna >=1500); kapi 76 yuksek, pencere denizligi 46 ust 88, pencere
ici '+' ahsap kasa; her doku onizlendi; her model/malzeme iwd'de dogrulanir.
"""
import os, sys, math, random, zipfile, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kmap import Harita

KOK = r'F:\Activision\Call of Duty 2'
HARITA = 'burya'
S = 8.0

def W(px, py):
    return ((px - 600) * S, (450 - py) * S)

# ---------------------------------------------------------------- malzemeler (onizlendi)
KAR = 'stalingradwinter_snow01'
KAR2 = 'stalingradwinter_snow02'
YOL = 'stalingradwinter_slush1'
KAYA = 'd_cliff04'
TUGLA = 'stalingradwinter_brickwallsnow01'      # merkez bina dis (gercek tugla, onizlendi)
TEMEL = 'stalingradwinter_brick02'
SIVA = 'stalingradwinter_plaster01'
KORNIS = 'stalingradwinter_concretetrim01'
TABAN = 'stalingradwinter_wood_floor'
CATI = 'stalingradwinter_roof_slate01'
SAC = 'stalingradwinter_metal_roof'             # baraka catisi (pasli sac)
TAHTA = 'stalingradwinter_woodplank01'
TAHTA2 = 'stalingradwinter_woodplank02'
TAHTA3 = 'stalingradwinter_woodplank03'
GRI = 'stalingradwinter_greywood'               # baraka dis kaplama
CIT = 'mtl_fence_wood'                          # kamp citi (dikey kalas)
TRIM = 'stalingradwinter_wood_trim'
KIRIS = 'stalingrad_beam_side'
MOLOZ = 'stalingradwinter_rubblesnow01'
YANIK = 'stalingradwinter_wood_burnt01'
BETON = 'stalingradwinter_concrete01'
KAPI_M = 'mtl_caen_door_01'                     # gercek tek kanat kapi (256x512, onizlendi)
GOK = 'sky_tankhunt'
CAULK = 'caulk'
SINIR = 'clip_player'

H = Harita()
H.ws.update({'_color': '.90 .94 1', 'ambient': '.18', 'sunlight': '1.1',
             'sundirection': '-30 -125 0', 'sundiffusecolor': '.80 .86 .98',
             'suncolor': '.92 .95 1', 'diffusefraction': '.62',
             '-contrastgain': '.4', 'northyaw': '90'})

# ---------------------------------------------------------------- yardimcilar
def _seg(px, py, a, b):
    ax, ay = a; bx, by = b
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
    """hat boyunca m birim ilerideki nokta (x, y)."""
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
    """hat'in [m0, m1] parcasi, ~adim aralikli noktalar."""
    n = max(1, int((m1 - m0) // adim))
    return [hat_nokta(hat, m0 + (m1 - m0) * k / float(n)) for k in range(n + 1)]

# ---------------------------------------------------------------- sinir (oynanabilir cokgen)
SINIR_PX = [(70, 860), (30, 760), (80, 690), (170, 640), (250, 580), (330, 520), (400, 460), (470, 400),
            (560, 355), (640, 330), (700, 280), (750, 200), (780, 110), (820, 55), (1000, 40),
            (1150, 50), (1170, 200), (1155, 330), (1125, 430), (1105, 560), (1040, 615), (960, 605),
            (880, 565), (810, 530), (760, 480), (715, 560), (650, 615), (565, 660), (470, 705),
            (380, 760), (300, 820), (200, 880), (110, 905)]
POLI = [W(*p) for p in SINIR_PX]
SX0, SX1, SY0, SY1 = -6912, 7552, -5760, 5376            # gok kutusu (128 kati; uclara >=1500)
ZTAVAN = 3072

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

def disari(x, y):
    return 0.0 if icinde(x, y) else kenar_mes(x, y)

# ---------------------------------------------------------------- dere (K -> G, kroki)
# Kuzey ve guney uclar harita disinda kivrilip kanyon basiyla kapanir.
DERE_PX = [(545, 260), (585, 360), (632, 440), (640, 503), (648, 560), (700, 625), (770, 700)]
DERE = [W(*p) for p in DERE_PX]
DERE_TAM = [W(*p) for p in [(470, 165), (505, 190), (530, 225)]] + DERE + \
           [W(*p) for p in [(830, 760), (880, 790), (930, 795)]]

def dere_mes(x, y):
    return min(_seg(x, y, DERE_TAM[i], DERE_TAM[i + 1]) for i in range(len(DERE_TAM) - 1))

def dere_x(y):
    for i in range(len(DERE) - 1):
        (xa, ya), (xb, yb) = DERE[i], DERE[i + 1]
        if yb <= y <= ya:
            return lerp(xa, xb, (ya - y) / float(ya - yb))
    return DERE[0][0] if y > DERE[0][1] else DERE[-1][0]

DERE_TABAN = -300
DERE_IC, DERE_DIS = 80, 190
KOPRU_Y = [W(0, 503)[1]]                      # konvoy yolunun dereyi gectigi yer

# ---------------------------------------------------------------- kamp
KAMP = (1700, 1500, 4200, 3000)               # x0, y0, x1, y1 (cit ekseni)
KAPI_X = 2300                                 # ana giris (guney cit), 220 genis
ZK = None                                     # kamp duz zemin z (asagida hesaplanir)

# ---------------------------------------------------------------- yollar
# KONVOY YOLU: harita disinda baslar (vadide kivrilir), krokideki yoldan kamp
# girisine. Kopru kesiti dereyi dik (dogu-bati) gecer.
KONVOY_PX = [(-40, 760), (-20, 800), (15, 830), (60, 822), (100, 790), (170, 752), (240, 714),
             (320, 666), (400, 618), (480, 576), (548, 535), (602, 503), (678, 503), (720, 452),
             (760, 405), (797, 368), (830, 330), (862, 296), (887, 266), (887, 240)]
PATLAMA_PX = (797, 368)                       # arac patlama noktasi (kroki)
# TAKVIYE YOLU: doguda harita disindan (guneye kivrik vadi) kamp girisinin dogusuna
TAKVIYE_PX = [(1335, 560), (1350, 505), (1330, 455), (1280, 410), (1220, 385), (1150, 368),
              (1080, 345), (1010, 318), (955, 296), (925, 288)]
# ORMAN YOLU (dekor, kroki 'alternatif guzergah'): karakoldan guneybatiya, harita
# disinda kivrilip kapanir
ORMAN_YOLU_PX = [(1010, 540), (940, 585), (880, 620), (840, 660), (820, 710), (835, 760), (870, 790)]
GIRIS_PX = {'konvoy': KONVOY_PX[:6], 'takviye': TAKVIYE_PX[:6], 'orman': ORMAN_YOLU_PX[3:]}
GIRIS_W = {k: [W(*p) for p in v] for k, v in GIRIS_PX.items()}

def giris_mes(x, y):
    return min(_seg(x, y, L[i], L[i + 1]) for L in GIRIS_W.values() for i in range(len(L) - 1))

# ---------------------------------------------------------------- arazi
TEPE = [(W(250, 560), 420, 150), (W(420, 700), 380, 120), (W(330, 545), 300, 110),
        (W(520, 430), 380, 140), (W(700, 330), 320, 120), (W(880, 430), 360, 130),
        (W(980, 520), 300, 80), (W(160, 820), 300, 90), (W(1100, 360), 260, 90)]

def kamp_mes(x, y):
    x0, y0, x1, y1 = KAMP
    return math.hypot(max(x0 - x, x - x1, 0), max(y0 - y, y - y1, 0))

def zemin_ham(x, y):
    z = 0.0
    for ((cx, cy), r, hh) in TEPE:
        z += hh * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / float(r * r))
    z += 16 * math.sin(x / 410.0) * math.cos(y / 450.0)
    if icinde(x, y):
        z += 160 * ss(700, 0, kenar_mes(x, y))
    else:
        o = kenar_mes(x, y)
        dis_z = 160 + 540 * ss(0, 1100, o) + 70 * math.sin(x / 520.0) * math.cos(y / 610.0) * ss(0, 600, o)
        z += dis_z * (0.10 + 0.90 * ss(170, 540, giris_mes(x, y)))
    # kamp ve cevresi duz
    km = kamp_mes(x, y)
    if km < 520:
        z = lerp(ZK_DEGER, z, ss(160, 520, km))
    dx = dere_mes(x, y)
    if dx < DERE_DIS + 140:
        z = z * ss(DERE_DIS, DERE_DIS + 140, dx) + DERE_TABAN * ss(DERE_DIS, DERE_IC, dx)
    return z

ZK_DEGER = 40.0

# yol tanimlari: (px, py, z) ; z None -> ham arazi
YOLLAR = {
    'konvoy': ([(px, py, None) for (px, py) in KONVOY_PX[:-1]] + [(887, 240, ZK_DEGER)], 220),
    'takviye': ([(px, py, None) for (px, py) in TAKVIYE_PX[:-1]] + [(925, 288, None)], 190),
    'orman': ([(px, py, None) for (px, py) in ORMAN_YOLU_PX], 130),
    'kamp_ic': ([(887, 240, ZK_DEGER), (887, 200, ZK_DEGER), (930, 160, ZK_DEGER), (1010, 140, ZK_DEGER)], 200),
}

def _kopru_z():
    y = KOPRU_Y[0]
    xr = dere_x(y)
    return max(zemin_ham(xr - 320, y), zemin_ham(xr + 320, y), 0.0)

YOL_HAT = {}
for ad, (pts, gen) in YOLLAR.items():
    hat = []
    for (px, py, z) in pts:
        x, y = W(px, py)
        if z is None:
            z = zemin_ham(x, y)
            if dere_mes(x, y) < DERE_DIS + 150:          # kopru uclari (olculdu: 46'lik basamak agi boluyordu)
                z = _kopru_z()
        hat.append((x, y, float(z)))
    YOL_HAT[ad] = (hat, gen)

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
    d, yz, yg = yol_bilgi(x, y)
    if d < yg + 170:
        if dere_mes(x, y) < DERE_DIS + 20 and z < yz - 40:
            return z
        z = lerp(z, yz, ss(yg + 170, yg + 20, d))
    return z

# ---------------------------------------------------------------- gokyuzu
H.oda_kabugu(SX0, SY0, -512, SX1, SY1, ZTAVAN, 16, CAULK, GOK, GOK)

# ---------------------------------------------------------------- arazi mesh
A = 128
xs = list(range(SX0, SX1 + 1, A)); ys = list(range(SY0, SY1 + 1, A))
def dere_bandi(x0, x1):
    return any(x0 - DERE_DIS - 200 < px < x1 + DERE_DIS + 200 for (px, py) in
               [(lerp(a[0], b[0], t / 8.0), 0) for a, b in zip(DERE_TAM, DERE_TAM[1:]) for t in range(9)])
def duvar_mi(x0, x1, y0, y1):
    return all(dere_mes(x, y) <= DERE_DIS + 20 for x in (x0, x1) for y in (y0, (y0 + y1) / 2.0, y1))
ZH = {}
def zh(x, y):
    k = (x, y)
    if k not in ZH:
        ZH[k] = round(yukseklik(x, y), 2)
    return ZH[k]
PAR = 4
i0 = 0
while i0 < len(xs) - 1:
    i1 = min(i0 + PAR, len(xs) - 1)
    if dere_bandi(xs[i0], xs[i1]):
        i1 = i0 + 1
    for j0 in range(0, len(ys) - 1, PAR):
        j1 = min(j0 + PAR, len(ys) - 1)
        mat = KAYA if duvar_mi(xs[i0], xs[i1], ys[j0], ys[j1]) else KAR
        H.mesh([[(xs[i], ys[j], zh(xs[i], ys[j])) for j in range(j0, j1 + 1)]
                for i in range(i0, i1 + 1)], mat, doku=4.0 if mat == KAR else 2.0)
    i0 = i1
# dere suyu (oyuncu inemez; yalniz gorsel)
SU = 'water_hill400_assault'
SU_Z = DERE_TABAN + 230
for i in range(len(DERE_TAM) - 1):
    (xa, ya), (xb, yb) = DERE_TAM[i], DERE_TAM[i + 1]
    L = math.hypot(xb - xa, yb - ya); ux, uy = (xb - xa) / L, (yb - ya) / L
    if i == 0:
        xa, ya = xa - ux * 260, ya - uy * 260
    if i == len(DERE_TAM) - 2:
        xb, yb = xb + ux * 260, yb + uy * 260
    n = max(1, int(math.hypot(xb - xa, yb - ya) // 256))
    for k in range(n):
        t0, t1 = k / float(n), (k + 1) / float(n) + 0.02
        p0 = (lerp(xa, xb, t0), lerp(ya, yb, t0)); p1 = (lerp(xa, xb, min(t1, 1)), lerp(ya, yb, min(t1, 1)))
        g = 185
        nx, ny = -uy * g, ux * g
        q = [(p0[0] - nx, p0[1] - ny), (p1[0] - nx, p1[1] - ny), (p1[0] + nx, p1[1] + ny), (p0[0] + nx, p0[1] + ny)]
        z0, z1 = DERE_TABAN - 8, SU_Z
        yuz = [((q[0][0], q[0][1], z0), (q[1][0], q[1][1], z0), (q[2][0], q[2][1], z0)),
               ((q[0][0], q[0][1], z1), (q[1][0], q[1][1], z1), (q[2][0], q[2][1], z1))]
        for m in range(4):
            a_, b_ = q[m], q[(m + 1) % 4]
            yuz.append(((a_[0], a_[1], z0), (b_[0], b_[1], z0), (a_[0], a_[1], z1)))
        H.konveks(yuz, [CAULK, SU, CAULK, CAULK, CAULK, CAULK], olcek=(512, 512), detay=True)

def yol_mesh(hat, gen):
    orn = []
    for i in range(len(hat) - 1):
        (ax, ay, az), (bx, by, bz) = hat[i], hat[i + 1]
        n = max(1, int(math.hypot(bx - ax, by - ay) // 96))
        for k in range(n):
            t = k / float(n); orn.append((lerp(ax, bx, t), lerp(ay, by, t)))
    orn.append(hat[-1][:2])
    satirlar = []
    for k, (px, py) in enumerate(orn):
        a = orn[max(0, k - 1)]; b = orn[min(len(orn) - 1, k + 1)]
        ux, uy = b[0] - a[0], b[1] - a[1]; L = math.hypot(ux, uy) or 1; ux, uy = ux / L, uy / L
        qx, qy = -uy, ux
        s = []
        for w in (-gen / 2.0, 0, gen / 2.0):
            x, y = px + qx * w, py + qy * w
            s.append((round(x, 2), round(y, 2), round(yukseklik(x, y) + 3, 2)))
        satirlar.append(s)
    parca = []
    for s in satirlar:
        if dere_mes(s[1][0], s[1][1]) < DERE_DIS + 10:
            if len(parca) > 1:
                H.mesh(parca, YOL, doku=4.0, detay=True)
            parca = []
            continue
        parca.append(s)
        if len(parca) == 24:
            H.mesh(parca, YOL, doku=4.0, detay=True); parca = [s]
    if len(parca) > 1:
        H.mesh(parca, YOL, doku=4.0, detay=True)
for ad, (hat, gen) in YOL_HAT.items():
    if ad != 'kamp_ic':
        yol_mesh(hat, gen)

# ---------------------------------------------------------------- kayitlar
MODELLER = []      # (model, x, y)
KAYALAR = []       # (x, y, r)
YAPILAR = {}       # ad -> (x0, y0, x1, y1, girilir)
AGAC = []
DUVARLAR = []      # (xa, ya, xb, yb) cizgi engeller (cit)
DUVAR_KAPI = []    # (x, y, yaricap)

def model(m, x, y, z=None, yaw=0, kayit=True, sinif='misc_model', **kv):
    if m.startswith('tree_'):
        AGAC.append((x, y))
    if kayit:
        MODELLER.append((m, x, y))
    if z is None:
        z = yukseklik(x, y)
    return H.ent(sinif, model='xmodel/' + m, origin=(round(x, 1), round(y, 1), round(z, 1)),
                 angles=(0, yaw, 0), **kv)

def isik(x, y, z, r=260, i=.6, renk='1 0.80 0.52'):
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
    egim = (rnd.uniform(-0.55, 0.55), rnd.uniform(-0.55, 0.55))
    zu = zt + h
    tepe = [(x, y, zu), (x + 10, y, zu + egim[0] * 10), (x, y + 10, zu + egim[1] * 10)]
    yuz = [((x, y, zb), (x + 10, y, zb), (x, y + 10, zb)), tepe]
    mats = [CAULK, KAR]
    for k in range(N):
        yuz.append((alt[k], alt[(k + 1) % N], ust[k]))
        mats.append(KAYA)
    H.konveks(yuz, mats, olcek=(256, 256), detay=True)
    KAYALAR.append((x, y, r * 1.15))

def dikey_levha(a, b, z0, z1, mat, kalin=16, detay=False, olcek=None):
    (ax, ay), (bx, by) = a, b
    L = math.hypot(bx - ax, by - ay)
    nx, ny = -(by - ay) / L * kalin / 2.0, (bx - ax) / L * kalin / 2.0
    p = [(ax - nx, ay - ny), (bx - nx, by - ny), (bx + nx, by + ny), (ax + nx, ay + ny)]
    yuz = [((ax, ay, z0), (bx, by, z0), (ax + nx, ay + ny, z0)),
           ((ax, ay, z1), (bx, by, z1), (ax + nx, ay + ny, z1))]
    for k in range(4):
        q0, q1 = p[k], p[(k + 1) % 4]
        yuz.append(((q0[0], q0[1], z0), (q1[0], q1[1], z0), (q0[0], q0[1], z1)))
    H.konveks(yuz, [mat] * 6, olcek=olcek, detay=detay)

def kutu6(x0, y0, z0, x1, y1, z1, m, detay=False, olcek=None, hedef=None):
    if x1 > x0 and y1 > y0 and z1 > z0:
        H.kutu6(x0, y0, z0, x1, y1, z1, m, olcek=olcek, detay=detay, hedef=hedef)

# ---------------------------------------------------------------- gorunmez sinir
for i in range(len(POLI)):
    (ax, ay), (bx, by) = POLI[i], POLI[(i + 1) % len(POLI)]
    L = math.hypot(bx - ax, by - ay)
    n = max(1, int(L // 48))
    parca = []
    for k in range(n):
        t0, t1 = k / float(n), (k + 1) / float(n)
        p0 = (lerp(ax, bx, t0), lerp(ay, by, t0)); p1 = (lerp(ax, bx, t1), lerp(ay, by, t1))
        mx, my = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0
        parca.append((p0, p1, giris_mes(mx, my) < 240))
    j = 0
    while j < len(parca):
        k = j
        while k + 1 < len(parca) and parca[k + 1][2] == parca[j][2]:
            k += 1
        if not parca[j][2]:
            dikey_levha(parca[j][0], parca[k][1], -600, 2400, SINIR)
        j = k + 1
# dere kenarlari: oyuncu dereye inemez (kopru haric)
for kenar in (-1, 1):
    y = DERE[0][1]
    while y > DERE[-1][1]:
        y2 = y - 32
        if all(min(abs(y - yk), abs(y2 - yk)) >= 112 and not (y2 < yk < y) for yk in KOPRU_Y):
            a = (dere_x(y) + kenar * (DERE_DIS + 10), y)
            b = (dere_x(y2) + kenar * (DERE_DIS + 10), y2)
            dikey_levha(a, b, -600, 900, SINIR)
        y = y2

# ---------------------------------------------------------------- kopru
def kopru(yk):
    xr = dere_x(yk)
    z = _kopru_z()
    x0, x1 = xr - DERE_DIS - 80, xr + DERE_DIS + 80
    g = 124
    H.kutu(x0, yk - g, z - 14, x1, yk + g, z + 2, TAHTA, TAHTA3, alt=TAHTA3)
    for xx in range(int(x0) + 24, int(x1) - 16, 64):
        H.kutu(xx, yk - g + 4, z + 2, xx + 40, yk + g - 4, z + 4, TAHTA2, TAHTA2, detay=True)
    for yy in (yk - g, yk + g - 8):
        for xx in range(int(x0), int(x1) + 1, 128):
            H.kutu(xx, yy, z + 2, xx + 8, yy + 8, z + 50, TAHTA3, detay=True)
        H.kutu(x0, yy, z + 42, x1, yy + 8, z + 50, TRIM, detay=True)
        H.kutu(x0, yy, z + 22, x1, yy + 8, z + 28, TRIM, detay=True)
    for xx in (xr - 120, xr + 112):
        for yy in (yk - g + 8, yk + g - 24):
            H.kutu(xx, yy, DERE_TABAN - 10, xx + 16, yy + 16, z - 14, TAHTA3, detay=True)
    H.kutu(x0, yk - g - 8, z + 2, x1, yk - g, z + 120, SINIR, SINIR, alt=SINIR)
    H.kutu(x0, yk + g, z + 2, x1, yk + g + 8, z + 120, SINIR, SINIR, alt=SINIR)
    YAPILAR['kopru'] = (x0, yk - g - 8, x1, yk + g + 8, True)
    return z
KOPRU_Z = [kopru(yk) for yk in KOPRU_Y]

# =========================================================================
# BINA YAPICI -- olculer kullanici sartlari:
#   kapi 52 x 76 (insan 72 ~ 1.80 m -> kapi ~1.90 m), kanat 10 kalin
#   pencere denizligi taban+46 (comelen gormez, ayaktaki basi gorunur), ust +88,
#   genislik 52; icinde '+' ahsap kasa (3 birim citalar, detail)
# =========================================================================
K = 16
KAPI_G, KAPI_H = 52, 76
PEN_G, PEN_ALT, PEN_UST = 52, 46, 88

def delikli_duvar(eksen, a, b, c0, c1, z0, z1, delikler, m, hedef=None):
    """eksen 'x': duvar x boyunca (a..b), kalinlik y=c0..c1. delik: (da, db, za, zb)."""
    def bx(p0, p1, q0, q1):
        if eksen == 'x': kutu6(p0, c0, q0, p1, c1, q1, m, hedef=hedef)
        else: kutu6(c0, p0, q0, c1, p1, q1, m, hedef=hedef)
    p = a
    for (da, db, za, zb) in sorted(delikler):
        bx(p, da, z0, z1)
        bx(da, db, z0, za)
        bx(da, db, zb, z1)
        p = db
    bx(p, b, z0, z1)

def pencere_kasa(eksen, c0, c1, da, db, za, zb, hedef=None):
    """'+' bicimli ahsap kasa: ortada dikey + yatay cita, duvar kalinliginin ortasinda."""
    cm = (c0 + c1) / 2.0
    xm, zm = (da + db) / 2.0, (za + zb) / 2.0
    def bx(p0, p1, q0, q1):
        if eksen == 'x': kutu6(p0, cm - 2, q0, p1, cm + 2, q1, {'*': TRIM}, detay=True, hedef=hedef)
        else: kutu6(cm - 2, p0, q0, cm + 2, p1, q1, {'*': TRIM}, detay=True, hedef=hedef)
    bx(xm - 1.5, xm + 1.5, za, zb)
    bx(da, xm - 1.5, zm - 1.5, zm + 1.5)
    bx(xm + 1.5, db, zm - 1.5, zm + 1.5)

def kapi_kanati(eksen, c0, c1, da, db, z0, hedef=None):
    """statik (acilmaz) kapi: 10 kalin, gercek kapi dokusu kanada oturtulur."""
    cm = (c0 + c1) / 2.0
    m = {'*': TRIM}
    if eksen == 'x':
        m.update({'-y': KAPI_M, '+y': KAPI_M})
        kutu6(da, cm - 5, z0, db, cm + 5, z0 + KAPI_H, m, olcek=(db - da, KAPI_H, da, -z0), hedef=hedef)
    else:
        m.update({'-x': KAPI_M, '+x': KAPI_M})
        kutu6(cm - 5, da, z0, cm + 5, db, z0 + KAPI_H, m, olcek=(db - da, KAPI_H, da, -z0), hedef=hedef)

def cati_ust(x0, y0, x1, y1, z_alt, mat, yuk=110, sacak=32, yon='y', hedef=None):
    if yon == 'y':
        ym = (y0 + y1) / 2.0
        H.kama(x0 - sacak, y0 - sacak, x1 + sacak, ym, z_alt, z_alt + 8, z_alt + yuk, '+y', mat, TRIM, alt=TRIM, hedef=hedef)
        H.kama(x0 - sacak, ym, x1 + sacak, y1 + sacak, z_alt, z_alt + 8, z_alt + yuk, '-y', mat, TRIM, alt=TRIM, hedef=hedef)
        for (ya, yb) in ((y0, y0 + K), (y1 - K, y1)):
            pass
        # uc kalkanlar (basamakli)
        for (xa, xb) in ((x0, x0 + K), (x1 - K, x1)):
            for k in range(5):
                dz = yuk * k / 5.0
                yy = (ym - y0) * k / 5.0
                kutu6(xa, y0 + yy, z_alt + dz, xb, y1 - yy, z_alt + dz + yuk / 5.0 + 2, {'*': GRI_KALKAN}, hedef=hedef)
    else:
        xm = (x0 + x1) / 2.0
        H.kama(x0 - sacak, y0 - sacak, xm, y1 + sacak, z_alt, z_alt + 8, z_alt + yuk, '+x', mat, TRIM, alt=TRIM, hedef=hedef)
        H.kama(xm, y0 - sacak, x1 + sacak, y1 + sacak, z_alt, z_alt + 8, z_alt + yuk, '-x', mat, TRIM, alt=TRIM, hedef=hedef)
        for (ya, yb) in ((y0, y0 + K), (y1 - K, y1)):
            for k in range(5):
                dz = yuk * k / 5.0
                xx = (xm - x0) * k / 5.0
                kutu6(x0 + xx, ya, z_alt + dz, x1 - xx, yb, z_alt + dz + yuk / 5.0 + 2, {'*': GRI_KALKAN}, hedef=hedef)
GRI_KALKAN = GRI

def supurgelik(eksen, yuz, yon, a, b, zf, bosluklar, hedef=None):
    """ic duvar dibi 3 kalin 12 yuksek ahsap seridi (kapi acikliklari atlanir)."""
    p = a
    for (g0, g1) in sorted(bosluklar) + [(b, b)]:
        if g0 > p + 1:
            if eksen == 'x':
                y0_, y1_ = (yuz, yuz + 3) if yon > 0 else (yuz - 3, yuz)
                kutu6(p, y0_, zf, g0, y1_, zf + 12, {'*': TRIM}, detay=True, hedef=hedef)
            else:
                x0_, x1_ = (yuz, yuz + 3) if yon > 0 else (yuz - 3, yuz)
                kutu6(x0_, p, zf, x1_, g0, zf + 12, {'*': TRIM}, detay=True, hedef=hedef)
        p = max(p, g1)

def kapi_rampasi(yon, m, x0, y0, x1, y1, zt, boy=72):
    """taban disaridan 16 yuksek: AI 16'lik basamakta yokus yukari bag kurmaz
    (olculen kural) -> kapi onune rampa."""
    g = KAPI_G / 2.0 + 16
    za = zt - 18
    if yon == 'g': H.kama(m - g, y0 - boy, m + g, y0, za - 30, za, zt, '+y', TEMEL, TEMEL, alt=CAULK)
    elif yon == 'k': H.kama(m - g, y1, m + g, y1 + boy, za - 30, za, zt, '-y', TEMEL, TEMEL, alt=CAULK)
    elif yon == 'b': H.kama(x0 - boy, m - g, x0, m + g, za - 30, za, zt, '+x', TEMEL, TEMEL, alt=CAULK)
    else: H.kama(x1, m - g, x1 + boy, m + g, za - 30, za, zt, '-x', TEMEL, TEMEL, alt=CAULK)

def tahta_kapak(yon, eks, c0, c1, m, z0):
    """kapali binanin penceresi: delik yok; dis yuzde cakili tahta kapak + cerceve."""
    a, b, za, zb = m - PEN_G / 2.0 - 4, m + PEN_G / 2.0 + 4, z0 + PEN_ALT - 4, z0 + PEN_UST + 4
    dis = c0 if yon in ('g', 'b') else c1
    s_ = -1 if yon in ('g', 'b') else 1
    lo, hi = (dis - 3, dis) if s_ < 0 else (dis, dis + 3)
    lo2, hi2 = (dis - 5, dis - 3) if s_ < 0 else (dis + 3, dis + 5)
    if eks == 'x':
        kutu6(a, lo, za, b, hi, zb, {'*': TRIM, '-y': TAHTA3, '+y': TAHTA3}, detay=True)
        kutu6(a, lo2, za + 18, b, hi2, za + 26, {'*': YANIK}, detay=True)
    else:
        kutu6(lo, a, za, hi, b, zb, {'*': TRIM, '-x': TAHTA3, '+x': TAHTA3}, detay=True)
        kutu6(lo2, a, za + 18, hi2, b, za + 26, {'*': YANIK}, detay=True)

def ev(ad, x0, y0, x1, y1, zt, h, acikliklar, dis_m, ic_m, cati_m, girilir=True, hedef=None,
       cati_yon='y', taban=True):
    """Tek katli bina. acikliklar: {'g'/'k'/'b'/'d': [('kapi'|'kapali'|'pen', merkez), ...]}
    merkez: duvar boyunca dunya koordinati (x ya da y)."""
    if taban:
        kutu6(x0, y0, zt - 40, x1, y1, zt, {'*': TEMEL, '+z': TABAN}, hedef=hedef)
    z0, z1 = zt, zt + h
    M = lambda ic, dis: {'*': dis_m, ic: ic_m, dis: dis_m}
    duvar = {'g': ('x', x0, x1, y0, y0 + K, '+y', '-y'), 'k': ('x', x0, x1, y1 - K, y1, '-y', '+y'),
             'b': ('y', y0 + K, y1 - K, x0, x0 + K, '+x', '-x'), 'd': ('y', y0 + K, y1 - K, x1 - K, x1, '-x', '+x')}
    ic_bosluk = {}
    for yon, (eks, a, b, c0, c1, ic, dis) in duvar.items():
        dl, bos = [], []
        for (tur, m) in acikliklar.get(yon, []):
            if tur in ('kapi', 'kapali'):
                dl.append((m - KAPI_G / 2.0, m + KAPI_G / 2.0, z0, z0 + KAPI_H))
                bos.append((m - KAPI_G / 2.0, m + KAPI_G / 2.0))
                if tur == 'kapi':
                    kapi_rampasi(yon, m, x0, y0, x1, y1, zt)
                if tur == 'kapali':
                    kapi_kanati(eks, c0, c1, m - KAPI_G / 2.0, m + KAPI_G / 2.0, z0, hedef=hedef)
            elif girilir:
                dl.append((m - PEN_G / 2.0, m + PEN_G / 2.0, z0 + PEN_ALT, z0 + PEN_UST))
                pencere_kasa(eks, c0, c1, m - PEN_G / 2.0, m + PEN_G / 2.0, z0 + PEN_ALT, z0 + PEN_UST, hedef=hedef)
            else:
                tahta_kapak(yon, eks, c0, c1, m, z0)
        delikli_duvar(eks, a, b, c0, c1, z0, z1, dl, M(ic, dis), hedef=hedef)
        ic_bosluk[yon] = bos
    # tavan + cati
    kutu6(x0, y0, z1, x1, y1, z1 + 12, {'*': TRIM, '-z': ic_m, '+z': CAULK}, hedef=hedef)
    cati_ust(x0, y0, x1, y1, z1 + 12, cati_m, yon=cati_yon, hedef=hedef)
    if girilir:
        supurgelik('x', y0 + K, +1, x0 + K, x1 - K, zt, ic_bosluk['g'], hedef)
        supurgelik('x', y1 - K, -1, x0 + K, x1 - K, zt, ic_bosluk['k'], hedef)
        supurgelik('y', x0 + K, +1, y0 + K, y1 - K, zt, ic_bosluk['b'], hedef)
        supurgelik('y', x1 - K, -1, y0 + K, y1 - K, zt, ic_bosluk['d'], hedef)
        # tavan kirisleri
        uzun_x = (x1 - x0) >= (y1 - y0)
        if uzun_x:
            for xx in range(int(x0) + 120, int(x1) - 60, 160):
                kutu6(xx, y0 + K, z1 - 10, xx + 10, y1 - K, z1, {'*': KIRIS}, detay=True, hedef=hedef)
        else:
            for yy in range(int(y0) + 120, int(y1) - 60, 160):
                kutu6(x0 + K, yy, z1 - 10, x1 - K, yy + 10, z1, {'*': KIRIS}, detay=True, hedef=hedef)
    YAPILAR[ad] = (x0, y0, x1, y1, girilir)

# =========================================================================
# KAMP ZEMINI, CIT, KULELER
# =========================================================================
ZK = ZK_DEGER
kx0, ky0, kx1, ky1 = KAMP
CIT_H = 120                                   # ~3 m
def cit(a, b, kapilar=()):
    """dikey kalas cit (16 kalin), kapi bosluklari (merkez, genislik)."""
    (ax, ay), (bx, by) = a, b
    yatay = abs(by - ay) < 1
    p = ax if yatay else ay
    son = bx if yatay else by
    for (m, g) in sorted(kapilar) + [(son + 1e6, 0)]:
        e = min(m - g / 2.0, son)
        if e > p:
            if yatay:
                kutu6(p, ay - 8, ZK - 40, e, ay + 8, ZK + CIT_H, {'*': CIT, '+z': TRIM}, olcek=(48, 192))
                for xx in range(int(p), int(e), 192):
                    kutu6(xx, ay - 14, ZK - 40, xx + 12, ay + 14, ZK + CIT_H + 16, {'*': KIRIS}, detay=True)
            else:
                kutu6(ax - 8, p, ZK - 40, ax + 8, e, ZK + CIT_H, {'*': CIT, '+z': TRIM}, olcek=(48, 192))
                for yy in range(int(p), int(e), 192):
                    kutu6(ax - 14, yy, ZK - 40, ax + 14, yy + 12, ZK + CIT_H + 16, {'*': KIRIS}, detay=True)
        p = m + g / 2.0
        if p > son:
            break
    DUVARLAR.append((ax, ay, bx, by))
cit((kx0, ky0), (kx1, ky0), [(KAPI_X, 220)])
cit((kx0, ky1), (kx1, ky1))
cit((kx0, ky0), (kx0, ky1))
cit((kx1, ky0), (kx1, ky1))
DUVAR_KAPI.append((KAPI_X, ky0, 140))
# kapi direkleri ve ust kemer (tahta)
for xx in (KAPI_X - 126, KAPI_X + 110):
    kutu6(xx, ky0 - 16, ZK - 40, xx + 16, ky0 + 16, ZK + 190, {'*': KIRIS})
    KAYALAR.append((xx + 8, ky0, 16))
kutu6(KAPI_X - 126, ky0 - 10, ZK + 170, KAPI_X + 126, ky0 + 10, ZK + 190, {'*': KIRIS}, detay=True)

KULE = []                    # (x, y, platform z, yon, rampa ust x, rampa alt x)
def kule(cx, cy, yon):
    """ahsap gozetleme kulesi: 4 ayak, platform (ZK+180), korkuluk, cati.
    Merdiven cit boyunca (yon -1 bati, +1 dogu): olculdu -- kuzeye uzanan
    merdiven kapi ici alani binadan ayirip ada yapiyordu. Kulenin alti bos
    (yalniz ayaklar engel): AI altindan gecer."""
    zp = ZK + 180
    w = 80
    for (dx, dy) in ((-w, -w), (w - 14, -w), (-w, w - 14), (w - 14, w - 14)):
        kutu6(cx + dx, cy + dy, ZK - 20, cx + dx + 14, cy + dy + 14, zp + 140, {'*': KIRIS})
        KAYALAR.append((cx + dx + 7, cy + dy + 7, 12))
    kutu6(cx - w, cy - w, zp - 12, cx + w, cy + w, zp, {'*': TRIM, '+z': TAHTA2})
    # korkuluk: merdiven tarafinda (x = cx + yon*w) ortada 46'lik gecit
    kutu6(cx - w, cy - w, zp, cx + w, cy - w + 6, zp + 44, {'*': TAHTA3}, detay=True)
    kutu6(cx - w, cy + w - 6, zp, cx + w, cy + w, zp + 44, {'*': TAHTA3}, detay=True)
    for sx in (-1, 1):
        xa, xb = (cx - w, cx - w + 6) if sx < 0 else (cx + w - 6, cx + w)
        if sx == yon:
            kutu6(xa, cy - w + 6, zp, xb, cy - 23, zp + 44, {'*': TAHTA3}, detay=True)
            kutu6(xa, cy + 23, zp, xb, cy + w - 6, zp + 44, {'*': TAHTA3}, detay=True)
        else:
            kutu6(xa, cy - w + 6, zp, xb, cy + w - 6, zp + 44, {'*': TAHTA3}, detay=True)
    H.kama(cx - w - 16, cy - w - 16, cx + w + 16, cy + w + 16, zp + 140, zp + 146, zp + 190, '+y', SAC, TRIM, alt=TRIM)
    # MG siperi: guney korkulugunun icinde kum torbasi/sandik kutusu (taret bunun ustunde)
    kutu6(cx - 40, cy - w + 6, zp, cx + 40, cy - w + 30, zp + 34, {'*': MOLOZ, '+z': TAHTA2})
    # merdiven: 12 basamak (15 yuksek, 20 kosu) + caulk rampa; basamaklar rampanin altinda
    L = 12 * 20 + 24
    if yon > 0:
        rx_ust, rx_alt = cx + w, cx + w + L
    else:
        rx_ust, rx_alt = cx - w, cx - w - L
    rampa = lambda x: ZK + 1 + (zp - ZK - 1) * (rx_alt - x) / float(rx_alt - rx_ust)
    for k in range(12):
        xa = rx_ust + yon * k * 20
        xb = xa + yon * 20
        uz = xb if abs(rampa(xb) - ZK) < abs(rampa(xa) - ZK) else xa
        zt_ = rampa(uz) - 1
        kutu6(min(xa, xb), cy - 23, zt_ - 6, max(xa, xb), cy + 23, zt_, {'*': TRIM, '+z': TAHTA2}, detay=True)
    if yon > 0:
        H.kama(rx_ust, cy - 23, rx_alt, cy + 23, ZK, ZK + 1, zp, '-x', CAULK, CAULK, alt=CAULK, detay=True)
    else:
        H.kama(rx_alt, cy - 23, rx_ust, cy + 23, ZK, ZK + 1, zp, '+x', CAULK, CAULK, alt=CAULK, detay=True)
    # merdiven ve cit arasi seridi (olu alan) de dugumsuz
    YAPILAR['kule_merd_%d' % cx] = (min(rx_ust, rx_alt), ky0, max(rx_ust, rx_alt), cy + 27, False)
    KULE.append((cx, cy, zp, yon, rx_ust, rx_alt))
kule(KAPI_X - 240, ky0 + 100, -1)
kule(KAPI_X + 240, ky0 + 100, 1)
# kule projektorleri: kulenin kuzey dibinde
for (cx, cy, zp, _y, _a, _b) in KULE:
    model('light_flaksheinwerfer_on', cx, cy + 150, ZK, 180)

# =========================================================================
# MERKEZ BINA (BOMBA HEDEFI) -- iki katli tugla; SAGLAM hali script_brushmodel
# 'bina_saglam' (patlamada silinir), YIKIK hali 'bina_yikik' +2000 yukarida
# (yol agi sagliklandan hesaplanir; patlamada indirilir).
# =========================================================================
BX0, BY0, BX1, BY1 = 2500, 1980, 3500, 2620
BZ = ZK + 16                                    # zemin kat dosemesi ustu. Deney haritasi (kr_deney) olcusu: +4 taban disaridan iceri bagi KESIYOR, +16 rampasiz iki yonlu
BZU = BZ + 160                                  # ust kat dosemesi ustu (doseme 144..160)
BZT = BZU + 144                                 # ust kat tavani alti
MERD = (2540, 2100, 2620, 2420)                 # merdiven (bati, kuzeye yukselir) x0 y0 x1 y1
BOMBA = (3000, 2300)
ENGEL_KAYDIR = 2000
saglam = []
yikik = []
# BETON AVLU (brush, mesh'in 1 ustunde): deney haritasi (kr_deney) olcusu --
# arazi MESH'inden 16'lik brush tabana yokus yukari yol bagi KURULMUYOR; brush
# zeminden kuruluyor. Bina cevresi brush avlu -> kapilar iki yonlu.
kutu6(BX0 - 200, BY0 - 200, ZK - 40, BX1 + 200, BY1 + 200, ZK + 1, {'*': TEMEL, '+z': BETON})
# zemin doseme ve temel (DUNYA: patlamadan sonra da kalir)
kutu6(BX0, BY0, ZK - 40, BX1, BY1, BZ, {'*': TEMEL, '+z': BETON})
def b_pen(m, kat):
    za = (BZ if kat == 0 else BZU) + PEN_ALT
    return (m - PEN_G / 2.0, m + PEN_G / 2.0, za, za - PEN_ALT + PEN_UST)
def b_kapi(m):
    return (m - KAPI_G / 2.0, m + KAPI_G / 2.0, BZ, BZ + KAPI_H)
# kapi rampalari: arazi MESH'inden 16'lik brush tabana yokus yukari bag kurulmuyor
# (olculdu: baraka rampali iki yonlu, bina rampasiz tek yonlu)
for (yon_, m_) in (('g', 3000), ('k', 2800), ('d', 2300)):
    kapi_rampasi(yon_, m_, BX0, BY0, BX1, BY1, BZ)
B_DELIK = {
    'g': [b_kapi(3000)] + [b_pen(x, k) for x in (2650, 2800, 3200, 3350) for k in (0, 1)] + [b_pen(3000, 1)],
    'k': [b_kapi(2800)] + [b_pen(x, k) for x in (2650, 3100, 3350) for k in (0, 1)],
    'b': [b_pen(y, k) for y in (2150, 2450) for k in (0, 1)],
    'd': [b_kapi(2300)] + [b_pen(y, k) for y in (2120, 2480) for k in (0, 1)] + [b_pen(2300, 1)],
}
BDIS = lambda ic, dis: {'*': TUGLA, ic: SIVA, dis: TUGLA}
for (z0, z1) in ((BZ, BZU), (BZU, BZT + 16)):
    sec = lambda L: [d for d in L if d[2] < z1 and d[3] > z0]
    hd = None if z0 == BZ else saglam
    delikli_duvar('x', BX0, BX1, BY0, BY0 + K, z0, z1, sec(B_DELIK['g']), BDIS('+y', '-y'), hedef=hd)
    delikli_duvar('x', BX0, BX1, BY1 - K, BY1, z0, z1, sec(B_DELIK['k']), BDIS('-y', '+y'), hedef=hd)
    delikli_duvar('y', BY0 + K, BY1 - K, BX0, BX0 + K, z0, z1, sec(B_DELIK['b']), BDIS('+x', '-x'), hedef=hd)
    delikli_duvar('y', BY0 + K, BY1 - K, BX1 - K, BX1, z0, z1, sec(B_DELIK['d']), BDIS('-x', '+x'), hedef=hd)
for yon, L in B_DELIK.items():
    for (da, db, za, zb) in L:
        if zb - za > KAPI_H - 1:
            continue
        hd = None if za < BZU else saglam
        if yon == 'g': pencere_kasa('x', BY0, BY0 + K, da, db, za, zb, hedef=hd)
        elif yon == 'k': pencere_kasa('x', BY1 - K, BY1, da, db, za, zb, hedef=hd)
        elif yon == 'b': pencere_kasa('y', BX0, BX0 + K, da, db, za, zb, hedef=hd)
        else: pencere_kasa('y', BX1 - K, BX1, da, db, za, zb, hedef=hd)
# kornis
for (a, b, c, d) in ((BX0 - 6, BY0 - 6, BX1 + 6, BY0), (BX0 - 6, BY1, BX1 + 6, BY1 + 6),
                     (BX0 - 6, BY0, BX0, BY1), (BX1, BY0, BX1 + 6, BY1)):
    kutu6(a, b, BZU - 12, c, d, BZU + 2, {'*': KORNIS}, detay=True, hedef=saglam)
# ara doseme (merdiven boslugu acik)
mx0, my0, mx1, my1 = MERD
dm = {'*': TRIM, '+z': TABAN, '-z': SIVA}
kutu6(BX0 + K, BY0 + K, BZU - 16, mx0, BY1 - K, BZU, dm, hedef=saglam)
kutu6(mx1, BY0 + K, BZU - 16, BX1 - K, BY1 - K, BZU, dict(dm, **{'-x': SIVA}), hedef=saglam)
kutu6(mx0, BY0 + K, BZU - 16, mx1, my0, BZU, dict(dm, **{'+y': SIVA}), hedef=saglam)
kutu6(mx0, my1, BZU - 16, mx1, BY1 - K, BZU, dict(dm, **{'-y': SIVA}), hedef=saglam)
# tavan + cati
kutu6(BX0, BY0, BZT, BX1, BY1, BZT + 16, {'*': TRIM, '-z': SIVA, '+z': CAULK}, hedef=saglam)
H.kama(BX0 - 40, BY0 - 40, BX1 + 40, (BY0 + BY1) / 2.0, BZT + 16, BZT + 24, BZT + 186, '+y', CATI, TRIM, alt=TRIM, hedef=saglam)
H.kama(BX0 - 40, (BY0 + BY1) / 2.0, BX1 + 40, BY1 + 40, BZT + 16, BZT + 24, BZT + 186, '-y', CATI, TRIM, alt=TRIM, hedef=saglam)
for (xa, xb) in ((BX0, BX0 + K), (BX1 - K, BX1)):
    for k in range(6):
        dz = 170 * k / 6.0
        yy = ((BY1 - BY0) / 2.0) * k / 6.0
        kutu6(xa, BY0 + yy, BZT + 16 + dz, xb, BY1 - yy, BZT + 16 + dz + 30, {'*': TUGLA}, hedef=saglam)
for (cx_, cy_) in ((BX0 + 160, BY1 - 160), (BX1 - 200, BY0 + 160)):
    kutu6(cx_, cy_, BZT + 16, cx_ + 48, cy_ + 48, BZT + 240, {'*': TUGLA}, detay=True, hedef=saglam)
# ic duvar: zemin katta dogu oda (komuta) -- kapi 52x76; ust katta iki oda
IX = 3150
delikli_duvar('y', BY0 + K, BY1 - K, IX - 6, IX + 6, BZ, BZU - 16, [(2300 - 26, 2300 + 26, BZ, BZ + KAPI_H)], {'*': SIVA})
delikli_duvar('y', BY0 + K, BY1 - K, IX - 6, IX + 6, BZU, BZT, [(2300 - 26, 2300 + 26, BZU, BZU + KAPI_H)], {'*': SIVA}, hedef=saglam)
# merdiven: 10 basamak x 16 yukselti, kuzeye + gorunmez caulk rampa
n = 10
kosu = (my1 - my0) / float(n)
for k in range(n):
    yb = my0 + k * kosu
    zt_ = BZ + (k + 1) * (BZU - BZ) / float(n)
    kutu6(mx0, yb, BZ, mx1, my1 if k == n - 1 else yb + kosu, zt_, {'*': TRIM, '+z': TABAN, '-y': TRIM},
          olcek=(mx1 - mx0, kosu, -mx0, -yb))
_kosu = kosu
_r0, _r1 = my0 - _kosu, my0 + (n - 1) * _kosu
H.kama(mx0, _r0, mx1, _r1, BZ, BZ + 1, BZU, '+y', CAULK, CAULK, alt=CAULK, detay=True)
MERD_Z = lambda y: BZ + (BZU - BZ) * max(0.0, min(1.0, (y - _r0) / (_r1 - _r0)))
# merdiven boslugu korkulugu (oyuncu duseme sinirinda)
kutu6(mx1, my0, BZU, mx1 + 6, my1, BZU + 40, {'*': TRIM}, detay=True, hedef=saglam)
# supurgelik + kirisler
for (zf, kapi_bos_g, kapi_bos_k, kapi_bos_d) in ((BZ, [(2974, 3026)], [(2774, 2826)], [(2274, 2326)]),
                                                 (BZU, [], [], [])):
    hd = None if zf == BZ else saglam
    supurgelik('x', BY0 + K, +1, BX0 + K, IX - 6, zf, kapi_bos_g, hd)
    supurgelik('x', BY0 + K, +1, IX + 6, BX1 - K, zf, [], hd)
    supurgelik('x', BY1 - K, -1, BX0 + K, IX - 6, zf, kapi_bos_k, hd)
    supurgelik('x', BY1 - K, -1, IX + 6, BX1 - K, zf, [], hd)
    supurgelik('y', BX0 + K, +1, BY0 + K, BY1 - K, zf, [], hd)
    supurgelik('y', BX1 - K, -1, BY0 + K, BY1 - K, zf, kapi_bos_d, hd)
for xx in range(BX0 + 140, BX1 - 60, 180):
    kutu6(xx, BY0 + K, BZU - 26, xx + 12, BY1 - K, BZU - 16, {'*': KIRIS}, detay=True, hedef=saglam)
    kutu6(xx, BY0 + K, BZT - 10, xx + 12, BY1 - K, BZT, {'*': KIRIS}, detay=True, hedef=saglam)
# Olculdu: brushmodel bina ustundeyken (2B sinir kutusu) disaridan iceri bag
# kurulmuyordu -> derlemede +2000 yukarida, GSC oyunun basinda indirir.
import re as _re
def _yukari(b, dz):
    return _re.sub(r'\( (\S+) (\S+) (\S+) \)', lambda m: '( %s %s %s )' % (m.group(1), m.group(2), _s2(float(m.group(3)) + dz)), b)
def _s2(v):
    return ('%.3f' % v).rstrip('0').rstrip('.') if v != int(v) else str(int(v))
def _kaydir(b, dx, dz):
    return _re.sub(r'\( (\S+) (\S+) (\S+) \)', lambda m: '( %s %s %s )' % (_s2(float(m.group(1)) + dx), m.group(2), _s2(float(m.group(3)) + dz)), b)
# Olculdu: bina ustundeki brushmodel (+2000'de bile) iceri bagi kesiyordu ->
# derlemede yatayda BINA_KAYMA kadar uzakta (dis halka altinda, dugum yok).
BINA_KAYMA = -9000
saglam = [_kaydir(b, BINA_KAYMA, ENGEL_KAYDIR) for b in saglam]
H.ent('script_brushmodel', brushlar=saglam, targetname='bina_saglam')
YAPILAR['merkez_bina'] = (BX0, BY0, BX1, BY1, True)

# YIKIK HAL (+2000): alcak kirik duvarlar, yanik kirisler, moloz yiginlari
rnd = random.Random(77)
def yk_duvar(eksen, a, b, c0, c1):
    p = a
    while p < b - 1:
        q = min(b, p + rnd.randint(70, 160))
        hh = rnd.choice((0, 10, 24, 40, 60, 0, 16))
        if hh:
            if eksen == 'x':
                kutu6(p, c0, BZU + ENGEL_KAYDIR, q, c1, BZU + hh + ENGEL_KAYDIR, {'*': TUGLA, '+z': MOLOZ}, hedef=yikik)
            else:
                kutu6(c0, p, BZU + ENGEL_KAYDIR, c1, q, BZU + hh + ENGEL_KAYDIR, {'*': TUGLA, '+z': MOLOZ}, hedef=yikik)
        p = q
yk_duvar('x', BX0, BX1, BY0, BY0 + K)
yk_duvar('x', BX0, BX1, BY1 - K, BY1)
yk_duvar('y', BY0 + K, BY1 - K, BX0, BX0 + K)
yk_duvar('y', BY0 + K, BY1 - K, BX1 - K, BX1)
for i in range(9):                              # moloz yiginlari (konveks tumsek)
    cx_ = rnd.uniform(BX0 + 140, BX1 - 140); cy_ = rnd.uniform(BY0 + 120, BY1 - 120)
    r_ = rnd.uniform(90, 160); h_ = rnd.uniform(30, 70)
    alt, ust = [], []
    for k in range(9):
        a_ = math.radians(k * 40 + rnd.uniform(-10, 10))
        alt.append((cx_ + math.cos(a_) * r_, cy_ + math.sin(a_) * r_, BZ - 2 + ENGEL_KAYDIR))
        ust.append((cx_ + math.cos(a_) * r_ * .45, cy_ + math.sin(a_) * r_ * .45, BZ + h_ + ENGEL_KAYDIR))
    yuz = [((cx_, cy_, BZ - 2 + ENGEL_KAYDIR), (cx_ + 10, cy_, BZ - 2 + ENGEL_KAYDIR), (cx_, cy_ + 10, BZ - 2 + ENGEL_KAYDIR)),
           ((cx_, cy_, BZ + h_ + ENGEL_KAYDIR), (cx_ + 10, cy_, BZ + h_ + ENGEL_KAYDIR), (cx_, cy_ + 10, BZ + h_ + ENGEL_KAYDIR))]
    mats = [CAULK, MOLOZ]
    for k in range(9):
        yuz.append((alt[k], alt[(k + 1) % 9], ust[k])); mats.append(MOLOZ)
    H.konveks(yuz, mats, olcek=(256, 256), hedef=yikik)
for i in range(6):                              # yanik kirisler (egik)
    x_ = rnd.uniform(BX0 + 100, BX1 - 200); y_ = rnd.uniform(BY0 + 100, BY1 - 100)
    kutu6(x_, y_, BZ + ENGEL_KAYDIR, x_ + rnd.randint(160, 260), y_ + 14, BZ + 14 + ENGEL_KAYDIR, {'*': YANIK}, hedef=yikik)
yikik = [_kaydir(b, BINA_KAYMA, 0) for b in yikik]          # z zaten +2000
H.ent('script_brushmodel', brushlar=yikik, targetname='bina_yikik')

# merkez bina esyalari (patlamada silinir -> script_model 'bina_esya')
B_ESYA = [('furniture_duhoc_bunker_table', 3000, 2380, BZ, 0), ('military_german_radio1_grey', 2960, 2400, BZ + 34, 180),
          ('furniture_duhoc_chair', 3000, 2450, BZ, 270), ('furniture_duhoc_chair', 2920, 2380, BZ, 0),
          ('furniture_file_cabinet_long_a', 2700, 2590, BZ, 270), ('furniture_bookshelveswide', 3120, 2590, BZ, 270),
          ('crate01_snow', 2680, 2030, BZ, 0), ('crate02_snow', 2740, 2030, BZ, 20), ('prop_crate_wehrmacht3', 3300, 2560, BZ, 0),
          ('furniture_bed_bunker1', 3400, 2120, BZ, 90), ('furniture_bed_bunker1', 3400, 2480, BZ, 90),
          ('prop_potbelly_stove', 3250, 2560, BZ, 0),
          ('furniture_rolltopdesk', 3440, 2400, BZU, 180), ('furniture_duhoc_chair', 3380, 2400, BZU, 0),
          ('furniture_bed_bunker2', 2800, 2560, BZU, 0), ('furniture_bed_bunker2', 2980, 2560, BZU, 0),
          ('crate01_snow', 3300, 2050, BZU, 0), ('prop_crate_wehrmacht1', 2750, 2050, BZU, 0),
          ('furniture_armoire', 3460, 2560, BZU, 180)]
for (m, x, y, z, yaw) in B_ESYA:
    model(m, x, y, z, yaw, sinif='script_model', targetname='bina_esya')
for (x, y) in ((2700, 2200), (2700, 2480), (3000, 2200), (3330, 2300)):
    isik(x, y, BZU - 40, 360, 1.1)
    isik(x, y, BZT - 40, 360, 1.1)
# PATLAYICILAR (uc): duvara dayali (stok demolition: TNT duvara/destege kurulur)
BOMBALAR = []
def bomba(no, x, y, z, yaw):
    H.ent('script_model', model='xmodel/military_tntbomb_obj', origin=(x, y, z), angles=(0, yaw, 0),
          targetname='bomba', script_noteworthy=str(no), target='bomba_tetik%d' % no)
    bl_ = []
    H.kutu(x - 56, y - 56, z - 40, x + 56, y + 56, z + 50, 'trigger', 'trigger', alt='trigger', hedef=bl_)
    H.ent('trigger_use', brushlar=bl_, targetname='bomba_tetik%d' % no)
    BOMBALAR.append((x, y, z))
bomba(1, IX - 6 - 3, 2160, BZ + 36, 180)          # merkez bina: ic duvarin bati yuzu

# =========================================================================
# BARAKALAR VE DEPOLAR (tek kat, ahsap)
# =========================================================================
EV_H = 128
# girilebilir baraka A (bati-guney): kapilar dogu ve kuzey
ev('baraka_a', 1820, 2070, 2380, 2350, ZK + 16, EV_H,
   {'d': [('kapi', 2210)], 'k': [('kapi', 2100)], 'g': [('pen', 1950), ('pen', 2150), ('pen', 2280)],
    'b': [('pen', 2210)]}, GRI, SIVA, SAC)
ev('baraka_b', 1820, 2540, 2240, 2790, ZK + 16, EV_H,
   {'g': [('kapali', 2030), ('pen', 1920), ('pen', 2150)], 'd': [('pen', 2660)]}, GRI, SIVA, SAC, girilir=False)
ev('baraka_c', 3780, 1700, 4080, 2200, ZK + 16, EV_H,
   {'b': [('kapali', 1950), ('pen', 1800), ('pen', 2100)]}, GRI, SIVA, SAC, girilir=False, cati_yon='x')
ev('baraka_d', 3780, 2350, 4080, 2800, ZK + 16, EV_H,
   {'b': [('kapali', 2575), ('pen', 2450), ('pen', 2700)]}, GRI, SIVA, SAC, girilir=False, cati_yon='x')
# depolar: girilebilir depo (kuzey-orta), kapali depo (kuzeybati)
ev('depo_a', 3150, 2770, 3600, 2950, ZK + 16, EV_H + 16,
   {'g': [('kapi', 3375), ('pen', 3220), ('pen', 3530)]}, GRI, GRI, SAC)
ev('depo_b', 2420, 2760, 2870, 2900, ZK + 16, EV_H + 16,
   {'g': [('kapali', 2645)], 'd': [('pen', 2830)]}, GRI, GRI, SAC, girilir=False)
for (x, y) in ((2100, 2210), (3375, 2860)):
    isik(x, y, ZK + 16 + EV_H - 30, 300, .9)
bomba(2, 3300, 2950 - 16 - 3, ZK + 16 + 36, 270)     # depo A: kuzey duvar ici
bomba(3, 1820 + 16 + 3, 2150, ZK + 16 + 36, 0)       # baraka A: bati duvar ici
EV_ESYA = [('furniture_bed_bunker1', 1900, 2250, 90), ('furniture_bed_bunker1', 2000, 2250, 90),
           ('furniture_bed_bunker1', 2300, 2290, 90), ('prop_potbelly_stove', 2200, 2310, 0),
           ('furniture_smallfoldingtable', 2150, 2150, 0), ('furniture_utilitychair1', 2210, 2150, 180),
           ('crate01_snow', 3200, 2910, 0), ('crate02_snow', 3260, 2910, 30), ('prop_crate_wehrmacht2', 3500, 2910, 0),
           ('prop_barrel_benzin_snow', 3560, 2830, 0), ('prop_barrel_benzin_snow', 3540, 2880, 0)]
for (m, x, y, yaw) in EV_ESYA:
    model(m, x, y, ZK + 16, yaw)

# kamp ici dekor ve siperler
KAMP_DEKOR = [('vehicle_opel_blitz_snow_static', 3700, 1640, 0),
              ('crate01_snow', 2560, 1760, 0), ('crate02_snow', 2610, 1760, 20),
              ('prop_barrel_green_snowside', 1900, 2380, 0),
              ('military_sandbag_snow_longsection', 2900, 1880, 0), ('military_sandbag_snow_longsection', 3100, 1880, 0)]
for (m, x, y, yaw) in KAMP_DEKOR:
    model(m, x, y, ZK, yaw)
# kamp disi engeller: dikenli tel (cit onu), kirpi, ejder disi; kapi onu kum torbalari
for x in range(kx0 + 80, kx1 - 60, 230):
    if abs(x - KAPI_X) > 300:
        model('caen_barbedwire_3', x, ky0 - 110, None, random.Random(x).randint(0, 30))
for y in range(ky0 + 120, ky1 - 60, 260):
    model('caen_barbedwire_3', kx0 - 110, y, None, 90 + random.Random(y).randint(0, 30))
for (x, y, m) in ((KAPI_X - 420, ky0 - 260, 'military_hedgehog'), (KAPI_X + 420, ky0 - 260, 'military_hedgehog'),
                  (KAPI_X - 560, ky0 - 380, 'military_dragonstooth_snow'), (KAPI_X + 560, ky0 - 360, 'military_dragonstooth_snow'),
                  (KAPI_X - 300, ky0 - 520, 'military_hedgehog'), (KAPI_X + 330, ky0 - 520, 'military_hedgehog')):
    model(m, x, y, None, random.Random(int(x)).randint(0, 90))
for (x, y, yaw) in ((KAPI_X - 200, ky0 - 200, 0), (KAPI_X + 200, ky0 - 200, 0), (KAPI_X - 340, ky0 - 140, 30),
                    (KAPI_X + 340, ky0 - 140, 330)):
    model('military_sandbag_snow_longsection', x, y, None, yaw)

# =========================================================================
# DEKOR: gozetleme kulesi (yol kenari), kucuk karakol (dogu), patlama noktasi
# =========================================================================
def kulube(cx, cy, w, d, h):
    x0, y0 = cx - w // 2, cy - d // 2
    z = min(yukseklik(x0 + a, y0 + b) for a in (0, w) for b in (0, d)) - 24
    zt = max(yukseklik(x0 + a, y0 + b) for a in (0, w) for b in (0, d))
    kutu6(x0, y0, z, x0 + w, y0 + d, zt + 8, {'*': TEMEL, '+z': TABAN})
    ev('kulube_%d_%d' % (cx, cy), x0, y0, x0 + w, y0 + d, zt + 8, h,
       {'g': [('kapali', cx), ('pen', x0 + 50)], 'd': [('pen', cy)]}, GRI, SIVA, SAC, girilir=False, taban=False)
for (px, py, w, d) in ((1010, 495, 240, 180), (1045, 560, 200, 160), (985, 560, 180, 150)):
    kulube(*[int(v) for v in W(px, py)], w, d, 128)
# yol kenari gozetleme kulesi (kroki 'Gozetleme Noktasi') -- dekor
def dekor_kule(cx, cy):
    z = yukseklik(cx, cy)
    for (dx, dy) in ((-60, -60), (46, -60), (-60, 46), (46, 46)):
        kutu6(cx + dx, cy + dy, z - 30, cx + dx + 14, cy + dy + 14, z + 330, {'*': KIRIS})
    kutu6(cx - 60, cy - 60, z + 230, cx + 60, cy + 60, z + 242, {'*': TRIM, '+z': TAHTA2})
    H.kama(cx - 74, cy - 74, cx + 74, cy + 74, z + 330, z + 336, z + 370, '+y', SAC, TRIM, alt=TRIM)
    YAPILAR['dkule'] = (cx - 64, cy - 64, cx + 64, cy + 64, False)
dekor_kule(*W(352, 600))

# =========================================================================
# KAYALAR, ORMAN
# =========================================================================
_kh = YOL_HAT['konvoy'][0]
_kx, _ky = dere_x(KOPRU_Y[0]), KOPRU_Y[0]
_en, KOPRU_M = 1e9, 0
for _m in range(0, int(hat_uzunluk(_kh)), 5):
    _p = hat_nokta(_kh, _m)
    _d = math.hypot(_p[0] - _kx, _p[1] - _ky)
    if _d < _en:
        _en, KOPRU_M = _d, _m
KONVOY_ARA = 340
PATLAMA = hat_nokta(_kh, KOPRU_M + KONVOY_ARA)     # pusu merkezi: oyuncunun kamyonu
# kopru engeli: arkadaki kamyon kopru ustunde patlayinca geri donus kapanir
_bl = []
H.kutu(_kx - 130, _ky - 132, KOPRU_Z[0] + ENGEL_KAYDIR, _kx - 114, _ky + 132, KOPRU_Z[0] + 220 + ENGEL_KAYDIR, SINIR, SINIR, alt=SINIR, hedef=_bl)
H.ent('script_brushmodel', brushlar=_bl, targetname='kopru_engel')
# pusu alani: yol iki yaninda kaya siperleri (oyuncu/AI)
for i, (dx, dy, r, h) in enumerate([(-420, 260, 80, 90), (380, -260, 70, 80), (-260, -420, 90, 70),
                                    (460, 300, 80, 100), (-600, -100, 70, 60), (650, -40, 90, 90),
                                    (-150, 700, 110, 140), (300, 760, 120, 150), (800, 520, 100, 130),
                                    (-700, 450, 90, 110)]):
    x, y = PATLAMA[0] + dx, PATLAMA[1] + dy
    if yol_mesafe(x, y) > 190 and dere_mes(x, y) > DERE_DIS + 160 and icinde(x, y):
        kaya(x, y, r, h, 500 + i)
# yol boyu kayalik yamaclar
konvoy_hat = YOL_HAT['konvoy'][0]
rr = random.Random(9)
for m in range(600, int(hat_uzunluk(konvoy_hat)) - 1200, 520):
    x, y = hat_nokta(konvoy_hat, m)
    s = rr.choice((-1, 1))
    (ax, ay) = hat_nokta(konvoy_hat, m - 50); (bx, by) = hat_nokta(konvoy_hat, m + 50)
    L = math.hypot(bx - ax, by - ay) or 1
    qx, qy = -(by - ay) / L, (bx - ax) / L
    d = rr.randint(330, 520)
    px_, py_ = x + qx * s * d, y + qy * s * d
    if icinde(px_, py_) and dere_mes(px_, py_) > DERE_DIS + 120:
        kaya(px_, py_, rr.randint(70, 120), rr.randint(60, 150), 600 + m)

random.seed(51)
CAM = ['tree_snow_pine_xl_c', 'tree_snow_pine_lg_c', 'tree_snow_pine_lg_c', 'tree_snow_pine_sm_c']
def agac_uygun(x, y, ic):
    if yol_mesafe(x, y) < 250:
        return False
    if dere_mes(x, y) < DERE_DIS + 110:
        return False
    if kamp_mes(x, y) < 380:
        return False
    if math.hypot(x - PATLAMA[0], y - PATLAMA[1]) < 300:
        return False
    if any(abs(x - a) < 140 and abs(y - b) < 140 for (a, b) in AGAC):
        return False
    for ad, v in YAPILAR.items():
        if v and v[0] - 160 < x < v[2] + 160 and v[1] - 160 < y < v[3] + 160:
            return False
    for (kx, ky, kr) in KAYALAR:
        if math.hypot(x - kx, y - ky) < kr + 60:
            return False
    if not (SX0 + 96 < x < SX1 - 96 and SY0 + 96 < y < SY1 - 96):
        return False
    return icinde(x, y) == ic
# icerde: yogun orman (yol iki yani, kroki), kenar bandi
for x in range(SX0 + 160, SX1 - 159, 210):
    for y in range(SY0 + 160, SY1 - 159, 210):
        x2, y2 = x + random.randint(-80, 80), y + random.randint(-80, 80)
        if icinde(x2, y2):
            yd = yol_mesafe(x2, y2)
            olas = 0.85 if kenar_mes(x2, y2) < 600 else (0.55 if yd < 900 else 0.75)
            if random.random() < olas and agac_uygun(x2, y2, True):
                model(random.choice(CAM), x2, y2, None, random.randint(0, 359))
for x in range(SX0 + 160, SX1 - 159, 260):                      # disarida sik bant
    for y in range(SY0 + 160, SY1 - 159, 260):
        x2, y2 = x + random.randint(-100, 100), y + random.randint(-100, 100)
        o = disari(x2, y2)
        if 60 < o < 1600 and agac_uygun(x2, y2, False):
            model(random.choice(CAM[:3]), x2, y2, None, random.randint(0, 359), kayit=False)
for (px, py, m) in [(260, 700, 'tree_destroyed_snow_stump_a'), (450, 610, 'tree_destoyed_snow_trunk_a'),
                    (700, 470, 'tree_destroyed_snow_fallen_log_a'), (520, 520, 'tree_destroyed_snow_stump_b'),
                    (850, 380, 'tree_destoyed_snow_trunk_b'), (150, 770, 'tree_destroyed_snow_fallen_log_a')]:
    x, y = W(px, py)
    if agac_uygun(x, y, True):
        model(m, x, y, None, random.randint(0, 359))

# ---------------------------------------------------------------- baslangic
# Oyuncu kamyon kasasinda baslar (GSC baglar); baslangic noktasi konvoy yolunun
# harita icindeki ilk kismi (yukleme ani icin; GSC hemen kamyona tasir).
BASLANGIC = W(100, 790)
H.ent('info_player_start', origin=(BASLANGIC[0], BASLANGIC[1], round(yukseklik(*BASLANGIC) + 8, 1)),
      angles=(0, 30, 0))
# guvenli alan (kacis): kamp girisinin disi, yol uzerinde
GUVENLI = (1850, 900)

# ---------------------------------------------------------------- dogrulama
def dogrula():
    var = set()
    for p in glob.glob(os.path.join(KOK, 'main', '*.iwd')):
        for n_ in zipfile.ZipFile(p).namelist():
            var.add(n_.lower())
    eksik = [m for m in sorted(H.malzemeler) if m not in ('caulk', 'clip_player', 'trigger', 'origin')
             and 'materials/' + m.lower() not in var]
    modeller = sorted({d['model'] for d, _ in H.ents if 'model' in d and d['classname'] in ('misc_model', 'script_model')})
    eksik_m = [m for m in modeller if m.lower() not in var]
    return eksik, eksik_m

H.ent('misc_turret', model='xmodel/weapon_mg42', weaponinfo='mg42_bipod_stand',
      origin=(SX0 + 400, SY0 + 400, round(yukseklik(SX0 + 400, SY0 + 400), 1)), angles=(0, 0, 0))

def sinir_gsc():
    o = ['// burya_sinir.gsc -- gen_burya.py URETIR, elle duzenlemeyin.',
         'cokgen()', '{', '\tp = [];']
    for (x, y) in POLI:
        o.append('\tp[p.size] = (%d, %d, 0);' % (round(x), round(y)))
    o += ['\treturn p;', '}', '']
    open(os.path.join(KOK, 'main', 'maps', HARITA + '_sinir.gsc'), 'w', newline='\r\n').write('\n'.join(o) + '\n')
sinir_gsc()

import ent_burya
ent_burya.yerlestir(sys.modules[__name__])

if __name__ == '__main__':
    eksik, eksik_m = dogrula()
    if eksik or eksik_m:
        raise SystemExit('EKSIK VARLIK! malzeme: %s model: %s' % (eksik, eksik_m))
    r = H.yaz(os.path.join(KOK, 'map_source', HARITA + '.map'))
    print('dunya brush/mesh: %(dunya_brush)d  entity: %(entity)d  bayt: %(bayt)d' % r)
    print('malzemeler:', r['malzeme'])
    print('misc_model: %d  kaya: %d  agac: %d  isik: %d' % (
        sum(1 for d, _ in H.ents if d['classname'] == 'misc_model'), len(KAYALAR), len(AGAC),
        sum(1 for d, _ in H.ents if d['classname'] == 'light')))
    kh = YOL_HAT['konvoy'][0]
    print('konvoy yolu: %d birim, kopru z=%s, kamp z=%.0f' % (hat_uzunluk(kh), [round(z) for z in KOPRU_Z], ZK))
