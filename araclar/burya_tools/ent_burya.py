# -*- coding: utf-8 -*-
"""
ent_burya.py -- yerlesim: yol dugumleri, siperler, zincir, konvoy/takviye
araclari ve yolculari, Alman gruplari, MG taretleri, betik noktalari.

KESIN SAYILAR (kullanici/senaryo):
  pusu 10 | kamp dis 9 + 2 MG | kamp ic 10 | merkez 5 | 2 dalga (6 + 8)
  konvoy: 3 kamyon (1: sofor, 2: sofor + Leonov + 6, 3: sofor)
  takviye: 2 kamyon x 7 (sofor + 6)
Her spawner/node bosluk denetiminden gecer ("in solid" 0 hedefi).
"""
import math

YARICAP = (('tree_destroyed_snow_fallen', 150), ('tree_destoyed', 70), ('tree_destroyed', 60),
           ('vehicle_', 190), ('caen_barbedwire', 170), ('tree_', 44), ('military_sandbag', 64),
           ('military_hedgehog', 60), ('military_dragonstooth', 50), ('light_flaksheinwerfer', 75),
           ('crate', 44), ('prop_crate', 50), ('prop_barrel', 26), ('prop_potbelly', 34), ('prop_flag', 20),
           ('furniture_bed_bunker', 110), ('furniture_duhoc_bunker_table', 90), ('furniture_file_cabinet_long', 75),
           ('furniture_bookshelves', 75), ('furniture_armoire', 65), ('furniture_rolltopdesk', 65),
           ('furniture_smallfoldingtable', 45), ('furniture_duhoc_chair', 28), ('furniture_utilitychair', 28),
           ('military_german_radio', 0))

