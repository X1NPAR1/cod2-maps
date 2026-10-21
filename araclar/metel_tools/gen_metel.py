# -*- coding: utf-8 -*-
"""
gen_metel.py -- CoD2 SP 'metel' (Operatsiya Metel, 8 Ocak 1943).

Kroki (Desktop/YeniMap/Kroki.png) BIREBIR: butun yerlesim kroki pikseliyle
yazilir, W(px, py) dunya birimine cevirir (1 px = 6 birim, kuzey = +Y).

  Guney   : baslangic, orman patikasi, kucuk kulube
  Bati    : B -- yuksek kar platosu, tek kivrimli rampa yolu, havan cukuru
  Merkez  : A -- avlulu iki katli Alman karakolu
  Dogu    : donmus dere yatagi + iki tahta kopru, C -- kayalik sirt, dar patika
  Cevre   : yukselen kar tepeleri + sik cam ormani; gorunmez sinir (clip_player)
            krokideki beyaz cizginin TAM uzerinde.

Krasnoye'den olculen kurallar: SP'de vis yok; tavanin alt yuzu de gokyuzu;
placeholder ('case*') dokular yok; KULLANILAN HER MALZEME/MODEL iwd'de
dogrulanir (asagida dogrula()).
"""
import os, sys, math, random, zipfile, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kmap import Harita

KOK = r'F:\Activision\Call of Duty 2'
S = 6.0

def W(px, py):
    return ((px - 640) * S, (520 - py) * S)

# ---------------------------------------------------------------- malzemeler
KAR = 'stalingradwinter_snow01'
KAR2 = 'stalingradwinter_snow02'
YOL = 'stalingradwinter_slush1'
KAYA = 'd_cliff04'
TUGLA = 'stalingradwinter_brick03'
TEMEL = 'stalingradwinter_brick02'
SIVA = 'stalingradwinter_plaster01'
KORNIS = 'stalingradwinter_concretetrim01'
TABAN = 'stalingradwinter_wood_floor'
CATI = 'stalingradwinter_roof_slate01'
TAHTA = 'stalingradwinter_woodplank01'
TAHTA2 = 'stalingradwinter_woodplank02'
TAHTA3 = 'stalingradwinter_woodplank03'
TRIM = 'stalingradwinter_wood_trim'
BASAMAK = 'stalingradwinter_stairs_concrete01'
PERVAZ = 'dawnville2_windowframe01'
KASA = 'dawnville2_doorframe01'
KIRIS = 'stalingrad_beam_side'
GOK = 'sky_tankhunt'
CAULK = 'caulk'
SINIR = 'clip_player'

H = Harita()
H.ws.update({'_color': '.92 .95 1', 'ambient': '.17', 'sunlight': '1.15',
             'sundirection': '-34 -60 0', 'sundiffusecolor': '.80 .86 .98',
             'suncolor': '.93 .96 1', 'diffusefraction': '.60',
             '-contrastgain': '.4', 'northyaw': '90'})

# ---------------------------------------------------------------- sinir
SINIR_PX = [(40, 395), (200, 205), (330, 235), (420, 105), (520, 40), (830, 28),
            (1000, 45), (1180, 95), (1240, 300), (1195, 505), (1175, 610), (1030, 815),
            (980, 825), (860, 975), (560, 970), (430, 850), (330, 700), (130, 640), (40, 560)]
POLI = [W(*p) for p in SINIR_PX]
SX0, SX1, SY0, SY1 = -4864, 4864, -4096, 4352            # gokyuzu kutusu (128 kati)
ZTAVAN = 2816

def _seg(px, py, a, b):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    L = float(dx * dx + dy * dy) or 1.0
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - (ax + dx * t), py - (ay + dy * t))

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

def ss(e0, e1, x):
    if e0 == e1:
        return 1.0 if x >= e1 else 0.0
    t = max(0.0, min(1.0, (x - e0) / float(e1 - e0)))
    return t * t * (3 - 2 * t)

def lerp(a, b, t):
    return a + (b - a) * t

# ---------------------------------------------------------------- dere
DERE_PX = [(845, 30), (858, 200), (870, 385), (862, 520), (868, 620),
           (885, 800), (905, 975)]
DERE = [W(*p) for p in DERE_PX]          # oynanabilir kisim (K-G), dere_x(y) bunu kullanir
# Uclar (kullanici: "derenin sonunda skybox gozukuyor; sola dogru gitsin, tepenin
# arkasindan geliyormus gibi gozuksun"): kuzey uc bakana gore SOLA (batiya),
# guney uc SOLA (doguya) kivrilir ve dis tepelerin icinde kapali kanyon basiyla
# biter -> dere boyunca bakinca gokyuzu kutusu degil kaya duvari gorunur.
DERE_TAM = [W(*p) for p in [(735, -110), (785, -85), (828, -35)]] + DERE +            [W(*p) for p in [(925, 1020), (975, 1050), (1030, 1060)]]

def dere_mes(x, y):
    return min(_seg(x, y, DERE_TAM[i], DERE_TAM[i + 1]) for i in range(len(DERE_TAM) - 1))

def dere_x(y):
    for i in range(len(DERE) - 1):
        (xa, ya), (xb, yb) = DERE[i], DERE[i + 1]
        if yb <= y <= ya:
            return lerp(xa, xb, (ya - y) / float(ya - yb))
    return DERE[0][0] if y > DERE[0][1] else DERE[-1][0]

DERE_TABAN = -360
DERE_IC, DERE_DIS = 90, 210            # taban yari genisligi, kenar yari genisligi
KOPRU_Y = [W(0, 385)[1], W(0, 620)[1]]  # kuzey ve guney kopru

# ---------------------------------------------------------------- bolgeler
B_MERKEZ = W(255, 295)
C_MERKEZ = W(1095, 340)
B_UST, C_UST = 210, 240
AVLU = (-1020, -320, 720, 1000)        # x0, y0, x1, y1 (alcak tugla duvar)
BINA = (-726, 118, 426, 822)           # karakol

def b_plato(x, y):
    r = math.hypot(x - B_MERKEZ[0], y - B_MERKEZ[1])
    return B_UST * ss(500, 340, r)

def c_sirt(x, y):
    e = math.hypot((x - C_MERKEZ[0]) / 1.0, (y - C_MERKEZ[1]) / 1.55)
    # tepe (e<150) DUZ: havan/kum torbasi/patika ucu oraya oturur; kenar kayalik puruzlu
    return C_UST * ss(470, 320, e) + 40 * ss(150, 240, e) * ss(330, 260, e) * math.sin(x / 90.0) * math.cos(y / 110.0)

TEPE = [(W(560, 175), 520, 190), (W(720, 140), 470, 220), (W(990, 150), 430, 200),
        (W(430, 640), 420, 110), (W(820, 820), 460, 130), (W(1020, 700), 380, 150),
        (W(170, 520), 420, 120), (W(300, 140), 380, 170), (W(1150, 200), 360, 160)]

# Kullanici (ekran goruntusu): yol tepeyi zikzakli bir yarikla asiyordu.
# Simdi yol daha uzun ve harita disinda tepeler arasinda GENIS, yumusak bir
# VADIDEN kivrilarak uzaklasir; dis tepe yuksekligi yol cevresinde vadiye iner.
# Kullanici (ikinci tur): vadinin sonu gokyuzune aciliyordu. Yollar harita
# sinirindan cikinca KESKIN donup bir tepenin arkasinda biter; vadi orada
# yamacla kapanir (bakinca gokyuzu degil tepe gorunur).
GUNEY_PX = [(350, 1160), (405, 1140), (440, 1108), (452, 1072), (458, 1035), (495, 1000), (555, 975), (610, 922),
            (650, 850), (642, 760), (645, 690), (640, 655)]
