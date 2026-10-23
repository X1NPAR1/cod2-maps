# -*- coding: utf-8 -*-
"""
ent_kasrelbab.py -- yerlesim: yol dugumleri, siperler, pencere noktalari, araclar
(konvoy 4, Crusader 5, Panzer 1, Ingiliz kamyonu), spawner'lar, flak88'ler, sur MG'leri.

SAYILAR (kullanici): kulube 2 | kasaba 25 (+ sur MG nisancilari) | flak murettebati 3 x 3 |
konvoy: 2 Blitz (yolcu dolu) + yari paletli + Panzer II | 5 Crusader + 20 Ingiliz + Price.
"""
import math

YARICAP = (('tree_desertpalm', 40), ('tree_desertbushy', 40), ('vehicle_', 190), ('haycart', 100),
           ('military_sandbag', 115), ('prop_crate', 36), ('prop_barrel', 22), ('egypt_prop_vase', 18),
           ('furniture_northafrica_longtable', 60), ('brush_', 0))

def yerlestir(G):
    H, yuk = G.H, G.yukseklik
    say = {}
    ZK, BZ = G.ZK, G.BZ
    DUGUM = []

    def ent(sinif, **kv):
        if sinif.startswith('node_'):
            x, y, z = kv['origin']
            if any(abs(x - a) < 40 and abs(y - b) < 40 and abs(z - c) < 60 for (a, b, c) in DUGUM):
                if 'targetname' not in kv:
                    return None
            DUGUM.append(kv['origin'])
        say[sinif] = say.get(sinif, 0) + 1
        return H.ent(sinif, **kv)

    def yaricap(m):
        for (on, r) in YARICAP:
            if m.startswith(on):
                return r
        return 30

    def kasabada(x, y, pay=280):
        return G.TX0 - pay < x < G.TX1 + pay and G.TY0 - pay < y < G.TY1 + pay

    def zz(x, y, ust=8):
        if kasabada(x, y, 300):
            return round(ZK + 1 + ust, 1)
        kx0, ky0, kx1, ky1 = G.KULUBE
        if kx0 - 200 < x < kx1 + 200 and ky0 - 200 < y < ky1 + 200:
            return round(ZK + 11 + ust, 1)
        return round(yuk(x, y) + ust, 1)

    IC = {}
    for (ad, x0, y0, x1, y1, gir, ac, dm) in G.BINALAR:
        if gir:
            IC[ad] = (x0, y0, x1, y1)
    IC['kulube'] = G.KULUBE

    def ic_serbest(x, y, r, oda):
        x0, y0, x1, y1 = IC[oda]
        if not (x0 + 16 + r <= x <= x1 - 16 - r and y0 + 16 + r <= y <= y1 - 16 - r):
            return False
        for (m, mx, my) in G.MODELLER:
            rr = yaricap(m)
            if rr and math.hypot(x - mx, y - my) < rr + r:
                return False
        return True

    def duvar_mes(x, y):
        return min([G._seg(x, y, (a, b), (c, d)) for (a, b, c, d) in G.DUVARLAR] + [1e9])

    def serbest(x, y, r=26, oda=None):
        if oda is not None:
            return ic_serbest(x, y, r, oda)
        if not G.icinde(x, y) and G.giris_mes(x, y) > 200:
            return False
        for ad, v in G.YAPILAR.items():
            if v[0] - r - 14 <= x <= v[2] + r + 14 and v[1] - r - 14 <= y <= v[3] + r + 14:
                return False
        if duvar_mes(x, y) < G.SUR_K + r + 14:
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
        if kasabada(x, y, 250):
            return True
        z = yuk(x, y)
        return all(abs(yuk(x + dx, y + dy) - z) < 55 for (dx, dy) in ((adim, 0), (-adim, 0), (0, adim), (0, -adim)))

    # =====================================================================
    # 1. SIPERLER ve PENCERE NOKTALARI
    # =====================================================================
    SIPER = []
    def siper(tur, x, y, yaw, r=24):
        p = yer_bul(x, y, r, None, 80)
        if not p or not egim_ok(*p, adim=50):
            return None
        e = ent(tur, origin=(p[0], p[1], zz(*p)), angles=(0, yaw, 0))
        if e is not None:
            SIPER.append((p[0], p[1]))
        return p
    for ad, (x0, y0, x1, y1, _g) in list(G.YAPILAR.items()):
        if not kasabada((x0 + x1) / 2.0, (y0 + y1) / 2.0, 0) or ad.startswith('kule') or ad == 'minare' or ad.endswith('_ust'):
            continue
        for (x, y, yaw) in ((x0 - 50, y0 - 50, 225), (x1 + 50, y0 - 50, 315), (x0 - 50, y1 + 50, 135), (x1 + 50, y1 + 50, 45)):
            siper('node_cover_crouch', x, y, yaw)
    for (m, mx, my) in G.MODELLER:
        if (m.startswith('military_sandbag') or m.startswith('prop_crate')) and (kasabada(mx, my, 300) or math.hypot(mx - G.KULUBE_M[0], my - G.KULUBE_M[1]) < 600):
            for (dx, dy) in ((0, 120), (0, -120), (120, 0), (-120, 0)):
                siper('node_cover_crouch', mx + dx, my + dy, round(math.degrees(math.atan2(-dy, -dx))) % 360)
    # sur disi (Ingiliz yaklasimi): kum tepeleri ve kayalar
    for (x, y) in ((1500, 1500), (1400, 2050), (1500, 2700), (1650, 3300), (2100, 1900), (2150, 3000), (1100, 2400),
                   (500, 1800), (600, 3000), (-200, 600), (-800, -300), (-1500, -700), (-2300, -800)):
        siper('node_cover_crouch', x, y, 0)
    PEN = []
    def pencere(oda, x, y, yaw):
        q = yer_bul(x, y, 16, oda, 60)
        if q:
            ent('script_origin', targetname='pencere', script_noteworthy=oda, origin=(q[0], q[1], BZ + 4), angles=(0, yaw, 0))
            PEN.append((q[0], q[1], oda, yaw))
    for (ad, x0, y0, x1, y1, gir, ac, dm) in G.BINALAR:
        if not gir:
            continue
        for yon, liste in ac.items():
            for (tur, m) in liste:
                if tur != 'pen':
                    continue
                if yon == 'g': pencere(ad, m, y0 + 16 + 22, 270)
                elif yon == 'k': pencere(ad, m, y1 - 16 - 22, 90)
                elif yon == 'b': pencere(ad, x0 + 16 + 22, m, 180)
                else: pencere(ad, x1 - 16 - 22, m, 0)

    # =====================================================================
    # 2. YOL DUGUMLERI
    # =====================================================================
    def izgara(x0, x1, y0, y1, adim, r=26):
        for x in range(int(x0), int(x1) + 1, adim):
            for y in range(int(y0), int(y1) + 1, adim):
                if serbest(x, y, r) and egim_ok(x, y):
                    ent('node_pathnode', origin=(x, y, zz(x, y)))
    izgara(G.TX0 - 250, G.TX1 + 250, G.TY0 - 250, G.TY1 + 250, 90, 22)          # kasaba: siki
    kx, ky = G.KULUBE_M
    izgara(kx - 700, kx + 700, ky - 700, ky + 700, 120)                            # kulube
    izgara(-500, G.TX0 - 260, 700, 4000, 220)                                      # Ingiliz yaklasimi
    # olculdu: 420'lik seyrek izgara baglanmiyordu (1029 'no connections') -> yalniz AI'nin
    # yurudugu koridorlar, 180 aralik: takviye yolu, baslangic -> kulube -> kasaba kapisi
    KOR = [list(G.TAKVIYE), [G.BASLANGIC, (-4500, -3300), (-3300, -2400), G.KULUBE_M],
           [G.KULUBE_M, (-600, 300), (900, 1700), (1900, 2400), (G.TX0 - 200, 2500)],
           [(1900, 2400), (1650, 1650), (1900, 1100)], [(1900, 2400), (1650, 2850), (1800, 3450)],
           [(G.TX1 + 200, 2600), (6900, 2620)]]
    def koridor_mes(x, y):
        return min(G._seg(x, y, h[i], h[i + 1]) for h in KOR for i in range(len(h) - 1))
    for x in range(-8400, 8401, 180):
        for y in range(-6660, 6661, 180):
            if koridor_mes(x, y) < 420 and serbest(x, y) and egim_ok(x, y):
                ent('node_pathnode', origin=(x, y, zz(x, y)))
    for oda, (x0, y0, x1, y1) in IC.items():
        zt = (ZK + 13 + 8) if oda == 'kulube' else (BZ + 8)
        for x in range(int(x0) + 56, int(x1) - 55, 80):
            for y in range(int(y0) + 56, int(y1) - 55, 80):
                if serbest(x, y, 20, oda):
                    ent('node_pathnode', origin=(x, y, zt))
    # kapilar: ic + dis
    for (ad, x0, y0, x1, y1, gir, ac, dm) in G.BINALAR + [('kulube',) + tuple(G.KULUBE) + (True, {'g': [('kapi', -1800)]}, None)]:
        if not gir:
            continue
        zt = (ZK + 13 + 8) if ad == 'kulube' else (BZ + 8)
        for yon, liste in ac.items():
            for (tur, m) in liste:
                if tur != 'kapi':
                    continue
                if yon == 'g': ic_, dis_ = (m, y0 + 50), (m, y0 - 110)
                elif yon == 'k': ic_, dis_ = (m, y1 - 50), (m, y1 + 110)
                elif yon == 'b': ic_, dis_ = (x0 + 50, m), (x0 - 110, m)
                else: ic_, dis_ = (x1 - 50, m), (x1 + 110, m)
                ent('node_pathnode', origin=(ic_[0], ic_[1], zt))
                ent('node_pathnode', origin=(dis_[0], dis_[1], zz(*dis_)))
    # buyuk kapi ve cikis kapisi gecitleri
    for x in (G.TX0 - 120, G.TX0, G.TX0 + 120):
        ent('node_pathnode', origin=(x, 2500, ZK + 9))
    for x in (G.TX1 - 120, G.TX1, G.TX1 + 120):
        ent('node_pathnode', origin=(x, 2600, ZK + 9))

    # =====================================================================
    # 3. ARACLAR
    # =====================================================================
    def arac_z(x, y):
        return round(yuk(x, y) + 16, 1) if not kasabada(x, y, 300) else round(ZK + 17, 1)
    def arac(ad, grup, nokta, hiz, tur, model, binen=None, yerler=(), takim='allies', son_yavas=True, durak=None):
        for i, (x, y) in enumerate(nokta):
            kv = {'origin': (round(x, 1), round(y, 1), arac_z(x, y)),
                  'targetname': ad + '_yol' if i == 0 else ('%s_durak' % ad if i == durak else '%s_yol_%d' % (ad, i))}
            if i + 1 < len(nokta):
                kv['target'] = ('%s_durak' % ad) if (i + 1) == durak else '%s_yol_%d' % (ad, i + 1)
            if i == 0:
                kv.update(spawnflags=1, speed=hiz, lookahead=1)
            if son_yavas and i == len(nokta) - 3:
                kv['speed'] = max(5, hiz // 2)
            H.ent('info_vehicle_node', **kv)
        (x0, y0), (x1, y1) = nokta[0], nokta[1]
        yaw = round(math.degrees(math.atan2(y1 - y0, x1 - x0)), 1)
        ek = {}
        if binen is not None:
            ek['script_vehicleride'] = binen
        if takim == 'axis':
            ek['script_turret'] = 0                 # kullanici: Panzer kendiliginden ates ediyordu (_tank turret_attack_think)
        H.ent('script_vehicle', targetname=ad, target=ad + '_yol', vehicletype=tur, model=model,
              script_vehiclespawngroup=grup, script_team=takim,
              origin=(round(x0, 1), round(y0, 1), arac_z(x0, y0) - 14), angles=(0, yaw, 0), **ek)
        L0 = math.hypot(x1 - x0, y1 - y0) or 1
        ux, uy = (x1 - x0) / L0, (y1 - y0) / L0
        for k, (yer, c, ekstra) in enumerate(yerler):
            yan = 80 if k % 2 == 0 else -80
            geri = 20 + (k // 2) * 60
            ox, oy = x0 + ux * geri - uy * yan, y0 + uy * geri + ux * yan
            say[c] = say.get(c, 0) + 1
            kv = dict(origin=(round(ox, 1), round(oy, 1), round(yuk(ox, oy) + 4, 1)), angles=(0, yaw, 0),
                      targetname=ad + '_asker', script_vehicleride=binen, script_startingposition=yer,
                      spawnflags=1, count=1)
            kv.update(ekstra)
            H.ent(c, **kv)
    ALMAN = ['actor_axis_afrikakorp_reg_kar98', 'actor_axis_afrikakorp_reg_mp40', 'actor_axis_afrikakorp_reg_kar98',
             'actor_axis_afrikakorp_reg_g43', 'actor_axis_afrikakorp_reg_mp40']
    BRIT = ['actor_ally_brit_africa_reg_rifle', 'actor_ally_brit_africa_reg_thompson', 'actor_ally_brit_africa_reg_bren',
            'actor_ally_brit_africa_reg_sten', 'actor_ally_brit_africa_reg_rifle', 'actor_ally_brit_africa_reg_thompson']
    KH = G.KONVOY
    LK = G.hat_uzunluk(KH)
    # KONVOY (yavas, 9 mph): Blitz, Blitz, yari paletli, Panzer II (GSC aralikla yola cikarir)
    K_NOK = G.hat_kes(KH, 0, LK)                                       # kullanici: soldaki yolun arkasindan (gizli bas)
    for k, (ad, tur, model, n_yolcu) in enumerate((('konvoy1', 'blitz', 'xmodel/vehicle_opel_blitz_desert', 9),
                                                  ('konvoy2', 'blitz', 'xmodel/vehicle_opel_blitz_desert', 9),
                                                  ('konvoy3', 'germanhalftrack', 'xmodel/vehicle_halftrack_mg_desert', 8),
                                                  ('konvoy4', 'panzer2', 'xmodel/vehicle_panzer_ii', 0))):
        yer = [(i, ALMAN[i % len(ALMAN)], {}) for i in range(n_yolcu)]
        arac(ad, 1 + k, K_NOK, 12, tur, model, binen=(1 + k) if n_yolcu else None, yerler=yer, takim='axis', son_yavas=False)
    # CRUSADER (5): takviye vadisinden, sur onunde yelpaze
    TH = G.TAKVIYE
    for k, (sx, sy) in enumerate(G.CR_DURAK):
        ortak = G.hat_kes(TH[:7], 0, G.hat_uzunluk(TH[:7]))         # (-3300,-3500)'e kadar ortak vadi
        n = ortak + [(-2900 + k * 380, -3000 + k * 160), (-300 + k * 260, -900 + k * 480), (sx - 700, sy - 250 + k * 40), (sx, sy)]
        # kullanici: kasabaya girince Crusaderlar dumduz ilerleyip gozden kaybolur ->
        # durak dugumu 'crusader%d_durak'; ardindan sur boyunca kuzey/guneye uzaklasma
        yon_ = 1 if sy > 2400 else -1
        devam = [(sx + 150, sy + yon_ * 1000), (sx + 250, sy + yon_ * 2400), (sx + 350, sy + yon_ * 3800), (sx + 450, sy + yon_ * 5200)]   # kullanici: gozumuzun onunde kaybolmasin
        arac('crusader%d' % (k + 1), 5 + k, n + devam, 12, 'crusader', 'xmodel/vehicle_crusader2', son_yavas=False, durak=len(n) - 1)
    # PANZER (son): cikis yolundan gelir, dogu kapisinin onunde durur
    PN = [(9600, -800), (8300, -250), (7300, 450), (6573, 978), (6400, 1900), (6347, 2609), (5992, 2595), (5560, 2600)]   # kullanici: durak daha ileride
    arac('panzer_son', 10, G.hat_kes(PN, 0, G.hat_uzunluk(PN)), 9, 'panzer2', 'xmodel/vehicle_panzer_ii', takim='axis')
    # INGILIZ KAMYONU (son): takviye yolunun ucundan buyuk kapinin onune
    # INGILIZ KAMYONU (son): Panzer'in durdugu yerde, KASASI kasabaya (batiya) donuk, duruk
    arac('kamyon', 11, [(3110, 2500), (2950, 2500), (2450, 2490), (1900, 2400), (1100, 1880), (300, 1050), (-300, 600)], 8, 'blitz',
         'xmodel/vehicle_opel_blitz_desert', son_yavas=False)   # final: bati kapisindan konvoy yoluna dogru
    _bt = []
    G.H.kutu(3240, 2420, ZK + 1, 3340, 2580, ZK + 120, 'trigger', 'trigger', alt='trigger', hedef=_bt)   # kasaya binme (kamyon arkasi)
    _pt = []
    G.H.kutu(5660, 2490, ZK + 1, 5820, 2710, ZK + 120, 'trigger', 'trigger', alt='trigger', hedef=_pt)   # Panzer arkasi (yapiskan bomba)
    H.ent('trigger_use', brushlar=_pt, targetname='panzer_tetik')
    H.ent('trigger_use', brushlar=_bt, targetname='kamyon_bin')
    print('konvoy yolu %d birim (9 mph ~%.0f sn)' % (LK, LK / (9 * 17.6)))

    # =====================================================================
    # 4. SPAWNER'LAR
    # =====================================================================
    def sp(c, x, y, oda=None, aci=90, z=None, **kv):
        if z is None:
            p = yer_bul(x, y, 28, oda, 220)
            if not p:
                raise SystemExit('SPAWNER YERI YOK: %s %s %s' % (c, x, y))
            if oda == 'kulube':
                z = ZK + 13 + 4
            elif oda:
                z = BZ + 4
            else:
                z = zz(*p, ust=4)
        else:
            p = (x, y)
        kv = {k: v for k, v in kv.items() if v is not None}
        kv.setdefault('angles', (0, aci, 0))
        say[c] = say.get(c, 0) + 1
        return H.ent(c, origin=(round(p[0]), round(p[1]), round(z, 1)), **kv)
    # KULUBE (2): biri disarida nobet, biri icerde telsiz basinda
    sp('actor_axis_afrikakorp_reg_kar98', -1760, -1220, 'kulube', 90, targetname='kulube_alman', script_noteworthy='telsizci',
       script_aigroup='kulube', spawnflags=1, count=1)
    # KASABA (25): pencereler, barikatlar, meydan, avlular
    n = 0
    for (x, y, oda, yaw) in PEN[:11]:
        sp(ALMAN[n % 5], x, y, oda, yaw, targetname='kasaba', script_aigroup='kasaba', spawnflags=1, count=1)
        n += 1
    for (x, y) in ((3950, 2350), (3980, 2620), (4870, 2450), (4880, 2700), (3300, 2500), (5500, 2550), (4300, 1950),
                   (4600, 3050), (3900, 3800 - 120), (5000, 1300 + 120), (3050, 3300), (6000, 3200), (5950, 1700), (4450, 2100),
                   (3300, 2100), (3700, 2850), (4200, 2650), (4700, 2300), (5150, 2550), (5450, 2950), (3850, 1550), (4750, 3650)):
        if n >= 32:
            break
        sp(ALMAN[n % 5], x, y, None, 180, targetname='kasaba', script_aigroup='kasaba', spawnflags=1, count=1)
        n += 1
    assert n == 32, n
    # PANZER ONCESI SALDIRI (10): cikis yolundan kasabaya
    for j in range(10):
        bx_, by_ = 7000 + (j % 5) * 140, 2560 + (j // 5) * 160 - 80
        sp(ALMAN[j % 5], bx_, by_, None, 180, targetname='dogu_alman', spawnflags=1, count=1)
    # FLAK MURETTEBATI (3 x 3)
    for i, (fx, fy, yaw) in enumerate(G.FLAKLAR):
        for k in range(3):
            a = math.radians(yaw + 140 + k * 40)
            sp(ALMAN[k], fx + math.cos(a) * 150, fy + math.sin(a) * 150, None, yaw, targetname='flak_murettebat',
               script_noteworthy=str(i + 1), script_aigroup='flak%d' % (i + 1), spawnflags=1, count=1)
    # SUR MG (2): bati kapi kuleleri ustu (dugumsuz; GSC yerinde tutar)
    for i, (cx, cy) in enumerate(G.KAPI_KULE):
        H.ent('misc_turret', model='xmodel/weapon_mg42', weaponinfo='mg42_bipod_stand', targetname='sur_mg',
              script_noteworthy=str(i + 1), origin=(cx - 120 + 14, cy, ZK + 444), angles=(0, 180, 0))
        sp('actor_axis_afrikakorp_reg_kar98', cx - 60, cy, None, 180, z=ZK + 404, targetname='sur_mg_alman',
           script_noteworthy=str(i + 1), spawnflags=1, count=1)
    # FLAK 88 modelleri + patlayici tetikleri
    for i, (fx, fy, yaw) in enumerate(G.FLAKLAR):
        H.ent('script_model', model='xmodel/german_artillery_flak88_aa_static', targetname='flak', script_noteworthy=str(i + 1),
              origin=(fx, fy, ZK + 1), angles=(0, yaw, 0))
        bl = []
        G.H.kutu(fx - 110, fy - 110, ZK + 1, fx + 110, fy + 110, ZK + 120, 'trigger', 'trigger', alt='trigger', hedef=bl)
        H.ent('trigger_use', brushlar=bl, targetname='flak_tetik', script_noteworthy=str(i + 1))
    # INGILIZ TAKVIYESI (20) + PRICE: takviye yolunun harita ici kismi (baslangic sirtinin arkasi)
    IT = 0
    # kullanici: Price + 3 kisi dogdugu yerde kaldi (dik yamac, 'in solid' dugumler) -> takviye yolunun
    # duz tabaninda, yolun 230 yaninda iki sira (Crusaderlar yolun ortasindan gecer)
    _ty = G.hat_kes(G.TAKVIYE[3:5], 0, G.hat_uzunluk(G.TAKVIYE[3:5]))
    def _yan(t_, d_):
        (ax, ay), (bx, by) = G.TAKVIYE[3], G.TAKVIYE[4]
        L_ = math.hypot(bx - ax, by - ay); ux, uy = (bx - ax) / L_, (by - ay) / L_
        return (ax + ux * t_ - uy * d_, ay + uy * t_ + ux * d_)
    for j in range(12):
        q_ = _yan(300 + (j // 2) * 110, 230 + (j % 2) * 80)
        p = yer_bul(q_[0], q_[1], 26, None, 200)
        if p:
            sp(BRIT[j % len(BRIT)], p[0], p[1], None, 30, z=zz(p[0], p[1], ust=18), targetname='ingiliz', spawnflags=1, count=1)
            IT += 1
    assert IT == 12, IT
    _pr = _yan(1100, 260)
    sp('actor_ally_brit_africa_price', round(_pr[0], 1), round(_pr[1], 1), None, 30, z=zz(_pr[0], _pr[1], ust=18), targetname='price', script_friendname='Cpt. Price', spawnflags=1, count=1)

    # =====================================================================
    # 5. BETIK NOKTALARI
    # =====================================================================
    ent('script_origin', targetname='cali', origin=(G.CALI_M[0], G.CALI_M[1], round(yuk(*G.CALI_M), 1)))
    ent('script_origin', targetname='kulube_m', origin=(kx, ky, ZK + 13))
    ent('script_origin', targetname='kasaba_meydan', origin=(4400, 2450, ZK + 1))
    ent('script_origin', targetname='buyuk_kapi_m', origin=(G.TX0, 2500, ZK + 120))
    ent('script_origin', targetname='cikis_kapi_m', origin=(G.TX1, 2600, ZK + 1))
    ent('script_origin', targetname='toplanma', origin=(-2200, -900, zz(-2200, -900, ust=0)))
    ent('script_origin', targetname='kamyon_yan', origin=(3200, 2660, ZK + 1))
    ent('script_origin', targetname='konvoy_son', origin=(G.KONVOY_SON[0], G.KONVOY_SON[1], round(yuk(*G.KONVOY_SON), 1)))
    ent('script_origin', targetname='panzer_arka', origin=(5740, 2600, ZK + 1))
    G.SAY = say
    print('pencere: %d, siper: %d' % (len(PEN), len(SIPER)))
    print('yerlesim:', ', '.join('%s %d' % kv for kv in sorted(say.items())))
