# -*- coding: utf-8 -*-
"""
ent_metel.py -- yerlesim (node, siper, zincir, spawner, havan isabet noktalari).
Anahtar adlari krasnoye'de oyunda calismis olanlar (stok d3dbsp'den olculmus):
  friendly_wave, spawnflags 1/7, script_aigroup, node -> target zinciri.

KESIN SAYILAR (kullanici): A 15, B 10, C 10 Alman.
Her spawner/node bosluk denetiminden gecer ("in solid" 0 hedefi).
"""
import math

YARICAP = (('tree_destroyed_snow_fallen', 150), ('tree_destoyed', 70), ('tree_destroyed', 60),
           ('vehicle_', 170), ('caen_barbedwire', 100), ('tree_', 44), ('military_sandbag', 64),
           ('powerpole', 20), ('prop_mortar_crate', 40), ('prop_mortar_case', 26), ('prop_mortar', 60),
           ('crate', 44), ('prop_crate', 50), ('prop_barrel', 26), ('prop_potbelly', 34),
           ('furniture_bed_bunker', 110), ('furniture_duhoc_bunker_table', 90), ('furniture_duhoc_table', 80),
           ('furniture_file_cabinet_long', 75), ('furniture_file_cabinet', 45), ('furniture_bookshelves', 75),
           ('furniture_armoire', 65), ('furniture_rolltopdesk', 65), ('furniture_smallfoldingtable', 45),
           ('furniture_duhoc_chair', 28), ('furniture_utilitychair', 28), ('military_flak88_box', 40),
           ('furniture_plainchair', 26), ('military_german_fieldradio', 0))