# Kullanici: "Almanlarin gelis yollari harita disina uzanan, arkasi gorunmeyen,
# cevresi tepelerle cevrili bir yol olsun" -> bati ve dogu giris yollari da
# uzun ve KIVRIMLI; harita disinda tepeler arasinda vadiden donup kaybolur.
GIRIS_PX = {
    'guney': GUNEY_PX,
    'bati_giris': [(-100, 830), (-60, 800), (-30, 765), (-18, 728), (-8, 672), (25, 628), (90, 605), (150, 598), (230, 612),
                   (350, 620), (470, 618)],
    'dogu_giris': [(1360, 735), (1320, 712), (1288, 680), (1272, 640), (1266, 585), (1240, 535), (1200, 505), (1150, 495), (1080, 505),
                   (1005, 520)],
}
GIRIS_W = {k: [W(*p) for p in v] for k, v in GIRIS_PX.items()}
def guney_mes(x, y):
    # en yakin giris yolu (vadi oyma icin)
    return min(_seg(x, y, L[i], L[i + 1]) for L in GIRIS_W.values() for i in range(len(L) - 1))

def zemin_ham(x, y):
    """yollar uygulanmadan once arazi."""
    z = 0.0
    for ((cx, cy), r, hh) in TEPE:
        z += hh * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / float(r * r))
    z += 14 * math.sin(x / 390.0) * math.cos(y / 470.0)
    # sinira yaklastikca yukselen kar tepeleri (icerden 650 birimlik bant)
    if icinde(x, y):
        z += 150 * ss(650, 0, kenar_mes(x, y))
    else:
        o = kenar_mes(x, y)
        dis_z = 150 + 520 * ss(0, 1100, o) + 70 * math.sin(x / 520.0) * math.cos(y / 610.0) * ss(0, 600, o)
        z += dis_z * (0.12 + 0.88 * ss(160, 520, guney_mes(x, y)))     # dar, kivrimli vadi
    # avlu ve karakol duz
    x0, y0, x1, y1 = AVLU
    d = math.hypot(max(x0 - 260 - x, x - x1 - 260, 0), max(y0 - 260 - y, y - y1 - 260, 0))
    z *= ss(0, 420, d)
    z = max(z, b_plato(x, y), c_sirt(x, y))
    # dere yatagi
    dx = dere_mes(x, y)
    if dx < DERE_DIS + 140:
        z = z * ss(DERE_DIS, DERE_DIS + 140, dx) + DERE_TABAN * ss(DERE_DIS, DERE_IC, dx)
    return z

# ---------------------------------------------------------------- yollar
# (px, py, z) ; z None -> ham arazi. Rampa yollar acik z verir.
YOLLAR = {
    # kullanici: "arkamizdaki yol tepeye tirmaniyor; oval olsun, gelisi gorunmesin"
    # -> yol baslangicin batisindan yay cizerek tepelerin ARKASINA kivrilir, sabit
    # alcak z ile tepeyi yarar (yarma duvarlari gorusu kapatir).
    'guney': ([(px, py, None) for (px, py) in GUNEY_PX[:-1]] + [(640, 655, 0)], 150),
    # karsi saldiri araclari: bati ve dogudan harita disindan gelen giris yollari
    'bati_giris': ([(px, py, None) for (px, py) in GIRIS_PX['bati_giris']], 140),
    'dogu_giris': ([(px, py, None) for (px, py) in GIRIS_PX['dogu_giris']], 140),
    'bati': ([(640, 655, 0), (560, 640, None), (470, 618, None), (395, 565, None),
              (350, 495, None), (335, 425, None), (352, 372, None), (405, 348, None)], 150),
    'kuzey': ([(405, 348, None), (480, 343, None), (560, 342, None), (650, 340, None),
               (740, 344, None), (800, 362, None), (826, 385, 'K'), (914, 385, 'K'),
               (960, 368, None), (1000, 345, None)], 140),
    'gdogu': ([(640, 655, 0), (720, 642, None), (790, 628, None), (830, 622, 'G'),
               (906, 620, 'G'), (955, 612, None), (995, 585, None), (1005, 520, None),
               (1003, 430, None), (1000, 345, None)], 140),
    'avlu': ([(640, 655, 0), (628, 610, 0), (615, 575, 0)], 130),
    'b_rampa': ([(345, 430, None), (305, 418, 30), (262, 402, 85), (228, 372, 150),
                 (214, 335, 200), (228, 305, B_UST), (252, 296, B_UST)], 110),
    'c_patika': ([(1005, 520, None), (1035, 497, 60), (1060, 470, 125), (1078, 438, 185),
                  (1090, 400, C_UST), (1095, 368, C_UST)], 70),
}

def _kopru_z(k):
    y = KOPRU_Y[0] if k == 'K' else KOPRU_Y[1]
    xr = dere_x(y)
    return max(zemin_ham(xr - 330, y), zemin_ham(xr + 330, y), 0.0)

YOL_HAT = {}
for ad, (pts, gen) in YOLLAR.items():
    hat = []
    for (px, py, z) in pts:
        x, y = W(px, py)
        if z is None:
            z = zemin_ham(x, y)
        elif z in ('K', 'G'):
            z = _kopru_z(z)
        hat.append((x, y, float(z)))
    YOL_HAT[ad] = (hat, gen)

def yol_bilgi(x, y):
    """(mesafe, yol z'si, yari genislik) en yakin yol icin."""
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
    if d < yg + 160:
        # dere ustunde (kopru acikligi) yol araziyi DOLDURMAZ; kopru brush'tir
        if dere_mes(x, y) < DERE_DIS + 20 and z < yz - 40:
            return z
        z = lerp(z, yz, ss(yg + 160, yg + 20, d))
    return z

# ---------------------------------------------------------------- gokyuzu
H.oda_kabugu(SX0, SY0, -512, SX1, SY1, ZTAVAN, 16, CAULK, GOK, GOK)

# ---------------------------------------------------------------- arazi
A = 128
xs = list(range(SX0, SX1 + 1, A)); ys = list(range(SY0, SY1 + 1, A))
# Kaya dokusu YALNIZ dere duvarinda (ilk derleme: 512'lik parcalar kiyiyi da
# kayaya boyuyordu). Dere bandinda mesh 1 sutun (128) genisliginde parcalanir;
# parca, tum satirlarinda dere duvari icindeyse (|x - dere| <= DERE_DIS) kaya.
def dere_bandi(x0, x1, y0, y1):
    # sutun (x0..x1) dere hattinin herhangi bir noktasina 'DERE_DIS+200' yakin mi
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
    if dere_bandi(xs[i0], xs[i1], ys[0], ys[-1]):
        i1 = i0 + 1
    for j0 in range(0, len(ys) - 1, PAR):
        j1 = min(j0 + PAR, len(ys) - 1)
        mat = KAYA if duvar_mi(xs[i0], xs[i1], ys[j0], ys[j1]) else KAR
        H.mesh([[(xs[i], ys[j], zh(xs[i], ys[j])) for j in range(j0, j1 + 1)]
                for i in range(i0, i1 + 1)], mat, doku=4.0 if mat == KAR else 2.0)
    i0 = i1