def yerlestir(G):
    H, yuk = G.H, G.yukseklik
    say = {}
    W = G.W
    BX0, BY0, BX1, BY1 = G.BX0, G.BY0, G.BX1, G.BY1
    BZ, BZU = G.BZ, G.BZU
    mx0, my0, mx1, my1 = G.MERD
    IX = G.IX
    ZK = G.ZK
    kx0, ky0, kx1, ky1 = G.KAMP

    DUGUM = []
    def ent(sinif, **kv):
        if sinif.startswith('node_'):
            x, y, z = kv['origin']
            if any(abs(x - a) < 24 and abs(y - b) < 24 and abs(z - c) < 60 for (a, b, c) in DUGUM):
                if 'targetname' not in kv:
                    return None
            DUGUM.append(kv['origin'])
        say[sinif] = say.get(sinif, 0) + 1
        return H.ent(sinif, **kv)

    def tetik(sinif, x0, y0, z0, x1, y1, z1, **kv):
        bl = []
        H.kutu(x0, y0, z0, x1, y1, z1, 'trigger', 'trigger', alt='trigger', hedef=bl)
        say[sinif] = say.get(sinif, 0) + 1
        return H.ent(sinif, brushlar=bl, **kv)

    def zemin(x, y):
        """mesh hucresinin gercek ucgen yuzeyi (iki ucgenlemenin buyugu)."""
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
        for (xa, ya, xb, yb) in G.DUVARLAR:
            d = G._seg(x, y, (xa, ya), (xb, yb))
            for (kx, ky, g) in G.DUVAR_KAPI:
                if math.hypot(x - kx, y - ky) < g:
                    d = 1e9
            en = min(en, d)
        return en

    GIRIS_HAT = [G.YOL_HAT[k][0] for k in ('konvoy', 'takviye')]
    def dis_koridor(x, y):
        for H_ in GIRIS_HAT:
            for i in range(len(H_) - 1):
                (ax, ay, _), (bx, by, _) = H_[i], H_[i + 1]
                if G._seg(x, y, (ax, ay), (bx, by)) < 180:
                    return True
        return False

    # -------- bina ici serbestlik (merkez bina 2 kat, baraka_a, depo_a)
    IC = {'merkez0': (BX0, BY0, BX1, BY1, BZ)}
    for ad in ('baraka_a', 'depo_a'):
        v = G.YAPILAR[ad]
        IC[ad] = (v[0], v[1], v[2], v[3], ZK + 16)

    def ic_serbest(x, y, r, oda):
        x0, y0, x1, y1, _ = IC[oda]
        if not (x0 + 16 + r <= x <= x1 - 16 - r and y0 + 16 + r <= y <= y1 - 16 - r):
            return False
        if oda.startswith('merkez'):
            if abs(x - IX) < 40:                  # ic kapi: yalniz acik dugumler (52'lik kapida izgara 'in solid')
                return False
            if mx0 - r - 8 <= x <= mx1 + r + 8 and my0 - r - 8 <= y <= my1 + r + 8:
                return False
        for (m, mx, my) in G.MODELLER:
            rr = yaricap(m)
            if rr and math.hypot(x - mx, y - my) < rr + r:
                return False
        return True

    def serbest(x, y, r=26, oda=None):
        if oda is not None:
            return ic_serbest(x, y, r, oda)
        if not G.icinde(x, y) and not dis_koridor(x, y):
            return False
        if G.dere_mes(x, y) < G.DERE_DIS + 40 + r:
            return False
        for ad, v in G.YAPILAR.items():
            if v[0] - r - 12 <= x <= v[2] + r + 12 and v[1] - r - 12 <= y <= v[3] + r + 12:
                return False
        if duvar_mes(x, y) < r + 20:
            return False
        for (m, mx, my) in G.MODELLER:
            rr = yaricap(m)
            if rr and abs(x - mx) < rr + r and abs(y - my) < rr + r and math.hypot(x - mx, y - my) < rr + r:
                return False
        for (kx, ky, kr) in G.KAYALAR:
            if math.hypot(x - kx, y - ky) < kr + r + 10:
                return False
        return True

    def yer_bul(x, y, r=26, oda=None, en=200):
        if serbest(x, y, r, oda):
            return (x, y)
        for rad in range(16, en + 1, 16):
            n = max(8, int(rad / 8))
            for k in range(n):
                a = 2 * math.pi * k / n
                px, py = round(x + rad * math.cos(a)), round(y + rad * math.sin(a))
                if serbest(px, py, r, oda):
                    return (px, py)
        return None

    def egim_ok(x, y, adim=80):
        z = yuk(x, y)
        return all(abs(yuk(x + dx, y + dy) - z) < 62 for (dx, dy) in ((adim, 0), (-adim, 0), (0, adim), (0, -adim)))

    def oda_z(oda):
        return IC[oda][4]

    # =====================================================================
    # 1. SIPERLER
    # =====================================================================
    SIPER = {'pusu': [], 'yol': [], 'kapi_dis': [], 'kamp_ic': [], 'merkez': [], 'guvenli': []}
    def siper(grup, tur, x, y, yaw, oda=None, r=24):
        if oda is None and not G.icinde(x, y):
            return None
        p = yer_bul(x, y, r, oda, 96)
        if not p or (oda is None and not egim_ok(*p, adim=60)):
            return None
        z = (oda_z(oda) + 8) if oda else zz(*p)
        e = ent(tur, origin=(p[0], p[1], z), angles=(0, yaw, 0))
        if e is not None and grup:
            SIPER[grup].append((p[0], p[1], z, yaw))
        return p
    PX, PY = G.PATLAMA
    # pusu alani: kayalarin yanlari (iki taraf da kullanir)
    for (kx, ky, kr) in G.KAYALAR:
        if math.hypot(kx - PX, ky - PY) < 1100:
            for a in range(0, 360, 90):
                t = math.radians(a)
                yaw = round(math.degrees(math.atan2(PY - ky, PX - kx))) % 360
                siper('pusu', 'node_cover_crouch', kx + math.cos(t) * (kr + 36), ky + math.sin(t) * (kr + 36), yaw)
    # yol kenari siperleri (ekip yaklasirken)
    for ad in ('konvoy',):
        hat = G.YOL_HAT[ad][0]
        for i in range(len(hat) - 1):
            (ax, ay, _), (bx2, by2, _) = hat[i], hat[i + 1]
            mx_, my_ = (ax + bx2) / 2.0, (ay + by2) / 2.0
            L = math.hypot(bx2 - ax, by2 - ay) or 1
            qx, qy = -(by2 - ay) / L, (bx2 - ax) / L
            for s in (-1, 1):
                siper('yol', 'node_cover_crouch', mx_ + qx * s * 170, my_ + qy * s * 170,
                      round(math.degrees(math.atan2(by2 - ay, bx2 - ax))) % 360)
    # kamp girisi disi: kum torbalari, kirpiler (guneye bakar)
    KX = G.KAPI_X
    for (dx, dy) in ((-200, -150), (200, -150), (-340, -90), (340, -90), (-420, -200), (420, -200),
                     (-300, -460), (330, -460), (-560, -320), (560, -300), (0, -380), (-120, 160), (120, 160)):
        siper('kapi_dis', 'node_cover_crouch', KX + dx, ky0 + dy, 270 if dy < 0 else 270)
    # kamp ici: binalar arasi, kum torbalari, araclar
    for (x, y, yaw) in ((2450, 1700, 270), (2650, 1800, 270), (2900, 1820, 270), (3100, 1820, 270),
                        (3350, 1800, 270), (3600, 1950, 180), (2450, 2300, 180), (3600, 2300, 0),
                        (2100, 2350, 270), (3650, 2650, 180), (2850, 2700, 270), (2000, 1750, 270),
                        (3900, 2280, 180), (2300, 2700, 270), (3000, 2700, 270), (3000, 2850, 270)):
        siper('kamp_ic', 'node_cover_stand', x, y, yaw)
    # merkez bina: pencere arkalari (iki kat)
    for kat, oda in ((0, 'merkez0'),):
        for (x, y, yaw) in ((2650, 2025, 270), (2800, 2025, 270), (3200, 2025, 270), (3350, 2025, 270),
                            (3000, 2025, 270), (2650, 2575, 90), (3100, 2575, 90), (3350, 2575, 90),
                            (2545, 2150, 180), (2545, 2450, 180), (3455, 2120, 0), (3455, 2480, 0)):
            siper('merkez', 'node_cover_crouch_window' if kat else 'node_cover_crouch', x, y, yaw, oda)
    # guvenli alan cevresi
    gx, gy = G.GUVENLI
    for (dx, dy) in ((-200, 0), (200, 0), (0, -200), (-150, -150), (150, -150), (0, 200)):
        siper('guvenli', 'node_cover_crouch', gx + dx, gy + dy, 45)

    # =====================================================================
    # 2. YOL DUGUMLERI
    # =====================================================================
    ADIM = 150
    gx0 = -4768 - ADIM * ((-4768 - (G.SX0 + 96)) // ADIM)
    gy0 = -4000 - ADIM * ((-4000 - (G.SY0 + 96)) // ADIM)
    for x in range(gx0, G.SX1 - 95, ADIM):
        for y in range(gy0, G.SY1 - 95, ADIM):
            if not serbest(x, y) or not egim_ok(x, y):
                continue
            ent('node_pathnode', origin=(x, y, zz(x, y)))
    for ad, (hat, gen) in G.YOL_HAT.items():
        if ad == 'orman':
            continue
        for i in range(len(hat) - 1):
            (ax, ay, _), (bx, by, _) = hat[i], hat[i + 1]
            n = max(1, int(math.hypot(bx - ax, by - ay) // 110))
            for k in range(n + 1):
                t = k / float(n)
                x, y = round(ax + (bx - ax) * t), round(ay + (by - ay) * t)
                if G.dere_mes(x, y) < G.DERE_DIS + 40:
                    continue
                for w in ((0,) if G.icinde(x, y) else (-55, 55)):
                    L = math.hypot(bx - ax, by - ay) or 1
                    qx, qy = -(by - ay) / L, (bx - ax) / L
                    px_, py_ = round(x + qx * w), round(y + qy * w)
                    if serbest(px_, py_, 20):
                        ent('node_pathnode', origin=(px_, py_, zz(px_, py_)))
    for x in range(kx0 + 40, kx1 - 39, 75):
        for y in range(ky0 + 40, ky1 - 39, 75):
            if serbest(x, y, 24):
                ent('node_pathnode', origin=(x, y, zz(x, y)))
    # kopru ustu
    for yk, zk in zip(G.KOPRU_Y, G.KOPRU_Z):
        xr = G.dere_x(yk)
        for dx in range(-int(G.DERE_DIS) - 60, int(G.DERE_DIS) + 61, 90):
            ent('node_pathnode', origin=(round(xr + dx), round(yk), round(zk + 10, 1)))
    # bina icleri
    for oda, (x0, y0, x1, y1, zt) in IC.items():
        for x in range(int(x0) + 56, int(x1) - 55, 84):
            for y in range(int(y0) + 56, int(y1) - 55, 84):
                if serbest(x, y, 22, oda):
                    ent('node_pathnode', origin=(x, y, zt + 8))
    # merkez bina: ic kapi, dis kapilar, merdiven
    for kat_z in (BZ,):
        for dx in (-40, 0, 40):
            ent('node_pathnode', origin=(IX + dx, 2300, kat_z + 8))
    for (x, y_ic, y_dis) in ((3000, BY0 + 50, BY0 - 110), (2800, BY1 - 50, BY1 + 110)):
        ent('node_pathnode', origin=(x, y_ic, BZ + 8))
        ent('node_pathnode', origin=(x, y_dis, zz(x, y_dis)))
    ent('node_pathnode', origin=(BX1 - 50, 2300, BZ + 8))
    ent('node_pathnode', origin=(BX1 + 110, 2300, zz(BX1 + 110, 2300)))
    sx = (mx0 + mx1) // 2
    ent('node_pathnode', origin=(sx + 10, my0 - 50, BZ + 8))
    for y in range(int(my0) + 10, int(my1), 50):
        if G.MERD_Z(y) < BZU - 90:              # ust kisim brushmodel kutusunda
            ent('node_pathnode', origin=(sx, y, round(G.MERD_Z(y) + 16, 1)))
    # baraka_a / depo_a kapilari (ic + dis dugum)
    for (x, y, dx, dy, oda, dis) in ((2380, 2210, 1, 0, 'baraka_a', 50), (2100, 2350, 0, 1, 'baraka_a', 100),
                                     (3375, 2770, 0, -1, 'depo_a', 90)):
        zt = oda_z(oda) + 8
        ent('node_pathnode', origin=(x - dx * 50, y - dy * 50, zt))
        if dis <= 72:
            zd = oda_z(oda) - 18 * dis / 72.0 + 8
        else:
            zd = zz(x + dx * dis, y + dy * dis)
        ent('node_pathnode', origin=(x + dx * dis, y + dy * dis, round(zd, 1)))
    # kuleler: platform + el merdiveni (stok tankhunt kalibi: begin altta merdivene
    # donuk 'ladder_up' -> end platformda; inis icin ust begin 'ladder_down')
    for (cx, cy, zp, yon, xo) in G.KULE:
        for dy in (-28, 32):                      # olculdu: merdiven dugumleriyle cakisma (overlap) AI'yi durduruyordu
            ent('node_pathnode', origin=(cx - yon * 40, cy + dy, zp + 8))
        yuz = 180 if yon > 0 else 0              # merdivene bakis
        alt_x = xo + yon * 34
        ust_x = cx + yon * 22
        n = len(say)
        H.ent('node_negotiation_begin', origin=(round(alt_x), cy, zz(alt_x, cy)), angles=(0, yuz, 0),
              animscript='ladder_up', targetname='kule_cik_%d' % cx, target='kule_ust_%d' % cx)
        H.ent('node_negotiation_end', origin=(round(ust_x), cy, zp + 8), angles=(0, yuz, 0), targetname='kule_ust_%d' % cx)
        H.ent('node_negotiation_begin', origin=(round(ust_x + yon * 46), cy, zp + 8), angles=(0, yuz, 0),
              animscript='ladder_down', targetname='kule_in_%d' % cx, target='kule_alt_%d' % cx)
        H.ent('node_negotiation_end', origin=(round(alt_x + yon * 50), cy, zz(alt_x + yon * 50, cy)), angles=(0, (yuz + 180) % 360, 0),
              targetname='kule_alt_%d' % cx)
        say['merdiven'] = say.get('merdiven', 0) + 1
        bx_ = alt_x + yon * 110
        ent('node_pathnode', origin=(round(bx_), cy, zz(bx_, cy)))
        ent('script_origin', targetname='kule_dip', script_noteworthy=str(cx), origin=(round(alt_x), cy, zz(alt_x, cy, 0)))
        ent('script_origin', targetname='kule_ust', script_noteworthy=str(cx), origin=(cx, cy - 10, zp + 4))

    # =====================================================================
    # 3. ZINCIR (oyuncu her zaman bir zincirde olmali -- olculen kural)
    # =====================================================================
    def zincir(ad, noktalar):
        pts = []
        for (x, y) in noktalar:
            p = yer_bul(x, y, 28, None, 260)
            if p and p not in pts:
                pts.append(p)
        for i, (x, y) in enumerate(pts):
            kv = {'origin': (x, y, zz(x, y)), 'angles': (0, 90, 0), 'targetname': ad if i == 0 else '%s_%d' % (ad, i)}
            if i + 1 < len(pts):
                kv['target'] = '%s_%d' % (ad, i + 1)
            ent('node_pathnode', **kv)
        return pts
    ilk = zincir('fc_baslangic', [W(120, 760), W(150, 740), W(180, 770), W(130, 800)])
    assert len(ilk) >= 2, 'baslangic zinciri'

    # =====================================================================
    # 4. ARACLAR -- konvoy (3) ve takviye (2)
    # =====================================================================
    def arac_z(x, y):
        if G.dere_mes(x, y) < G.DERE_DIS + 60:
            return G.KOPRU_Z[0] + 16
        return round(zemin(x, y) + 16, 1)
    def arac(ad, grup, nokta, hiz, binen, yerler, takim='allies', yavas=False):
        for i, (x, y) in enumerate(nokta):
            kv = {'origin': (round(x, 1), round(y, 1), arac_z(x, y)),
                  'targetname': ad + '_yol' if i == 0 else '%s_yol_%d' % (ad, i)}
            if i + 1 < len(nokta):
                kv['target'] = '%s_yol_%d' % (ad, i + 1)
            if i == 0:
                kv.update(spawnflags=1, speed=hiz, lookahead=1)
            if yavas and i == len(nokta) - 3:
                kv['speed'] = max(5, hiz // 2)
            H.ent('info_vehicle_node', **kv)
        (x0, y0), (x1, y1) = nokta[0], nokta[1]
        yaw = round(math.degrees(math.atan2(y1 - y0, x1 - x0)), 1)
        H.ent('script_vehicle', targetname=ad, target=ad + '_yol', vehicletype='blitz',
              model='xmodel/vehicle_opel_blitz_snow', script_vehiclespawngroup=grup, script_team=takim,
              script_vehicleride=binen, origin=(round(x0, 1), round(y0, 1), arac_z(x0, y0) - 14), angles=(0, yaw, 0))
        L0 = math.hypot(x1 - x0, y1 - y0) or 1
        ux, uy = (x1 - x0) / L0, (y1 - y0) / L0
        for k, (yer, c, ekstra) in enumerate(yerler):
            yan = 65 if k % 2 == 0 else -65
            geri = 20 + (k // 2) * 60
            ox, oy = x0 + ux * geri - uy * yan, y0 + uy * geri + ux * yan
            q = yer_bul(round(ox), round(oy), 26, None, 160)
            if q:
                ox, oy = q
            say[c] = say.get(c, 0) + 1
            kv = dict(origin=(round(ox, 1), round(oy, 1), round(zemin(ox, oy) + 4, 1)), angles=(0, yaw, 0),
                      targetname=ad + '_asker', script_vehicleride=binen, script_startingposition=yer,
                      spawnflags=1, count=1)
            kv.update(ekstra)
            H.ent(c, **kv)
    SOV = ['actor_ally_rus_reg_ppsh', 'actor_ally_rus_reg_mosin', 'actor_ally_rus_reg_svt40',
           'actor_ally_rus_reg_pps42', 'actor_ally_rus_reg_ppsh', 'actor_ally_rus_reg_mosin']
    KH = G.YOL_HAT['konvoy'][0]
    dB = G.KOPRU_M                          # kopru ortasinin yol mesafesi
    ARA = G.KONVOY_ARA
    YOLCULUK = min(6600, dB - 80)           # en fazla 15 mph x 25 sn
    HIZ = max(8, int(round(YOLCULUK / 25.0 / 17.6))) - 5   # mph; kullanici testi: 5 mph yavas
    durus = {'konvoy3': dB, 'konvoy2': dB + ARA + 260, 'konvoy1': dB + 2 * ARA + 260}   # kullanici: bizim arac patlayan kamyondan uzak
    for k, ad in enumerate(('konvoy1', 'konvoy2', 'konvoy3')):
        m1 = durus[ad]
        nokta = G.hat_kes(KH, m1 - YOLCULUK, m1)
        if ad == 'konvoy1':
            # saga kirip yol kenarinda burnu saga donuk durur
            (ax, ay), (bx, by) = G.hat_nokta(KH, m1 - 60), G.hat_nokta(KH, m1)
            L = math.hypot(bx - ax, by - ay) or 1
            ux, uy = (bx - ax) / L, (by - ay) / L
            rx, ry = uy, -ux                 # sag
            nokta = nokta[:-1] + [(bx + ux * 60 + rx * 70, by + uy * 60 + ry * 70),
                                  (bx + ux * 110 + rx * 170, by + uy * 110 + ry * 170)]
            yerler = [(0, 'actor_ally_rus_reg_ppsh', {}), (1, SOV[1], {}), (2, SOV[2], {})]
        elif ad == 'konvoy2':
            yerler = [(0, 'actor_ally_rus_reg_ppsh', {}),
                      (1, 'actor_ally_rus_commissar_ppsh', {'script_noteworthy': 'leonov', 'script_friendname': 'Lt. Leonov'})]
            yerler += [(2 + i, SOV[i], {}) for i in range(4)]
        else:
            yerler = [(0, 'actor_ally_rus_reg_ppsh', {})] + [(1 + i, SOV[i + 2], {}) for i in range(3)]
        arac(ad, k + 1, nokta, HIZ, k + 1, yerler)
    G.KONVOY_DURUS = [G.hat_nokta(KH, durus[a]) for a in ('konvoy1', 'konvoy2', 'konvoy3')]
    print('konvoy: kopru mesafesi %d, yolculuk %d, hiz %d mph' % (dB, YOLCULUK, HIZ))
    TH = G.YOL_HAT['takviye'][0]
    LT = G.hat_uzunluk(TH)
    nokta = G.hat_kes(TH, 0, LT - 340)                               # kullanici: 2. durak
    yerler = [(i, SOV[i % len(SOV)], {}) for i in range(9)]           # Opel Blitz'in 9 yeri (stok _truck)
    arac('takviye1', 4, nokta, 20, 4, yerler, yavas=True)

    # =====================================================================
    # 5. ALMANLAR
    # =====================================================================
    TUFEK = ['actor_axis_snow_wehr_reg_kar98k', 'actor_axis_snow_wehr_reg_mp40', 'actor_axis_snow_wehr_reg_kar98k',
             'actor_axis_snow_wehr_reg_g43', 'actor_axis_snow_wehr_reg_mp40']
    def sp(c, x, y, oda=None, aci=90, **kv):
        p = yer_bul(x, y, 28, oda, 220)
        if p and oda is None and not egim_ok(*p, adim=40):        # yamaca gomulmesin ('in solid' olculdu)
            for (dx, dy) in ((60, 0), (-60, 0), (0, 60), (0, -60), (120, 0), (-120, 0), (0, 120), (0, -120)):
                q = yer_bul(p[0] + dx, p[1] + dy, 28, oda, 60)
                if q and egim_ok(*q, adim=40):
                    p = q
                    break
        if not p:
            raise SystemExit('SPAWNER YERI YOK: %s %s %s' % (c, x, y))
        z = (oda_z(oda) + 4) if oda else zemin(*p) + 4
        kv = {k: v for k, v in kv.items() if v is not None}
        kv.setdefault('angles', (0, aci, 0))
        say[c] = say.get(c, 0) + 1
        return H.ent(c, origin=(p[0], p[1], round(z, 1)), **kv)
    def grup(ad, aig, noktalar, adet, subay=True):
        n = 0
        for i, q in enumerate(noktalar):
            if n >= adet:
                break
            x, y = q[0], q[1]
            oda = q[4] if len(q) > 4 else None
            c = 'actor_axis_snow_wehr_officer_mp40' if (subay and i == 0) else TUFEK[i % len(TUFEK)]
            sp(c, x, y, oda, 270, targetname=ad, script_aigroup=aig, spawnflags=1, count=1)
            n += 1
        if n != adet:
            raise SystemExit('%s: %d/%d asker yerlesti' % (ad, n, adet))
    # PUSU (10): patlamanin kuzey/kuzeydogusu, kayalarin ve ormanin arkasi
    PUSU_N = [(PX + dx, PY + dy, 0, 0) for (dx, dy) in
              ((500, 1000), (800, 850), (1050, 600), (1150, 300), (-150, 1100), (250, 1150),
               (950, -350), (1100, -100), (-450, 1000), (650, 1200))]
    grup('pusu', 'pusu', PUSU_N, 10)
    # KAMP DIS (9): kapi onu siperleri ve kapi ici
    KD_N = [(x, y, 0, 270) for (x, y) in ((2200, 1800), (2300, 1860), (2400, 1800), (2250, 1960), (2350, 1960),
                                           (2150, 1900), (2450, 1900), (2300, 1760), (2200, 2010), (2500, 1760))]
    grup('kamp_dis', 'kamp_dis', KD_N, 10)
    # KAMP IC (10)
    KI_N = list(SIPER['kamp_ic'][:9])
    KI_N += [(x, y, 0, 0, 'baraka_a') for (x, y) in ((1950, 2190), (2100, 2270), (2280, 2140))]
    KI_N += [(x, y, 0, 0, 'depo_a') for (x, y) in ((3300, 2850), (3430, 2840), (3240, 2830))]
    grup('kamp_ic', 'kamp_ic', KI_N, 15)
    # MERKEZ (5): merkez binanin pencere arkalari
    M_N = [(q[0], q[1], q[2], q[3], 'merkez0') for q in SIPER['merkez']]
    grup('kamp_merkez', 'kamp_merkez', M_N[:7], 7)
    # YEDEK (takviye gelene kadar her olen Alman 2-5 sn sonra yerine): kampin
    # kuzeyi, binalarin arkasi (kapidan gorulmez; GSC ayrica gorus denetler)
    for i, (x, y) in enumerate(((2700, 2700), (3000, 2700), (3300, 2680), (2050, 2450), (2250, 2470),
                                (4130, 2250), (4130, 1900), (3700, 2900))):
        sp(TUFEK[i % len(TUFEK)], x, y, None, 270, targetname='kamp_yedek', spawnflags=1, count=1)
    # BINA ICI YEDEK: bir Sovyet kampa girince dogus yalniz binalarin icinde
    for i, q in enumerate(M_N[7:11] + [(2000, 2290, 0, 0, 'baraka_a'), (2250, 2290, 0, 0, 'baraka_a'),
                                       (3520, 2860, 0, 0, 'depo_a'), (3200, 2880, 0, 0, 'depo_a')]):
        sp(TUFEK[i % len(TUFEK)], q[0], q[1], q[4], 270, targetname='bina_yedek', script_noteworthy=q[4], spawnflags=1, count=1)
    # KARSI SALDIRI (50): kampi cevreleyen orman, her yonden (sinir icinde, egim uygun)
    KARSI = []
    for (x, y) in ((1200, 1700), (1150, 2200), (1200, 2700), (1300, 3300), (1900, 3550), (2600, 3600),
                   (3300, 3600), (4000, 3550), (4700, 3300), (4800, 2700), (4800, 2100), (4750, 1500),
                   (4400, 1000), (3600, 900), (1100, 1200), (2900, 3450), (4600, 2400), (1000, 2450)):
        p_ = yer_bul(x, y, 28, None, 260)
        if p_ and egim_ok(*p_, adim=40):
            KARSI.append(p_)
    assert len(KARSI) >= 10, ('karsi saldiri noktasi az', len(KARSI))
    for i, (x, y) in enumerate(KARSI):
        sp(TUFEK[i % len(TUFEK)], x, y, None, 0, targetname='karsi', spawnflags=1, count=1)
    print('karsi saldiri dogus noktasi:', len(KARSI), KARSI)
    # MG nisancilari (2): kule platformlarinda; taret misc_turret 'kule_mg'
    for (cx, cy, zp, _y, _x) in G.KULE:
        H.ent('misc_turret', model='xmodel/weapon_mg42', weaponinfo='mg42_bipod_stand', targetname='kule_mg',
              origin=(cx, cy - 62, zp + 34), angles=(0, 270, 0), script_noteworthy=str(cx))
        H.ent('actor_axis_snow_wehr_reg_kar98k', origin=(cx, cy - 10, zp + 4), angles=(0, 270, 0),
              targetname='kamp_mg', script_aigroup='kamp_dis', spawnflags=1, count=1)
        say['mg'] = say.get('mg', 0) + 1

    # EV SIPERLERI (karsi saldiri): pencere ve kapi arkalari -- script_origin 'ev_siper'
    EVS = [('baraka_a', 1950, 2070 + 38, 270), ('baraka_a', 2150, 2070 + 38, 270), ('baraka_a', 2280, 2070 + 38, 270),
           ('baraka_a', 1820 + 38, 2210, 180), ('baraka_a', 2380 - 50, 2160, 0), ('baraka_a', 2060, 2350 - 50, 90),
           ('baraka_a', 2240, 2300, 90),
           ('depo_a', 3220, 2770 + 38, 270), ('depo_a', 3530, 2770 + 38, 270), ('depo_a', 3330, 2770 + 40, 270)]
    # merkez bina zemin kat: her pencerenin hemen arkasi (kullanici: siper pencere onu)
    EVS += [('merkez0', x, BY0 + 16 + 22, 270) for x in (2650, 2800, 3200, 3350)]
    EVS += [('merkez0', x, BY1 - 16 - 22, 90) for x in (2650, 3100, 3350)]
    EVS += [('merkez0', BX0 + 16 + 22, y, 180) for y in (2150, 2450)]
    EVS += [('merkez0', BX1 - 16 - 22, y, 0) for y in (2120, 2480)]
    for i, (oda, x, y, yaw) in enumerate(EVS):
        q = yer_bul(x, y, 16, oda, 160 if oda == 'baraka_a' else 90)
        if q:
            ent('script_origin', targetname='ev_siper', script_noteworthy=oda, origin=(q[0], q[1], oda_z(oda) + 4), angles=(0, yaw, 0))
            if oda == 'baraka_a':                 # karsi saldirida bir kez dogan 7 Sovyet
                kv = dict(origin=(q[0], q[1], oda_z(oda) + 4), angles=(0, yaw, 0), targetname='ev_sovyet', spawnflags=1, count=1)
                if i == 4:
                    kv['script_noteworthy'] = 'kapi'
                H.ent(SOV[i % len(SOV)], **kv)
                say['ev_sovyet'] = say.get('ev_sovyet', 0) + 1
    # merkez bina UST KAT pencere arkalari (ust katta yol agi yok: GSC gorulmeden yerlestirir)
    UZ = G.BZU + 4
    UST = [(x, BY0 + 16 + 24) for x in (2650, 2800, 3200, 3350)] + [(x, BY1 - 16 - 24) for x in (2650, 3100, 3350)] + \
          [(BX0 + 16 + 24, y) for y in (2150, 2450)] + [(BX1 - 16 - 24, y) for y in (2120, 2300)]
    for (x, y) in UST:
        ent('script_origin', targetname='ust_siper', origin=(x, y, UZ))
    # merkez bina ust kat MG42 (guney orta pencere, denizlik BZU+34)
    H.ent('misc_turret', model='xmodel/weapon_mg42', weaponinfo='mg42_bipod_stand', targetname='bina_mg',
          origin=(3000, BY0 + 10, G.BZU + 34), angles=(0, 270, 0))
    ent('script_origin', targetname='bina_mg_yer', origin=(3000, BY0 + 42, G.BZU + 4))
    # =====================================================================
    # 6. BETIK NOKTALARI
    # =====================================================================
    gx, gy = G.GUVENLI
    ent('script_origin', targetname='guvenli', origin=(gx, gy, zz(gx, gy, 0)))
    for (x, y) in G.KONVOY_DURUS:
        ent('script_origin', targetname='konvoy_durus', origin=(round(x), round(y), zz(x, y, 0)))
    ent('script_origin', targetname='patlama', origin=(round(G.PATLAMA[0]), round(G.PATLAMA[1]), zz(*G.PATLAMA, ust=0)))
    for (x, y, z) in ((2650, 2050, BZ + 40), (3350, 2050, BZ + 40), (2650, 2550, BZ + 40), (3350, 2550, BZ + 40),
                      (3000, 2300, BZ + 20), (3000, 2300, BZU + 60), (2700, 2300, BZU + 120), (3300, 2300, BZU + 120)):
        ent('script_origin', targetname='bina_fx', origin=(x, y, z))
    ent('script_origin', targetname='kopru', origin=(round(G.dere_x(G.KOPRU_Y[0])), round(G.KOPRU_Y[0]), round(G.KOPRU_Z[0])))
    ent('script_origin', targetname='kamp_kapi', origin=(KX, ky0 - 200, zz(KX, ky0 - 200, 0)))
    ent('script_origin', targetname='kamp_merkez_nokta', origin=(3000, 1850, zz(3000, 1850, 0)))
    ent('script_origin', targetname='yan_kapi', origin=(3700, 1650, zz(3700, 1650, 0)))
    G.SIPER = SIPER
    G.SAY = say
    print('siper:', {k: len(v) for k, v in SIPER.items()})
    print('yerlesim:', ', '.join('%s %d' % kv for kv in sorted(say.items())))