def yerlestir(G):
    H, yuk = G.H, G.yukseklik
    say = {}
    X0, Y0, X1, Y1 = G.BINA
    XW, XE = G.XW, G.XE
    mx0, my0, mx1, my1 = G.MERDIVEN
    ZT, ZU = G.Z_TEMEL, G.Z_UST

    DUGUM = []
    # g_connectpaths olcumu: bu noktalar C sirtinda kayalarla cevrili, baglantisiz
    YALNIZ = [(2960, 1394), (2732, 1550)]
    def ent(sinif, **kv):
        if sinif.startswith('node_'):
            x, y, z = kv['origin']
            if any(abs(x - a) < 40 and abs(y - b) < 40 for (a, b) in YALNIZ):
                return None
            if any(abs(x - a) < 24 and abs(y - b) < 24 and abs(z - c) < 60 for (a, b, c) in DUGUM):
                if 'targetname' not in kv:
                    return None
                for k in range(1, 12):
                    nx = x + 40 * k
                    if not any(abs(nx - a) < 24 and abs(y - b) < 24 and abs(z - c) < 60 for (a, b, c) in DUGUM):
                        kv['origin'] = (nx, y, z); break
            DUGUM.append(kv['origin'])
        say[sinif] = say.get(sinif, 0) + 1
        return H.ent(sinif, **kv)

    def tetik(sinif, x0, y0, z0, x1, y1, z1, **kv):
        bl = []
        H.kutu(x0, y0, z0, x1, y1, z1, 'trigger', 'trigger', alt='trigger', hedef=bl)
        say[sinif] = say.get(sinif, 0) + 1
        return H.ent(sinif, brushlar=bl, **kv)

    def zemin(x, y):
        """Mesh hucresinin GERCEK ucgen yuzeyi. Eski '4 kosenin en yuksegi'
        egimli arazide dugumleri 30-50 birim havada birakiyordu (olculdu:
        yikik ev icinde dugum z=103, zemin ~50) -> dostlar yol bulamayip
        DONUYORDU. Kosegen yonu bilinmedigi icin iki ucgenlemenin buyugu."""
        A = 128
        i = math.floor((x - G.SX0) / A); j = math.floor((y - G.SY0) / A)
        x0, y0 = G.SX0 + i * A, G.SY0 + j * A
        u, v = (x - x0) / float(A), (y - y0) / float(A)
        z00, z10 = yuk(x0, y0), yuk(x0 + A, y0)
        z01, z11 = yuk(x0, y0 + A), yuk(x0 + A, y0 + A)
        if u >= v:
            za = z00 + (z10 - z00) * u + (z11 - z10) * v
        else:
            za = z00 + (z01 - z00) * v + (z11 - z01) * u
        if u + v <= 1:
            zb = z00 + (z10 - z00) * u + (z01 - z00) * v
        else:
            zb = z11 + (z01 - z11) * (1 - u) + (z10 - z11) * (1 - v)
        ek = 3 if G.yol_mesafe(x, y) < 200 else 0
        return max(za, zb) + ek

    def zz(x, y, ust=8):
        return round(zemin(x, y) + ust, 1)

    def yaricap(m):
        for (on, r) in YARICAP:
            if m.startswith(on):
                return r
        return 36

    def duvar_mes(x, y):
        en = 1e9
        for (xa, ya, xb, yb) in G.YIKIK_DUVAR:
            en = min(en, G._seg(x, y, (xa, ya), (xb, yb)))
        for (xa, ya, xb, yb) in G.DUVARLAR:
            d = G._seg(x, y, (xa, ya), (xb, yb))
            for (kx, ky, g) in G.DUVAR_KAPI:
                if math.hypot(x - kx, y - ky) < g:
                    d = 1e9
            en = min(en, d)
        return en

    def serbest(x, y, r=26, kat=None):
        """kat None: dis mekan. kat 0/1: karakol ici zemin/ust kat."""
        if kat is None:
            if not G.icinde(x, y) and y < -3300:      # guney yolunun kopuk ucu (olculdu)
                return False
            if -290 <= x <= -10 and G.BINA[1] - 170 <= y <= G.BINA[1]:     # giris sundurmasi
                return False
            if not G.icinde(x, y) and not dis_koridor(x, y):
                return False
            if G.dere_mes(x, y) < G.DERE_DIS + 40 + r:
                return False
            for ad, v in G.YAPILAR.items():
                if v[0] - r - 12 <= x <= v[2] + r + 12 and v[1] - r - 12 <= y <= v[3] + r + 12:
                    return False
            if duvar_mes(x, y) < r + 20:
                return False
        else:
            if not (X0 + 16 + r <= x <= X1 - 16 - r and Y0 + 16 + r <= y <= Y1 - 16 - r):
                return False
            for xw, kapi_y in ((XW, 230 if kat == 0 else 730), (XE, 230 if kat == 0 else 730)):
                if abs(x - xw) < 6 + r and not abs(y - kapi_y) < 48 - r:
                    return False
            if mx0 - r - 8 <= x <= mx1 + r + 8 and my0 - r - 8 <= y <= my1 + (r + 8 if kat == 1 else r + 8):
                return False
        for (m, mx, my) in G.MODELLER:
            rr = yaricap(m)
            if rr and abs(x - mx) < rr + r and abs(y - my) < rr + r and math.hypot(x - mx, y - my) < rr + r:
                return False
        for (kx, ky, kr) in G.KAYALAR:
            if math.hypot(x - kx, y - ky) < kr + r + 10:
                return False
        return True

    GUNEY_HAT = G.YOL_HAT['guney'][0]
    GIRIS_HAT = [G.YOL_HAT[k][0] for k in ('guney', 'bati_giris', 'dogu_giris')]
    def dis_koridor(x, y):
        """harita disinda izinli alan: uc giris yolu (takviye ve karsi saldiri)."""
        for H_ in GIRIS_HAT:
            for i in range(len(H_) - 1):
                (ax, ay, _), (bx, by, _) = H_[i], H_[i + 1]
                if G._seg(x, y, (ax, ay), (bx, by)) < 170:
                    return True
        return False

    def yer_bul(x, y, r=26, kat=None, en=200):
        if serbest(x, y, r, kat):
            return (x, y)
        for rad in range(16, en + 1, 16):
            n = max(8, int(rad / 8))
            for k in range(n):
                a = 2 * math.pi * k / n
                px, py = round(x + rad * math.cos(a)), round(y + rad * math.sin(a))
                if serbest(px, py, r, kat):
                    return (px, py)
        return None

    def egim_ok(x, y, adim=80):
        z = yuk(x, y)
        return all(abs(yuk(x + dx, y + dy) - z) < 62 for (dx, dy) in ((adim, 0), (-adim, 0), (0, adim), (0, -adim)))

    # =====================================================================
    # 2. SIPER DUGUMLERI
    # =====================================================================
    SIPER = {'b': [], 'c': [], 'a_dis': [], 'a_zemin': [], 'a_ust': []}
    def siper(grup, tur, x, y, yaw, kat=None, r=24):
        if kat is None and not G.icinde(x, y):
            return None                     # harita disinda siper yok (kopuk kalıyordu)
        p = yer_bul(x, y, r, kat, 96)
        if not p or (kat is None and not egim_ok(*p, adim=60)):
            return None
        z = (ZT + 8) if kat == 0 else (ZU + 8) if kat == 1 else zz(*p)
        e = ent(tur, origin=(p[0], p[1], z), angles=(0, yaw, 0))
        if e is not None and grup:
            SIPER[grup].append((p[0], p[1], z, yaw))
        return p
    # B: kum torbasi halkasinin hemen ici (disari bakar) + rampa ustu kayalar
    MBx, MBy = G.MB
    for k in range(8):
        if k == 5:
            continue
        a = math.radians(k * 45)
        siper('b', 'node_cover_crouch', MBx + math.cos(a) * 115, MBy + math.sin(a) * 115, k * 45)
    bx, by = G.B_MERKEZ
    for (dx, dy, yaw) in ((150, 120, 0), (-150, 30, 200), (40, -230, 290), (220, -120, 330), (-60, 230, 90)):
        siper('b', 'node_cover_stand', bx + dx, by + dy, yaw)
    # C: kaya cukurunun ici + sirt boyunca
    MCx, MCy = G.MC
    for (dx, dy, yaw) in ((-120, -60, 180), (-120, 60, 180), (-120, 140, 160), (60, 150, 90), (100, -120, 270),
                          (-60, -170, 230), (150, 60, 0)):
        siper('c', 'node_cover_crouch', MCx + dx, MCy + dy, yaw)
    cx, cy = G.C_MERKEZ
    for (dx, dy, yaw) in ((-200, -380, 220), (150, -260, 300), (230, 330, 60), (-230, 400, 150), (-60, -600, 250)):
        siper('c', 'node_cover_stand', cx + dx, cy + dy, yaw)
    # A dis: kum torbalari, kamyon, avlu duvari arkasi (guneye bakar)
    for (x, y) in ((-560, -100), (-460, -100), (100, -100), (200, -100), (330, -60), (520, -60),
                   (-900, -220), (600, -230), (-900, 600), (620, 300), (-500, 920), (300, 920)):
        siper('a_dis', 'node_cover_crouch', x, y, 270 if y < 400 else 90)
    # A zemin: pencere arkalari ve kapi kenarlari
    for (x, y, yaw) in ((-600, 160, 270), (-440, 160, 270), (120, 160, 270), (300, 160, 270),
                        (-680, 420, 180), (380, 420, 0), (-560, 780, 90), (250, 780, 90),
                        (-250, 180, 270), (-40, 180, 270)):
        siper('a_zemin', 'node_cover_stand', x, y, yaw, kat=0)
    # A ust: pencere hatti
    for (x, y, yaw) in ((-600, 165, 270), (-440, 165, 270), (-86, 230, 270), (120, 230, 270), (300, 230, 270),
                        (-680, 420, 180), (-680, 740, 180), (380, 420, 0), (380, 740, 0), (-250, 780, 90),
                        (250, 780, 90)):
        siper('a_ust', 'node_cover_stand', x, y, yaw, kat=1)
    # ekip icin yol kenari siperler (agac/kaya yanlari) -- yaklasma boyunca
    for ad in ('guney', 'bati', 'gdogu', 'kuzey'):
        hat = G.YOL_HAT[ad][0]
        for i in range(0, len(hat) - 1):
            (ax, ay, _), (bx2, by2, _) = hat[i], hat[i + 1]
            mx_, my_ = (ax + bx2) / 2.0, (ay + by2) / 2.0
            L = math.hypot(bx2 - ax, by2 - ay) or 1
            qx, qy = -(by2 - ay) / L, (bx2 - ax) / L
            for s in (-1, 1):
                siper(None, 'node_cover_crouch', mx_ + qx * s * 160, my_ + qy * s * 160,
                      round(math.degrees(math.atan2(by2 - ay, bx2 - ax))) % 360)

    # =====================================================================
    # 1. YOL DUGUMLERI
    # =====================================================================
    ADIM = 150
    for x in range(G.SX0 + 96, G.SX1 - 95, ADIM):
        for y in range(G.SY0 + 96, G.SY1 - 95, ADIM):
            if not serbest(x, y) or not egim_ok(x, y):
                continue
            if (x, y) in ((1082, -2474), (4382, -1424)):     # baglantisiz kalan tekil noktalar (olculdu)
                continue
            ent('node_pathnode', origin=(x, y, zz(x, y)))
    # yollar boyunca sik dugum (rampa ve patika icin zorunlu: egim_ok yalniz yolda gevser)
    for ad, (hat, gen) in G.YOL_HAT.items():
        for i in range(len(hat) - 1):
            (ax, ay, _), (bx, by, _) = hat[i], hat[i + 1]
            n = max(1, int(math.hypot(bx - ax, by - ay) // 110))
            for k in range(n + 1):
                t = k / float(n)
                x, y = round(ax + (bx - ax) * t), round(ay + (by - ay) * t)
                if G.dere_mes(x, y) < G.DERE_DIS + 40:              # kopru ustu: asagida
                    continue
                if not G.icinde(x, y) and y < -3300:                # guney yolunun kopuk ucu
                    continue
                if serbest(x, y, 20):
                    ent('node_pathnode', origin=(x, y, zz(x, y)))
    # C patikasi: sik dugum (olculdu: z 97..191 arasi dugumsuzdu, C tepesi adaydi)
    hat = G.YOL_HAT['c_patika'][0]
    for i in range(len(hat) - 1):
        (ax, ay, _), (bx2, by2, _) = hat[i], hat[i + 1]
        n = max(1, int(math.hypot(bx2 - ax, by2 - ay) // 70))
        for k in range(n + 1):
            t = k / float(n)
            x, y = round(ax + (bx2 - ax) * t), round(ay + (by2 - ay) * t)
            if all(math.hypot(x - kx, y - ky) > kr + 18 for (kx, ky, kr) in G.KAYALAR):
                ent('node_pathnode', origin=(x, y, zz(x, y)))
    # kopru ustu dugumleri
    for yk, zk in zip(G.KOPRU_Y, G.KOPRU_Z):
        xr = G.dere_x(yk)
        for dx in range(-int(G.DERE_DIS) - 40, int(G.DERE_DIS) + 41, 100):
            ent('node_pathnode', origin=(round(xr + dx), round(yk), round(zk + 10, 1)))
    # YIKIK EV ICI: ekip burada dogar. Izgara (150) icini ancak tek noktayla
    # kapsiyordu ve o nokta baglantisiz kaldi (olculdu) -> dostlar DONUYORDU.
    # 64'luk ic izgara + guney acikligindan disari cikis zinciri.
    yx0, yy0, yx1, yy1 = G.YIKIK
    YIKIK_DUGUM = []
    for x in range(int(yx0) + 50, int(yx1) - 40, 48):
        for y in range(int(yy0) + 45, int(yy1) - 35, 48):
            if serbest(x, y, 14):
                ent('node_pathnode', origin=(x, y, zz(x, y)))   # yakininda dugum zaten varsa o kullanilir
                YIKIK_DUGUM.append((x, y))
    for k in range(4):
        cx_, cy_ = (yx0 + yx1) / 2.0 + 40, yy0 + 30 - k * 70
        if serbest(cx_, cy_, 18):
            ent('node_pathnode', origin=(round(cx_), round(cy_), zz(cx_, cy_)))

    # karakol ici: zemin ve ust kat
    for (kat, zt) in ((0, ZT + 8), (1, ZU + 8)):
        for x in range(X0 + 56, X1 - 55, 84):
            for y in range(Y0 + 56, Y1 - 55, 84):
                if serbest(x, y, 22, kat):
                    ent('node_pathnode', origin=(x, y, zt))
        for xw in (XW, XE):                          # ic kapi gecisleri
            ky = 230 if kat == 0 else 730
            for dx in (-40, 0, 40):
                ent('node_pathnode', origin=(xw + dx, ky, zt))
    # merdiven: alt, basamaklar, ust
    sx = (mx0 + mx1) // 2
    ent('node_pathnode', origin=(sx, my0 - 70, ZT + 8))
    for y in range(int(my0) + 10, int(my1), 60):           # rampa yuzeyinde
        ent('node_pathnode', origin=(sx, y, round(G.MERDIVEN_Z(y) + 16, 1)))
    ent('node_pathnode', origin=(sx, my1 + 48, ZU + 8))
    # dis kapilar (on, arka): ic ve dis dugum
    for (kx, ic_y, dis_y) in ((-150, Y0 + 48, Y0 - 210), (-60, Y1 - 48, Y1 + 80)):
        ent('node_pathnode', origin=(kx, ic_y, ZT + 8))
        ent('node_pathnode', origin=(kx, dis_y, zz(kx, dis_y)))
    ent('node_pathnode', origin=(-150, Y0 - 80, ZT + 8))              # sundurma ustu

    # =====================================================================
    # 3. DOST ZINCIRLERI -- GSC oyuncuya en yakin zinciri secer
    # =====================================================================
    ZINCIRLER = {}
    def zincir(ad, noktalar, kat=None):
        pts = []
        for (x, y) in noktalar:
            p = yer_bul(x, y, 28, kat, 220)
            if p and p not in pts:
                pts.append(p)
        for i, (x, y) in enumerate(pts):
            z = (ZT + 8) if kat == 0 else (ZU + 8) if kat == 1 else zz(x, y)
            kv = {'origin': (x, y, z), 'angles': (0, 90, 0), 'targetname': ad if i == 0 else '%s_%d' % (ad, i)}
            if i + 1 < len(pts):
                kv['target'] = '%s_%d' % (ad, i + 1)
            ent('node_pathnode', **kv)
        ZINCIRLER[ad] = pts
    W = G.W
    zincir('fc_baslangic', [W(640, 870), W(670, 870), W(700, 860), W(630, 840), W(690, 830)])
    zincir('fc_guney', [W(625, 760), W(660, 760), W(620, 720), W(670, 720), W(640, 700)])
    zincir('fc_kavsak', [W(600, 660), W(680, 660), W(610, 625), W(670, 625), W(560, 655)])
    zincir('fc_bati', [W(420, 600), W(460, 590), W(380, 545), W(360, 600), W(410, 640)])
    zincir('fc_brampa', [W(330, 440), W(310, 470), W(360, 450), W(340, 400), W(300, 430)])
    zincir('fc_b', [W(240, 290), W(270, 285), W(255, 310), W(225, 300), W(275, 305)])
    zincir('fc_dogu', [W(760, 650), W(790, 655), W(770, 615), W(740, 610), W(800, 600)])
    zincir('fc_dogu2', [W(960, 630), W(990, 610), W(950, 590), W(975, 570), W(1000, 640)])
    zincir('fc_cpatika', [W(1010, 520), W(990, 500), W(1020, 480), W(985, 470), W(1030, 540)])
    zincir('fc_c', [W(1085, 360), W(1110, 340), W(1080, 320), W(1100, 380), W(1070, 345)])
    zincir('fc_kuzey', [W(560, 330), W(600, 325), W(650, 328), W(700, 330), W(520, 330)])
    zincir('fc_kuzeydogu', [W(950, 380), W(970, 350), W(990, 380), W(940, 350), W(980, 330)])
    zincir('fc_avlu', [(-500, -220), (-250, -240), (0, -240), (250, -220), (-150, -280)])
    zincir('fc_zemin', [(-560, 300), (-250, 200), (-60, 300), (230, 300), (-100, 760)], kat=0)
    zincir('fc_ust', [(-560, 400), (-100, 420), (230, 420), (-560, 700), (230, 700)], kat=1)
    G.ZINCIRLER = ZINCIRLER

    # =====================================================================
    # 4. SOVYET EKIP + TAKVIYE
    # =====================================================================
    def sp(c, x, y, kat=None, aci=90, **kv):
        p = yer_bul(x, y, 28, kat, 220)
        if not p:
            raise SystemExit('SPAWNER YERI YOK: %s %s %s' % (c, x, y))
        z = (ZT + 4) if kat == 0 else (ZU + 4) if kat == 1 else zemin(*p) + 4
        kv = {k: v for k, v in kv.items() if v is not None}
        kv.setdefault('angles', (0, aci, 0))
        say[c] = say.get(c, 0) + 1
        return H.ent(c, origin=(p[0], p[1], round(z, 1)), **kv)
    bsx, bsy = G.BASLANGIC
    yx0, yy0, yx1, yy1 = G.YIKIK
    ycx, ycy = (yx0 + yx1) / 2.0, (yy0 + yy1) / 2.0
    YD = sorted(YIKIK_DUGUM, key=lambda q: math.hypot(q[0] - ycx, q[1] - ycy))
    def dugumde(c, q, **kv):
        say[c] = say.get(c, 0) + 1
        kv.setdefault('angles', (0, 270, 0))
        return H.ent(c, origin=(q[0], q[1], round(zemin(*q) + 4, 1)), **kv)
    assert len(YD) >= 7, 'yikik ev ici dugum az: %d' % len(YD)
    dugumde('actor_ally_rus_commissar_ppsh', YD[0], targetname='leonov', spawnflags=7, count=1,
            script_friendname='Lt. Leonov')
    EKIP = ['actor_ally_rus_reg_mosin', 'actor_ally_rus_reg_ppsh', 'actor_ally_rus_reg_svt40',
            'actor_ally_rus_reg_mosin', 'actor_ally_rus_reg_pps42', 'actor_ally_rus_reg_ppsh']
    for i, c in enumerate(EKIP):
        dugumde(c, YD[i + 1], targetname='ekip', spawnflags=1, count=1)
    # takviye: harita DISINDA guney yolu (orman arkasi, gorus disi) -- TEK nokta
    TAKVIYE_C = ['actor_ally_rus_reg_ppsh', 'actor_ally_rus_reg_mosin', 'actor_ally_rus_reg_svt40',
                 'actor_ally_rus_reg_pps42']
    # savunma takviyesi: karakolun KUZEYINDE ormanin icinde (oyuncu goremez)
    for i, c in enumerate(['actor_ally_rus_reg_ppsh', 'actor_ally_rus_reg_mosin', 'actor_ally_rus_reg_svt40',
                           'actor_ally_rus_reg_pps42']):
        # duz kuzey yolu (bina kuzeybatisi); dik tepede dugum yoktu, takviye kaliyordu
        sp(c, -1500 + i * 90, 1180, None, 0, targetname='takviye_kuzey', spawnflags=1, count=1)
    tx, ty = G.W(500, 997)           # guney yolu, tepe arkasi (uc kisim yol agindan kopuk, olculdu)
    for i, c in enumerate(TAKVIYE_C):
        sp(c, tx - 60 + (i % 2) * 120, ty - (i // 2) * 110, targetname='takviye', target='player', spawnflags=1)
    # harita disi yol koridoru dugumleri (takviye ve guneyden gelen Almanlar)
    for H_ in GIRIS_HAT:
      for i in range(len(H_) - 1):
        (ax, ay, _), (bx2, by2, _) = H_[i], H_[i + 1]
        L = math.hypot(bx2 - ax, by2 - ay) or 1
        qx, qy = -(by2 - ay) / L, (bx2 - ax) / L
        n = max(1, int(L // 110))
        for k in range(n + 1):
            t = k / float(n)
            x, y = ax + (bx2 - ax) * t, ay + (by2 - ay) * t
            if G.icinde(x, y):
                continue
            if y < -3300:                   # guney yolunun kopuk ucu (olculdu): dugum yok
                continue
            for w in (-55, 55):
                px_, py_ = round(x + qx * w), round(y + qy * w)
                if serbest(px_, py_, 20):
                    ent('node_pathnode', origin=(px_, py_, zz(px_, py_)))
    px0 = min(p[0] for p in G.POLI); px1 = max(p[0] for p in G.POLI)
    py0 = min(p[1] for p in G.POLI); py1 = max(p[1] for p in G.POLI)
    tetik('trigger_multiple', px0, py0, -600, px1, py1, 1500, targetname='friendly_wave', target='takviye')

    # =====================================================================
    # 5. ALMANLAR  (KESIN: B 10, C 10, A 15)
    # =====================================================================
    TUFEK = ['actor_axis_snow_wehr_reg_kar98k', 'actor_axis_snow_wehr_reg_mp40', 'actor_axis_snow_wehr_reg_kar98k',
             'actor_axis_snow_wehr_reg_G43', 'actor_axis_snow_wehr_reg_mp40']
    def grup(ad, aig, noktalar, kat_f, adet, subay=True):
        n = 0
        for i, (x, y, z, yaw) in enumerate(noktalar):
            if n >= adet:
                break
            c = 'actor_axis_snow_wehr_officer_mp40' if (subay and i == 0) else TUFEK[i % len(TUFEK)]
            kat = kat_f(x, y, z)
            sp(c, x, y, kat, yaw, targetname=ad, script_aigroup=aig, spawnflags=1, count=1)
            n += 1
        if n != adet:
            raise SystemExit('%s: %d/%d asker yerlesti' % (ad, n, adet))
    dis = lambda x, y, z: None
    # B: 2 havan ekibi (havanin iki yaninda) + 8 siper
    B_N = [(MBx + 40, MBy - 40, 0, 300), (MBx - 40, MBy - 60, 0, 300)] + SIPER['b']
    grup('alman_b', 'mevzi_b', B_N, dis, 10)
    C_N = [(MCx + 40, MCy - 40, 0, 200), (MCx + 40, MCy + 30, 0, 200)] + SIPER['c']
    grup('alman_c', 'mevzi_c', C_N, dis, 10)
    print('siper:', {k: len(v) for k, v in SIPER.items()})
    # dogu ust oda kapisi savunmaya kadar KILITLI -> oraya Alman konmaz (A kilitlenmesin)
    ust_uygun = [q for q in SIPER['a_ust'] if XW + 20 < q[0] < XE - 20]   # iki yan oda da kapali
    ust5 = ust_uygun[:5]
    A_N = SIPER['a_dis'][:5] + SIPER['a_zemin'][:5] + ust5 + SIPER['a_dis'][5:5 + 5 - len(ust5)]
    katf = lambda x, y, z: 1 if z > ZU else 0 if z > ZT and X0 < x < X1 and Y0 < y < Y1 else None
    grup('alman_a', 'karakol', A_N, katf, 15)

    def yol_noktasi(hat, mesafe):
        kalan = mesafe
        for i in range(len(hat) - 1):
            (ax, ay, _), (bx, by, _) = hat[i], hat[i + 1]
            L = math.hypot(bx - ax, by - ay)
            if kalan <= L:
                t = kalan / L
                return (round(ax + (bx - ax) * t), round(ay + (by - ay) * t))
            kalan -= L
        return (round(hat[-1][0]), round(hat[-1][1]))
    # KARSI SALDIRI (kullanici: binanin sagi, solu ve onunden, UZAKTAN; toplam 50)
    # her yonde 3 spawner, GSC her partide count=1 ile yeniden kullanir.
    # dogus noktalari harita DISINDA, vadilerin icinde, YOL EKSENI UZERINDE
    # (kullanici: "duvar icinde Alman dogdu" -> yamaca/agaca degil yolun ortasina)
    for yon, hat_ad, bas in (('bati', 'bati_giris', 120), ('dogu', 'dogu_giris', 120), ('guney', 'guney', 900)):
        hat = G.YOL_HAT[hat_ad][0]
        for i in range(5):
            ox, oy = yol_noktasi(hat, bas + i * 75)
            H.ent(TUFEK[(i + len(yon)) % len(TUFEK)], origin=(ox, oy, round(zemin(ox, oy) + 4, 1)),
                  angles=(0, 90, 0),
                  targetname='karsi_' + yon, spawnflags=1, count=1)

    # =====================================================================
    # 5b. KARSI SALDIRI ARACLARI (kullanici): kamyon (guney), yarim paletli 1
    # (bati), yarim paletli 2 (dogu, guney kopruden). Yarim paletli: 1 MG
    # nisancisi (yer 1) + 5 yolcu. MG yayi +-30 (stok _halftrack): arac durdugu
    # yerde burnu karakola donuk olacak sekilde son parca yonlendirildi.
    # Anahtarlar krasnoye'de oyunda calisanlar (script_vehicle, info_vehicle_node).
    # =====================================================================
    def arac_z(x, y):
        if G.dere_mes(x, y) < G.DERE_DIS + 60:
            yk = min(G.KOPRU_Y, key=lambda v: abs(v - y))
            return G.KOPRU_Z[G.KOPRU_Y.index(yk)] + 16
        return round(zemin(x, y) + 16, 1)
    def arac(ad, tip, model, grup, nokta, hiz, binen, yerler, cesit, takim='axis'):
        ince = []
        for i in range(len(nokta) - 1):
            (ax, ay), (bx, by) = nokta[i], nokta[i + 1]
            n = max(1, int(math.hypot(bx - ax, by - ay) // 240))
            for k in range(n):
                t = k / float(n)
                ince.append((ax + (bx - ax) * t, ay + (by - ay) * t))
        ince.append(nokta[-1])
        for i, (x, y) in enumerate(ince):
            kv = {'origin': (round(x, 1), round(y, 1), arac_z(x, y)),
                  'targetname': ad + '_yol' if i == 0 else '%s_yol_%d' % (ad, i)}
            if i + 1 < len(ince):
                kv['target'] = '%s_yol_%d' % (ad, i + 1)
            if i == 0:
                kv.update(spawnflags=1, speed=hiz, lookahead=1)
            if i == len(ince) - 3:
                kv['speed'] = max(5, hiz // 2)
            H.ent('info_vehicle_node', **kv)
        (x0, y0), (x1, y1) = ince[0], ince[1]
        yaw = round(math.degrees(math.atan2(y1 - y0, x1 - x0)), 1)
        H.ent('script_vehicle', targetname=ad, target=ad + '_yol', vehicletype=tip, model=model,
              script_vehiclespawngroup=grup, script_team=takim, script_vehicleride=binen,
              origin=(round(x0, 1), round(y0, 1), arac_z(x0, y0) - 14), angles=(0, yaw, 0))
        # yolcular: arac yaninda (harita disi), aracin icine isinlanir
        # yolcular aracin YOLU boyunca, govdeden uzakta (olculdu: duz ileri
        # yerlestirince virajda yamaca giriyordu; cok yakinda govdeye denk geliyordu)
        def yol_boyu(m):
            kalan = m
            for i in range(len(ince) - 1):
                (ax, ay), (bx, by) = ince[i], ince[i + 1]
                L = math.hypot(bx - ax, by - ay)
                if kalan <= L:
                    return (ax + (bx - ax) * kalan / L, ay + (by - ay) * kalan / L)
                kalan -= L
            return ince[-1]
        L0 = math.hypot(x1 - x0, y1 - y0) or 1
        ux, uy = (x1 - x0) / L0, (y1 - y0) / L0
        for k, yer in enumerate(yerler):
            c = cesit[k % len(cesit)]
            yan = 110 if k % 2 == 0 else -110          # iki yanda (170: vadide yamaca gomuluyordu)
            geri = 20 + (k // 2) * 60                  # govde boyunca, yolun duz kisminda
            ox, oy = x0 + ux * geri - uy * yan, y0 + uy * geri + ux * yan
            say[c] = say.get(c, 0) + 1
            H.ent(c, origin=(round(ox, 1), round(oy, 1), round(zemin(ox, oy) + 4, 1)), angles=(0, yaw, 0),
                  targetname=ad + '_asker', script_vehicleride=binen, script_startingposition=yer,
                  spawnflags=1, count=1)
    GH = G.YOL_HAT['guney'][0]; BH = G.YOL_HAT['bati_giris'][0]
    DH = G.YOL_HAT['dogu_giris'][0]; GD = G.YOL_HAT['gdogu'][0]
    xy = lambda L: [(p[0], p[1]) for p in L]
    arac('kamyon', 'blitz', 'xmodel/vehicle_opel_blitz_snow', 1,
         xy(GH[:10]) + [W(628, 728), W(608, 706)], 60, 1, range(9), TUFEK)
    arac('yaripalet1', 'germanhalftrack', 'xmodel/vehicle_halftrack_mg_snow', 2,
         xy(BH[:10]) + [W(430, 595)], 16, 2, range(0, 6), TUFEK)
    arac('yaripalet2', 'germanhalftrack', 'xmodel/vehicle_halftrack_mg_snow', 3,
         xy(DH) + xy([GD[6], GD[5], GD[4], GD[3]]) + [W(798, 640), W(773, 627)], 16, 3, range(0, 6), TUFEK)

    # Final (kullanici): baslangic bolgesinden 2 SOVYET kamyonu, Alman kamyonunun
    # yari hizinda; biri karakolun dogusundaki, digeri batisindaki yolda durur.
    SOV = ['actor_ally_rus_reg_ppsh', 'actor_ally_rus_reg_mosin', 'actor_ally_rus_reg_svt40',
           'actor_ally_rus_reg_pps42']
    bas = xy(GH[:10]) + [W(645, 690), W(640, 655)]
    arac('sovyet_dogu', 'blitz', 'xmodel/vehicle_opel_blitz_snow', 4,
         bas + [W(690, 646), W(728, 640)], 20, 4, range(9), SOV, takim='allies')
    arac('sovyet_bati', 'blitz', 'xmodel/vehicle_opel_blitz_snow', 5,
         bas + [W(560, 640), W(505, 628)], 20, 5, range(9), SOV, takim='allies')

    # sol (bati) ust oda: kapiyi kirip saldiracak Alman (kapinin hemen arkasinda)
    for (dx, dy, c) in ((-160, 700, 'actor_axis_snow_wehr_reg_mp40'), (-210, 745, 'actor_axis_snow_wehr_reg_kar98k')):   # dosya dolabindan uzak (olculdu)
        H.ent(c, origin=(XW + dx, dy, ZU + 4), angles=(0, 0, 0), targetname='kapi_alman', spawnflags=1, count=1)
        say[c] = say.get(c, 0) + 1

    # =====================================================================
    # 6. HAVAN ISABET NOKTALARI (maps\_mortar::generic_style) + namlu
    # =====================================================================
    def isabet(ad, noktalar):
        for (x, y) in noktalar:
            p = yer_bul(x, y, 40, None, 160)
            if p:
                ent('script_origin', targetname=ad, origin=(p[0], p[1], round(zemin(*p), 1)))
    isabet('havan_b', [W(650, 820), W(610, 760), W(680, 720), W(600, 690), W(520, 660), W(470, 640),
                       W(430, 590), W(390, 640), W(560, 600), W(700, 680)])
    isabet('havan_c', [W(690, 800), W(720, 760), W(700, 700), W(740, 670), W(780, 640), W(810, 600),
                       W(930, 650), W(970, 640), W(960, 560), W(660, 620)])
    ent('script_origin', targetname='havan_b_namlu', origin=(MBx, MBy, G.B_UST + 48))
    ent('script_origin', targetname='havan_c_namlu', origin=(MCx, MCy, G.C_UST + 48))
    # final cemberi merkezi (avlu, giris onu)
    ent('script_origin', targetname='daire_merkez', origin=(-150, -130, zz(-150, -130, 0)))

    G.SAY = say
    print('yerlesim:', ', '.join('%s %d' % kv for kv in sorted(say.items())))