# DERE SUYU (kullanici: "derenin icine su ekle"). Kis haritalarinda su malzemesi
# yok; stok water_hill400_assault (iwd'de var). Oyuncu dereye inemez (kenar
# clip_player), su yalniz gorseldir: tabandaki buz seridinin 12 birim ustunde,
# kenarlari buz (slush) olarak kalir. Her dere parcasi icin konveks prizma.
SU = 'water_hill400_assault'
SU_Z = DERE_TABAN + 250
for i in range(len(DERE_TAM) - 1):
    (xa, ya), (xb, yb) = DERE_TAM[i], DERE_TAM[i + 1]
    L = math.hypot(xb - xa, yb - ya); ux, uy = (xb - xa) / L, (yb - ya) / L
    if i == 0:                               # uclarda su kanyon basinin altina uzar
        xa, ya = xa - ux * 260, ya - uy * 260
    if i == len(DERE_TAM) - 2:
        xb, yb = xb + ux * 260, yb + uy * 260
    n = max(1, int(math.hypot(xb - xa, yb - ya) // 256))
    for k in range(n):
        t0, t1 = k / float(n), (k + 1) / float(n) + 0.02
        p0 = (lerp(xa, xb, t0), lerp(ya, yb, t0)); p1 = (lerp(xa, xb, min(t1, 1)), lerp(ya, yb, min(t1, 1)))
        g = 205                 # yuksek seviyede dere duvarina kadar genisler (fazlasi arazi altinda)
        nx, ny = -uy * g, ux * g
        q = [(p0[0] - nx, p0[1] - ny), (p1[0] - nx, p1[1] - ny), (p1[0] + nx, p1[1] + ny), (p0[0] + nx, p0[1] + ny)]
        z0, z1 = DERE_TABAN - 8, SU_Z         # kullanici: "su seviyesi yuksek olsun"
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
    # dere uzerindeki kisim kopru brush'u ile kapanir: o satirlari atla
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
    yol_mesh(hat, gen)

# ---------------------------------------------------------------- engel kayitlari
MODELLER = []      # (model, x, y)
KAYALAR = []       # (x, y, r)
YAPILAR = {}       # ad -> (x0, y0, x1, y1, acik)
AGAC = []

def model(m, x, y, z=None, yaw=0, kayit=True):
    if m.startswith('tree_'):
        AGAC.append((x, y))
    if kayit:
        MODELLER.append((m, x, y))
    if z is None:
        z = yukseklik(x, y)
    H.ent('misc_model', model='xmodel/' + m, origin=(round(x, 1), round(y, 1), round(z, 1)),
          angles=(0, yaw, 0))

def isik(x, y, z, r=260, i=.6, renk='1 0.80 0.52'):
    H.ent('light', origin=(x, y, z), radius=r, intensity=i, _color=renk,
          **{'def': 'light_point_linear_nocenter'})

def kaya(x, y, r, h, tohum, gom=40):
    """Konveks kaya: 8 kenarli, ust yuzu egik, yanlari ice dogru. Yan d_cliff04,
    ust kar. Taban arazinin 'gom' kadar icinde (havada durmaz)."""
    rnd = random.Random(tohum)
    zt = min(yukseklik(x + dx, y + dy) for dx in (-r, 0, r) for dy in (-r, 0, r))
    zb = zt - gom
    # ilk tur goruntusu: 8 kenarli duz tepeli kayalar kutuk gibiydi -> 11 kenar,
    # tepe halkasi dar ve duzensiz, ust yuz belirgin egik
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
    KAYALAR.append((x, y, r * 1.15))         # en genis taban yaricapi

def dikey_levha(a, b, z0, z1, mat, kalin=16):
    """iki nokta arasinda dikey ince levha (egik sinir duvarlari icin)."""
    (ax, ay), (bx, by) = a, b
    L = math.hypot(bx - ax, by - ay)
    nx, ny = -(by - ay) / L * kalin / 2.0, (bx - ax) / L * kalin / 2.0
    p = [(ax - nx, ay - ny), (bx - nx, by - ny), (bx + nx, by + ny), (ax + nx, ay + ny)]
    yuz = [((ax, ay, z0), (bx, by, z0), (ax + nx, ay + ny, z0)),
           ((ax, ay, z1), (bx, by, z1), (ax + nx, ay + ny, z1))]
    for k in range(4):
        q0, q1 = p[k], p[(k + 1) % 4]
        yuz.append(((q0[0], q0[1], z0), (q1[0], q1[1], z0), (q0[0], q0[1], z1)))
    H.konveks(yuz, [mat] * 6)

# ---------------------------------------------------------------- gorunmez sinir
SINIR_KAPI = []
for i in range(len(POLI)):
    (ax, ay), (bx, by) = POLI[i], POLI[(i + 1) % len(POLI)]
    L = math.hypot(bx - ax, by - ay)
    n = max(1, int(L // 48))
    parca = []
    for k in range(n):
        t0, t1 = k / float(n), (k + 1) / float(n)
        p0 = (lerp(ax, bx, t0), lerp(ay, by, t0)); p1 = (lerp(ax, bx, t1), lerp(ay, by, t1))
        mx, my = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0
        parca.append((p0, p1, guney_mes(mx, my) < 230))
    j = 0
    while j < len(parca):
        k = j
        while k + 1 < len(parca) and parca[k + 1][2] == parca[j][2]:
            k += 1
        if parca[j][2]:
            SINIR_KAPI.append((parca[j][0], parca[k][1]))
        else:
            dikey_levha(parca[j][0], parca[k][1], -600, 2200, SINIR)
        j = k + 1
# dere kenarlari: oyuncu dereye inemez (kopru acikliklari haric)
# 32'lik parcalar, kopru korkulugunun (|y-yk|=112) hemen disinda biter: arada
# atlanacak bosluk kalmaz (kullanici: "derenin icine atlanamasin").
for kenar in (-1, 1):
    y = DERE[0][1]
    while y > DERE[-1][1]:
        y2 = y - 32
        if all(min(abs(y - yk), abs(y2 - yk)) >= 104 and not (y2 < yk < y) for yk in KOPRU_Y):
            a = (dere_x(y) + kenar * (DERE_DIS + 10), y)
            b = (dere_x(y2) + kenar * (DERE_DIS + 10), y2)
            dikey_levha(a, b, -600, 900, SINIR)
        y = y2

# ---------------------------------------------------------------- kopruler
def kopru(yk):
    xr = dere_x(yk)
    z = max(yol_bilgi(xr - DERE_DIS - 40, yk)[1], yol_bilgi(xr + DERE_DIS + 40, yk)[1])
    x0, x1 = xr - DERE_DIS - 70, xr + DERE_DIS + 70
    H.kutu(x0, yk - 104, z - 14, x1, yk + 104, z + 2, TAHTA, TAHTA3, alt=TAHTA3)   # guverte
    for xx in range(int(x0) + 24, int(x1) - 16, 64):                               # enine tahtalar
        H.kutu(xx, yk - 100, z + 2, xx + 40, yk + 100, z + 4, TAHTA2, TAHTA2, detay=True)
    for yy in (yk - 104, yk + 96):                                                  # korkuluk
        for xx in range(int(x0), int(x1) + 1, 128):
            H.kutu(xx, yy, z + 2, xx + 8, yy + 8, z + 50, TAHTA3, detay=True)
        H.kutu(x0, yy, z + 42, x1, yy + 8, z + 50, TRIM, detay=True)
        H.kutu(x0, yy, z + 22, x1, yy + 8, z + 28, TRIM, detay=True)
    for xx in (xr - 120, xr + 112):                                                 # ayaklar
        for yy in (yk - 96, yk + 80):
            H.kutu(xx, yy, DERE_TABAN - 10, xx + 16, yy + 16, z - 14, TAHTA3, detay=True)
    H.kutu(xr - 120, yk - 96, z - 60, xr + 128, yk - 88, z - 14, TAHTA3, detay=True)
    H.kutu(xr - 120, yk + 88, z - 60, xr + 128, yk + 96, z - 14, TAHTA3, detay=True)
    # korkuluk oyuncuyu da tutar (atlayip dereye dusmesin)
    H.kutu(x0, yk - 112, z + 2, x1, yk - 104, z + 120, SINIR, SINIR, alt=SINIR)
    H.kutu(x0, yk + 104, z + 2, x1, yk + 112, z + 120, SINIR, SINIR, alt=SINIR)
    YAPILAR['kopru_%d' % int(yk)] = (x0, yk - 112, x1, yk + 112, True)
    return z
KOPRU_Z = [kopru(yk) for yk in KOPRU_Y]

# =========================================================================
# A -- IKI KATLI KARAKOL
# =========================================================================
K = 16
Z_TEMEL = 16                 # zemin kat dosemesi ustu
Z_UST = 224                  # ust kat dosemesi ustu (doseme 208..224)
Z_TAVAN = 400                # ust kat tavani alti
X0, Y0, X1, Y1 = BINA
XW, XE = -326, 26            # ic duvar eksenleri (hol: XW..XE)
MERDIVEN = (-318, 330, -190, 650)   # x0, y0, x1, y1 (kuzeye dogru yukselir)
YAPILAR['karakol'] = (X0, Y0, X1, Y1, True)

def kutu6(x0, y0, z0, x1, y1, z1, m, detay=False, olcek=None):
    if x1 > x0 and y1 > y0 and z1 > z0:
        H.kutu6(x0, y0, z0, x1, y1, z1, m, olcek=olcek, detay=detay)

def delikli_duvar(eksen, a, b, c0, c1, z0, z1, delikler, m):
    """eksen 'x': duvar x boyunca (a..b), kalinlik y=c0..c1. delik: (da, db, za, zb)."""
    def bx(p0, p1, q0, q1):
        if eksen == 'x': kutu6(p0, c0, q0, p1, c1, q1, m)
        else: kutu6(c0, p0, q0, c1, p1, q1, m)
    p = a
    for (da, db, za, zb) in sorted(delikler):
        bx(p, da, z0, z1)
        bx(da, db, z0, za)
        bx(da, db, zb, z1)
        p = db
    bx(p, b, z0, z1)

def cerceve(eksen, c0, c1, da, db, za, zb, kapi):
    """pervaz: aciklik cevresi, duvarin iki yuzunde 4 birim tasar."""
    fm = KASA if kapi else PERVAZ
    for (lo, hi) in ((c0 - 4, c0), (c1, c1 + 4)):
        def box(p0, p1, q0, q1, o):
            if eksen == 'x': H.kutu(p0, lo, q0, p1, hi, q1, fm, olcek=o, detay=True)
            else: H.kutu(lo, p0, q0, hi, p1, q1, fm, olcek=o, detay=True)
        box(da - 6, da, za, zb + 6, (8, 128))
        box(db, db + 6, za, zb + 6, (8, 128))
        box(da - 6, db + 6, zb, zb + 6, (128, 8))
        if not kapi:
            box(da - 8, db + 8, za - 6, za, (128, 8))

def pen(m, kat):    # pencere 72x80; kullanici: "ayakta bile yolu goremiyoruz" ->
    za = (Z_TEMEL if kat == 0 else Z_UST) + 36       # esik taban+36, ust taban+116
    return (m - 36, m + 36, za, za + 80)              # (goz hizasi taban+60 icinde)

def kapi(m, kat, gen=96):
    z = Z_TEMEL if kat == 0 else Z_UST
    return (m - gen // 2, m + gen // 2, z, z + 128)

# dis duvar acikliklari
DIS_DELIK = {
    'g': [kapi(-150, 0, 112), pen(-600, 0), pen(-440, 0), pen(120, 0), pen(300, 0),
          pen(-600, 1), pen(-440, 1), pen(-86, 1), pen(120, 1), pen(300, 1)],
    'k': [kapi(-60, 0), pen(-560, 0), pen(250, 0), pen(-560, 1), pen(-250, 1), pen(250, 1)],
    'b': [pen(300, 0), pen(620, 0), pen(300, 1), pen(620, 1)],
    'd': [pen(300, 0), pen(620, 0), pen(300, 1), pen(620, 1)],
}
DIS_M = lambda ic_yuz, dis_yuz, ust: {'*': TUGLA if not ust else SIVA, ic_yuz: SIVA,
                                     dis_yuz: TUGLA if not ust else SIVA}
# temel (tugla, zemin kati alti)
kutu6(X0, Y0, -24, X1, Y1, Z_TEMEL, {'*': TEMEL, '+z': TABAN})
# dis duvarlar iki parca: zemin kat (tugla dis) + ust kat (siva dis), arada kornis
for (kat, z0, z1) in ((0, Z_TEMEL, Z_UST), (1, Z_UST, Z_TAVAN + 16)):
    sec = lambda L: [d for d in L if (d[2] < z1 and d[3] > z0)]
    ust = kat == 1
    delikli_duvar('x', X0, X1, Y0, Y0 + K, z0, z1, sec(DIS_DELIK['g']), DIS_M('+y', '-y', ust))
    delikli_duvar('x', X0, X1, Y1 - K, Y1, z0, z1, sec(DIS_DELIK['k']), DIS_M('-y', '+y', ust))
    delikli_duvar('y', Y0 + K, Y1 - K, X0, X0 + K, z0, z1,
                  [(Y0 + d[0] - 0, Y0 + d[1], d[2], d[3]) for d in sec(DIS_DELIK['b'])], DIS_M('+x', '-x', ust))
    delikli_duvar('y', Y0 + K, Y1 - K, X1 - K, X1, z0, z1,
                  [(Y0 + d[0], Y0 + d[1], d[2], d[3]) for d in sec(DIS_DELIK['d'])], DIS_M('-x', '+x', ust))
# kapi/pencere cerceveleri kullanici istegiyle kaldirildi
# kornis bandi (katlar arasi) ve sacak
for (a, b, c, d) in ((X0 - 6, Y0 - 6, X1 + 6, Y0), (X0 - 6, Y1, X1 + 6, Y1 + 6),
                     (X0 - 6, Y0, X0, Y1), (X1, Y0, X1 + 6, Y1)):
    H.kutu(a, b, Z_UST - 10, c, d, Z_UST + 4, KORNIS, detay=True)
# ara doseme (merdiven boslugu acik)
mx0, my0, mx1, my1 = MERDIVEN
dm = {'*': TRIM, '+z': TABAN, '-z': SIVA}
kutu6(X0 + K, Y0 + K, Z_UST - 16, mx0, Y1 - K, Z_UST, dm)
kutu6(mx1, Y0 + K, Z_UST - 16, X1 - K, Y1 - K, Z_UST, dm)
kutu6(mx0, Y0 + K, Z_UST - 16, mx1, my0, Z_UST, dm)
kutu6(mx0, my1, Z_UST - 16, mx1, Y1 - K, Z_UST, dm)
# tavan
kutu6(X0, Y0, Z_TAVAN, X1, Y1, Z_TAVAN + 16, {'*': TRIM, '-z': SIVA, '+z': CAULK})
# ic duvarlar (12 kalin): zemin ve ust kat; her katta bir kapi
for xw in (XW, XE):
    ic = {'*': SIVA}
    delikli_duvar('y', Y0 + K, Y1 - K, xw - 6, xw + 6, Z_TEMEL, Z_UST - 16,
                  [(230 - 48, 230 + 48, Z_TEMEL, Z_TEMEL + 128)], ic)
    delikli_duvar('y', Y0 + K, Y1 - K, xw - 6, xw + 6, Z_UST, Z_TAVAN,
                  [(730 - 48, 730 + 48, Z_UST, Z_UST + 128)], ic)
# ust kat: hol ile dogu oda arasinda ust holu bolen kisa duvar YOK (acik sahanlik)
# merdiven: 12 basamak x 16 yukselti, kuzeye
n = 12
kosu = (my1 - my0) / float(n)
for k in range(n):
    yb = my0 + k * kosu
    zt = Z_TEMEL + (k + 1) * (Z_UST - Z_TEMEL) / float(n)
    H.kutu6(mx0, yb, Z_TEMEL, mx1, my1 if k == n - 1 else yb + kosu, zt,
            {'*': TRIM, '+z': BASAMAK, '-y': BASAMAK})
# merdiven korkulugu (bosluk kenari: dogu ve guney)
H.kutu(mx1, my0, Z_UST, mx1 + 6, my1, Z_UST + 40, TRIM, detay=True)
H.kutu(mx0, my0 - 6, Z_UST, mx1 + 6, my0, Z_UST + 40, TRIM, detay=True)
for yy in range(int(my0), int(my1) + 1, 80):
    H.kutu(mx1, yy, Z_UST, mx1 + 6, yy + 6, Z_UST + 40, KIRIS, detay=True)
H.kutu(mx1, my0, Z_UST, mx1 + 8, my1, Z_UST + 48, SINIR, SINIR, alt=SINIR)
H.kutu(mx0, my0 - 8, Z_UST, mx1 + 8, my0, Z_UST + 48, SINIR, SINIR, alt=SINIR)

# cati: kirma (kalkan yok) -- iki egik yuz + mahya
def cati(x0, y0, x1, y1, z_alt, yuk=170, sacak=40):
    ym = (y0 + y1) / 2.0
    ust = z_alt + yuk
    H.kama(x0 - sacak, y0 - sacak, x1 + sacak, ym, z_alt, z_alt + 8, ust, '+y', CATI, TRIM, alt=TRIM)
    H.kama(x0 - sacak, ym, x1 + sacak, y1 + sacak, z_alt, z_alt + 8, ust, '-y', CATI, TRIM, alt=TRIM)
    H.kutu(x0 - sacak, ym - 8, ust - 4, x1 + sacak, ym + 8, ust + 8, TRIM, detay=True)
    # kalkan duvarlari (dogu/bati ucgen yerine siva kutu basamak)
    for (xa, xb) in ((x0, x0 + K), (x1 - K, x1)):
        for k in range(6):
            dz = yuk * k / 6.0
            yy = (ym - y0) * k / 6.0
            kutu6(xa, y0 + yy, z_alt + dz, xb, y1 - yy, z_alt + dz + yuk / 6.0 + 2, {'*': SIVA})
    return ust
cati(X0, Y0, X1, Y1, Z_TAVAN + 16)
for (bx, by) in ((X0 + 120, Y1 - 150), (X1 - 160, Y0 + 150)):
    H.kutu(bx, by, Z_TAVAN + 16, bx + 48, by + 48, Z_TAVAN + 230, TUGLA, detay=True)
# giris sundurmasi (kroki: on cephede cikinti)
H.kama(-150 - 120, Y0 - 150, -150 + 120, Y0, -16, 0, Z_TEMEL, '+y', TEMEL, TEMEL, alt=CAULK)
for k, dy in enumerate((0, 50, 100)):
    pass
for xx in (-150 - 112, -150 + 104):
    H.kutu(xx, Y0 - 146, Z_TEMEL, xx + 12, Y0 - 134, 190, TRIM, detay=True)
H.kama(-150 - 140, Y0 - 170, -150 + 140, Y0, 190, 196, 236, '+y', CATI, TRIM, alt=TRIM, detay=True)

H.kama(-130, Y1, 10, Y1 + 110, -16, 0, Z_TEMEL, '-y', TEMEL, TEMEL, alt=CAULK)   # arka kapi rampasi
# merdiven: basamaklarin ustune gorunmez yurunur rampa ('clip': oyuncu + AI);
# basamak koseleriyle hemen hemen ayni hizada -> AI yokus yukari bag kurar
# rampa tum basamak koselerinin USTUNDE (olculdu: 26'lik on uzatma koseleri
# 0.4 birim disarida birakiyordu -> rampa dugumleri 'in solid')
# Merdiven rampasi: gorunmez KATI (caulk). Basamak yukseltisi 208/12 = 17.33
# (16 degil!). Rampa tum basamak ON-UST koselerinden gecer; ilk tasarim ust
# basamaklarin 14 birim altinda kaliyordu -> AI yokus yukari bag kuramiyordu
# (yol_denetim olcumu: z 167 ustu baglanti yoktu).
_kosu = (MERDIVEN[3] - MERDIVEN[1]) / 12.0
_r0, _r1 = MERDIVEN[1] - _kosu, MERDIVEN[1] + 11 * _kosu      # z: Z_TEMEL -> Z_UST
H.kama(MERDIVEN[0], _r0, MERDIVEN[2], _r1, Z_TEMEL, Z_TEMEL + 1, Z_UST, '+y',
       CAULK, CAULK, alt=CAULK, detay=True)
MERDIVEN_Z = lambda y: Z_TEMEL + (Z_UST - Z_TEMEL) * max(0.0, min(1.0, (y - _r0) / (_r1 - _r0)))

# ic esya (taban z: zemin 16, ust 224). crate01_snow ustu = taban + 26 (olculdu)
ESYA = [
    # ZEMIN BATI -- komuta/telsiz odasi
    ('furniture_duhoc_bunker_table', -520, 470, Z_TEMEL, 0), ('furniture_duhoc_chair', -520, 395, Z_TEMEL, 90),
    ('furniture_duhoc_chair', -520, 545, Z_TEMEL, 270), ('furniture_duhoc_chair', -615, 470, Z_TEMEL, 0),
    ('furniture_file_cabinet_long_a', -650, 772, Z_TEMEL, 270), ('furniture_file_cabinet_long_a', -575, 772, Z_TEMEL, 270),
    ('furniture_bookshelveswide', -672, 640, Z_TEMEL, 0), ('crate01_snow', -400, 760, Z_TEMEL, 0),
    ('military_german_fieldradio_green', -400, 760, Z_TEMEL + 26, 200), ('prop_crate_wehrmacht3', -420, 190, Z_TEMEL, 10),
    # ZEMIN DOGU -- kogus
    ('furniture_bed_bunker1', 340, 260, Z_TEMEL, 90), ('furniture_bed_bunker1', 340, 470, Z_TEMEL, 90),
    ('furniture_bed_bunker1', 340, 680, Z_TEMEL, 90), ('prop_potbelly_stove', 230, 770, Z_TEMEL, 0),
    ('furniture_armoire', 85, 765, Z_TEMEL, 270), ('furniture_smallfoldingtable', 150, 430, Z_TEMEL, 0),
    ('furniture_utilitychair1', 150, 500, Z_TEMEL, 270), ('crate01_snow', 110, 180, Z_TEMEL, 0),
    ('crate02_snow', 170, 180, Z_TEMEL, 15),
    # UST BATI -- subay odasi
    ('furniture_rolltopdesk', -660, 700, Z_UST, 0), ('furniture_duhoc_chair', -600, 700, Z_UST, 180),
    ('furniture_duhoc_table', -500, 450, Z_UST, 0), ('furniture_plainchair', -500, 385, Z_UST, 90),
    ('furniture_bed_bunker2', -640, 260, Z_UST, 90), ('furniture_file_cabinet_short_a', -400, 780, Z_UST, 270),
    # UST DOGU -- savunma/depo: cephane
    ('crate01_snow', 330, 740, Z_UST, 0), ('crate02_snow', 330, 690, Z_UST, 30), ('crate01_snow', 270, 740, Z_UST, 45),
    ('prop_crate_wehrmacht1', 300, 580, Z_UST, 0), ('military_flak88_box_open', 160, 760, Z_UST, 0),
]
for (m, x, y, z, yaw) in ESYA:
    model(m, x, y, z, yaw)
# ilk ic tur goruntusu: odalar cok karanlikti -> her odada iki lamba
for (x, y) in ((-600, 300), (-460, 660), (100, 300), (300, 660), (-100, 250), (-100, 650)):
    isik(x, y, Z_UST - 36, 380, 1.15)
    isik(x, y, Z_TAVAN - 36, 380, 1.15)
# kapi onu aydinlatma
isik(-150, Y0 - 100, 180, 300, .7)

# LAMBRI: ic duvarlarin alt 32 birimi ahsap kaplama (kapi acikliklari atlanir)
def lambri(eksen, yuz, yon, a, b, zf, bosluk):
    p = a
    for (g0, g1) in sorted(bosluk) + [(b, b)]:
        if g0 > p:
            if eksen == 'x':
                y0_, y1_ = (yuz, yuz + 3) if yon > 0 else (yuz - 3, yuz)
                H.kutu(p, y0_, zf, g0, y1_, zf + 32, TAHTA3, detay=True)
            else:
                x0_, x1_ = (yuz, yuz + 3) if yon > 0 else (yuz - 3, yuz)
                H.kutu(x0_, p, zf, x1_, g0, zf + 32, TAHTA3, detay=True)
        p = max(p, g1)
for (kat, zf) in ((0, Z_TEMEL), (1, Z_UST)):
    on_kapi = [(-206, -94)] if kat == 0 else []
    arka_kapi = [(-108, -12)] if kat == 0 else []
    lambri('x', Y0 + K, +1, X0 + K, XW - 6, zf, [])
    lambri('x', Y0 + K, +1, XW + 6, XE - 6, zf, on_kapi)
    lambri('x', Y0 + K, +1, XE + 6, X1 - K, zf, [])
    lambri('x', Y1 - K, -1, X0 + K, XW - 6, zf, [])
    lambri('x', Y1 - K, -1, XW + 6, XE - 6, zf, arka_kapi)
    lambri('x', Y1 - K, -1, XE + 6, X1 - K, zf, [])
    lambri('y', X0 + K, +1, Y0 + K, Y1 - K, zf, [])
    lambri('y', X1 - K, -1, Y0 + K, Y1 - K, zf, [])
    ky = 230 if kat == 0 else 730
    for xw in (XW, XE):
        bos = [(ky - 48, ky + 48)]
        lambri('y', xw - 6, -1, Y0 + K, Y1 - K, zf, bos)
        hol_bos = bos + ([(MERDIVEN[1] - 8, MERDIVEN[3] + 8)] if xw == XW else [])
        lambri('y', xw + 6, +1, Y0 + K, Y1 - K, zf, hol_bos)

# KALDIRILABILIR GORUNMEZ DUVARLAR (script_brushmodel + clip_player; stok
# crossroads.gsc barn_wall_blocker notsolid kalibi)
ENGEL_KAYDIR = 2000
def engel(ad, kutular):
    bl = []
    for (a, b, c, d, e, f) in kutular:
        H.kutu(a, b, c + ENGEL_KAYDIR, d, e, f + ENGEL_KAYDIR, SINIR, SINIR, alt=SINIR, hedef=bl)
    H.ent('script_brushmodel', brushlar=bl, targetname=ad)
# savunmada kapi ve pencereler: gercek duvar hissi (kullanici). Derlemede
# yukarida -> yol agi engelsiz; GSC ekip iceri girince indirir.
pk = [(-206, Y0 - 4, Z_TEMEL, -94, Y0 + K + 4, Z_TEMEL + 128),
      (-108, Y1 - K - 4, Z_TEMEL, -12, Y1 + 4, Z_TEMEL + 128)]
for yon, L in DIS_DELIK.items():
    for (da, db, za, zb) in L:
        if zb - za >= 120:
            continue
        if yon == 'g': pk.append((da, Y0 - 4, za, db, Y0 + K + 4, zb))
        elif yon == 'k': pk.append((da, Y1 - K - 4, za, db, Y1 + 4, zb))
        elif yon == 'b': pk.append((X0 - 4, Y0 + da, za, X0 + K + 4, Y0 + db, zb))
        else: pk.append((X1 - K - 4, Y0 + da, za, X1 + 4, Y0 + db, zb))
engel('savunma_duvar', pk)
# kullanici: "A bolgesini temizlemeden B ve C'ye gidilemesin" -> bati hat (x=-1600)
# ve iki kopru ortasi; A temizlenince GSC bu engeli kaldirir.
bc = [(-1608, -3400, -400, -1592, 3500, 700)]
for yk, zk in zip(KOPRU_Y, KOPRU_Z):
    xr = dere_x(yk)
    bc.append((xr - 8, yk - 130, zk - 60, xr + 8, yk + 130, zk + 400))
engel('engel_bc', bc)
# sinir gecitleri acik: oyuncuyu GSC tutar (metel_sinir.gsc)

# avlu duvari (alcak tugla, kapilar guney ve kuzey, x=-150)
ax0, ay0, ax1, ay1 = AVLU
def avlu_duvar(eksen, a, b, c, kapilar):
    p = a
    for (m, g) in sorted(kapilar):
        if eksen == 'x': kutu6(p, c - 12, -40, m - g / 2, c + 12, 72, {'*': TUGLA, '+z': KAR2})
        else: kutu6(c - 12, p, -40, c + 12, m - g / 2, 72, {'*': TUGLA, '+z': KAR2})
        for q in (m - g / 2 - 24, m + g / 2):
            if eksen == 'x': H.kutu(q, c - 18, -40, q + 24, c + 18, 110, TEMEL, detay=True)
            else: H.kutu(c - 18, q, -40, c + 18, q + 24, 110, TEMEL, detay=True)
        p = m + g / 2
    if eksen == 'x': kutu6(p, c - 12, -40, b, c + 12, 72, {'*': TUGLA, '+z': KAR2})
    else: kutu6(c - 12, p, -40, c + 12, b, 72, {'*': TUGLA, '+z': KAR2})
avlu_duvar('x', ax0, ax1, ay0, [(-150, 300)])
avlu_duvar('x', ax0, ax1, ay1, [(-150, 300)])
avlu_duvar('y', ay0 + 12, ay1 - 12, ax0, [])
avlu_duvar('y', ay0 + 12, ay1 - 12, ax1, [(450, 220)])
YAPILAR['avlu_duvar'] = None   # cizgi engel: asagida DUVARLAR listesinde
DUVARLAR = [(ax0, ay0, ax1, ay0), (ax0, ay1, ax1, ay1), (ax0, ay0, ax0, ay1), (ax1, ay0, ax1, ay1)]
DUVAR_KAPI = [(-150, ay0, 150), (-150, ay1, 150), (ax1, 450, 110)]
del YAPILAR['avlu_duvar']

for (m, x, y, yaw) in [('vehicle_opel_blitz_snow_static', 420, -150, 180),
                       ('crate01_snow', 600, 800, 0), ('crate02_snow', 600, 740, 20), ('crate01_snow', 555, 800, 40),
                       ('prop_barrel_benzin_snow', -900, 880, 0), ('prop_barrel_benzin_snow', -870, 900, 0),
                       ('military_sandbag_snow_longsection', -620, -150, 0), ('military_sandbag_snow_longsection', -508, -150, 0),
                       ('military_sandbag_snow_longsection', 160, -150, 0), ('military_sandbag_snow_longsection', 48, -150, 0),
                       ('powerpole01', -1100, -420, 0), ('powerpole01', 800, -420, 0)]:
    model(m, x, y, None, yaw)
for x in range(-980, 700, 230):
    if abs(x + 150) > 260:
        model('caen_barbedwire_3', x, ay0 - 90, None, random.Random(x).randint(0, 30))

# ---------------------------------------------------------------- kulubeler
def kulube(cx, cy, w, d, h, yaw_kapi='g'):
    x0, y0 = cx - w // 2, cy - d // 2
    z = min(yukseklik(x0 + a, y0 + b) for a in (0, w) for b in (0, d)) - 24
    zt = max(yukseklik(x0 + a, y0 + b) for a in (0, w) for b in (0, d))
    kutu6(x0, y0, z, x0 + w, y0 + d, zt + 8, {'*': TEMEL, '+z': TABAN})
    for (a, b, c, e) in ((x0, y0, x0 + w, y0 + 10), (x0, y0 + d - 10, x0 + w, y0 + d),
                         (x0, y0 + 10, x0 + 10, y0 + d - 10), (x0 + w - 10, y0 + 10, x0 + w, y0 + d - 10)):
        H.kutu(a, b, zt + 8, c, e, zt + h, TAHTA3, TAHTA3)
    H.kama(x0 - 16, y0 - 16, x0 + w + 16, y0 + d + 16, zt + h, zt + h + 6, zt + h + 50, '+y', CATI, TAHTA3, alt=TAHTA3)
    YAPILAR['kulube_%d_%d' % (cx, cy)] = (x0, y0, x0 + w, y0 + d, False)
kulube(*[int(v) for v in W(692, 722)], 176, 144, 120)          # guney yol kenari
kulube(*[int(v) for v in W(338, 492)], 160, 128, 112)          # B yolu dibi

# ---------------------------------------------------------------- B mevzisi
bx, by = B_MERKEZ
MB = (bx - 60, by + 40)          # havan
for k in range(8):
    if k == 5:          # arka (bati-guneybati) acik: giris
        continue
    a = math.radians(k * 45)
    model('military_sandbag_snow_longsection', MB[0] + math.cos(a) * 165, MB[1] + math.sin(a) * 165,
          B_UST, k * 45 + 90)
# havan ekibi stok _mortarteam animasyonlariyla kullanir -> script_model
# (prop_mortar statik misc_model OLAMAZ: cok kemikli, olculdu)
H.ent('script_model', model='xmodel/prop_mortar', targetname='havan_b_top',
      origin=(MB[0], MB[1], B_UST), angles=(0, 315, 0))
MODELLER.append(('prop_mortar', MB[0], MB[1]))
for (m, dx, dy, yaw) in (('prop_mortar_crate', 70, -60, 20), ('prop_mortar_crate', 70, -10, 0),
                         ('prop_mortar_case', -60, 70, 45), ('prop_mortar_case', -20, 90, 10)):
    model(m, MB[0] + dx, MB[1] + dy, B_UST, yaw)
for i, (dx, dy, r, h) in enumerate([(260, 180, 70, 70), (-250, 150, 90, 95), (-120, -260, 80, 60),
                                    (300, -180, 60, 55), (60, 300, 75, 80)]):
    kaya(bx + dx, by + dy, r, h, 100 + i)
for (dx, dy) in ((-300, 280), (200, 330), (-330, -120), (330, 60)):
    model('tree_snow_pine_lg_c', bx + dx, by + dy, None, random.Random(dx).randint(0, 359))

# ---------------------------------------------------------------- C mevzisi
cx_, cy_ = C_MERKEZ
MC = (cx_ - 20, cy_ + 60)
# dogal kaya cukuru: kayalar halka, bati (patika) tarafi acik, tek kum torbasi hatti
for i, (a, r, h) in enumerate([(20, 70, 85), (65, 80, 100), (110, 75, 90), (155, 70, 70),
                               (290, 65, 60), (330, 75, 80)]):
    t = math.radians(a)
    kaya(MC[0] + math.cos(t) * 230, MC[1] + math.sin(t) * 230, r, h, 200 + i)
for k, dx in enumerate((-112, 0, 112)):
    model('military_sandbag_snow_longsection', MC[0] - 170, MC[1] + dx, C_UST, 90)
H.ent('script_model', model='xmodel/prop_mortar', targetname='havan_c_top',
      origin=(MC[0], MC[1], C_UST), angles=(0, 210, 0))
MODELLER.append(('prop_mortar', MC[0], MC[1]))
for (m, dx, dy, yaw) in (('prop_mortar_crate', 60, 70, 0), ('prop_mortar_crate2', 110, 40, 30),
                         ('prop_mortar_case', 70, -70, 60)):
    model(m, MC[0] + dx, MC[1] + dy, C_UST, yaw)
# sirt boyunca dagilmis kayalar (acik, kayalik)
for i, (dx, dy, r, h) in enumerate([(-200, -500, 90, 70), (150, -380, 70, 55), (230, 450, 100, 90),
                                    (-240, 520, 80, 65), (40, 760, 90, 75), (-120, -760, 70, 50),
                                    (260, -120, 60, 50)]):
    kaya(cx_ + dx, cy_ + dy, r, h, 300 + i)
for (dx, dy) in ((300, 600), (-280, 800), (330, -600)):
    model('tree_snow_pine_sm_c', cx_ + dx, cy_ + dy, None, random.Random(dy).randint(0, 359))

# ---------------------------------------------------------------- orman
random.seed(43)
CAM = ['tree_snow_pine_xl_c', 'tree_snow_pine_lg_c', 'tree_snow_pine_lg_c', 'tree_snow_pine_sm_c']
def agac_uygun(x, y, ic):
    if yol_mesafe(x, y) < 230:
        return False
    if dere_mes(x, y) < DERE_DIS + 120:
        return False
    if AVLU[0] - 250 < x < AVLU[2] + 250 and AVLU[1] - 250 < y < AVLU[3] + 250:
        return False
    if math.hypot(x - B_MERKEZ[0], y - B_MERKEZ[1]) < 420 or math.hypot(x - C_MERKEZ[0], (y - C_MERKEZ[1]) / 1.55) < 380:
        return False
    if any(abs(x - a) < 150 and abs(y - b) < 150 for (a, b) in AGAC):
        return False
    for ad, v in YAPILAR.items():
        if v and v[0] - 160 < x < v[2] + 160 and v[1] - 160 < y < v[3] + 160:
            return False
    if not (SX0 + 96 < x < SX1 - 96 and SY0 + 96 < y < SY1 - 96):
        return False
    return icinde(x, y) == ic
# icerde: kenar bandi + kroki ormanlari (kuzey tepeler, guney yan, B cevresi)
ORMAN = [(W(560, 175), 450, 16), (W(720, 140), 420, 14), (W(990, 150), 380, 12),
         (W(430, 700), 420, 14), (W(800, 800), 420, 14), (W(1010, 700), 330, 10),
         (W(170, 500), 380, 12), (W(300, 140), 330, 10), (W(1160, 200), 300, 8),
         (W(560, 520), 200, 4), (W(760, 520), 220, 5), (W(450, 450), 220, 5)]
for ((ox, oy), r, n) in ORMAN:
    for k in range(n * 3):
        if n <= 0:
            break
        a = random.uniform(0, 2 * math.pi); rr = r * math.sqrt(random.random())
        x, y = ox + math.cos(a) * rr, oy + math.sin(a) * rr
        if agac_uygun(x, y, True):
            model(random.choice(CAM), x, y, None, random.randint(0, 359)); n -= 1
for x in range(SX0 + 160, SX1 - 159, 230):                      # kenar bandi (iceride)
    for y in range(SY0 + 160, SY1 - 159, 230):
        x2, y2 = x + random.randint(-90, 90), y + random.randint(-90, 90)
        if icinde(x2, y2) and kenar_mes(x2, y2) < 420 and agac_uygun(x2, y2, True):
            model(random.choice(CAM), x2, y2, None, random.randint(0, 359))
for x in range(SX0 + 160, SX1 - 159, 260):                      # disarida sik bant
    for y in range(SY0 + 160, SY1 - 159, 260):
        x2, y2 = x + random.randint(-100, 100), y + random.randint(-100, 100)
        o = disari(x2, y2)
        if 60 < o < 1500 and agac_uygun(x2, y2, False):
            model(random.choice(CAM[:3]), x2, y2, None, random.randint(0, 359), kayit=False)
# olu agac ve kutukler (yol kenarlari, orman acikliklari)
for (px, py, m) in [(600, 760, 'tree_destroyed_snow_stump_a'), (480, 600, 'tree_destoyed_snow_trunk_a'),
                    (760, 600, 'tree_destroyed_snow_fallen_log_a'), (420, 400, 'tree_destroyed_snow_stump_b'),
                    (950, 690, 'tree_destoyed_snow_trunk_b'), (700, 880, 'tree_destroyed_snow_fallen_log_a')]:
    x, y = W(px, py)
    if agac_uygun(x, y, True):
        model(m, x, y, None, random.randint(0, 359))

# baslangic
BASLANGIC = W(655, 952)       # kullanici: "spawn biraz daha geride"
# kullanici: "baslangicta onumuzde bir yapi olsun ki direkt catisma baslamasin"
# -> yikik tas ciftlik evi: uc duvar (biri yarim), cati cokmus, moloz.
def yikik_ev(cx, cy, w, d):
    x0, y0, x1, y1 = cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2
    zb = min(yukseklik(x, y) for x in (x0, x1) for y in (y0, y1)) - 30
    zt = max(yukseklik(x, y) for x in (x0, x1) for y in (y0, y1))
    dm = {'*': TUGLA, '+z': KAR2}
    kutu6(x0, y1 - 20, zb, x1, y1, zt + 170, dm)                    # kuzey (tam)
    kutu6(x0, y0, zb, x0 + 20, y1 - 20, zt + 150, dm)               # bati
    kutu6(x1 - 20, y0 + 70, zb, x1, y1 - 20, zt + 110, dm)          # dogu (yikik)
    kutu6(x0 + 20, y0, zb, x0 + 110, y0 + 20, zt + 90, dm)          # guney kalinti
    kaya(x1 - 40, y0 + 30, 40, 30, 900, gom=20)                     # moloz (dogu kosesi disi)
    global YIKIK
    YIKIK = (x0, y0, x1, y1)
yikik_ev(*W(673, 910), 360, 220)
yx0, yy0, yx1, yy1 = YIKIK
YIKIK_DUVAR = [(yx0, yy1 - 10, yx1, yy1 - 10), (yx0 + 10, yy0, yx0 + 10, yy1),
               (yx1 - 10, yy0 + 70, yx1 - 10, yy1), (yx0, yy0 + 10, yx0 + 110, yy0 + 10)]
BASLANGIC = ((yx0 + yx1) / 2.0, yy0 - 120)       # kullanici: "kirik binanin ONUNDE dogalim"
H.ent('info_player_start', origin=(BASLANGIC[0], BASLANGIC[1], round(yukseklik(*BASLANGIC) + 8, 1)),
      angles=(0, 90, 0))

# ---------------------------------------------------------------- dogrulama
def dogrula():
    var = set()
    for p in glob.glob(os.path.join(KOK, 'main', '*.iwd')):
        for n in zipfile.ZipFile(p).namelist():
            var.add(n.lower())
    eksik = [m for m in sorted(H.malzemeler) if m not in ('caulk', 'clip_player', 'trigger')
             and 'materials/' + m.lower() not in var]
    modeller = sorted({d['model'] for d, _ in H.ents if 'model' in d and d['classname'] in ('misc_model', 'script_model')})
    eksik_m = [m for m in modeller if m.lower() not in var]
    return eksik, eksik_m

H.ent('misc_turret', model='xmodel/weapon_mg42', weaponinfo='mg42_bipod_stand',
      origin=(SX0 + 300, SY0 + 300, round(yukseklik(SX0 + 300, SY0 + 300), 1)), angles=(0, 0, 0))

def sinir_gsc():
    o = ['// metel_sinir.gsc -- gen_metel.py URETIR, elle duzenlemeyin.',
         '// Oyuncu siniri: clip_player AI\'yi de durdurdugu icin (olculdu) sinir',
         '// gecitleri acik; oyuncuyu bu cokgen ile betik tutar.',
         'cokgen()', '{', '\tp = [];']
    for (x, y) in POLI:
        o.append('\tp[p.size] = (%d, %d, 0);' % (round(x), round(y)))
    o += ['\treturn p;', '}', '']
    open(os.path.join(KOK, 'main', 'maps', 'metel_sinir.gsc'), 'w', newline='\r\n').write('\n'.join(o) + '\n')
sinir_gsc()

import ent_metel
ent_metel.yerlestir(sys.modules[__name__])

if __name__ == '__main__':
    eksik, eksik_m = dogrula()
    if eksik or eksik_m:
        raise SystemExit('EKSIK VARLIK! malzeme: %s model: %s' % (eksik, eksik_m))
    r = H.yaz(os.path.join(KOK, 'map_source', 'metel.map'))
    print('dunya brush/mesh: %(dunya_brush)d  entity: %(entity)d  bayt: %(bayt)d' % r)
    print('malzemeler:', r['malzeme'])
    print('misc_model: %d  kaya: %d  agac: %d  isik: %d' % (
        sum(1 for d, _ in H.ents if d['classname'] == 'misc_model'), len(KAYALAR), len(AGAC),
        sum(1 for d, _ in H.ents if d['classname'] == 'light')))
    print('B ust z=%.0f  C ust z=%.0f  kopru z=%s  baslangic z=%.0f' % (
        yukseklik(*B_MERKEZ), yukseklik(*C_MERKEZ), [round(z) for z in KOPRU_Z], yukseklik(*BASLANGIC)))
