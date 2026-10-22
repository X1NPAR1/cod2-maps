# -*- coding: utf-8 -*-
"""
ent_kumtepe.py -- yerlesim: yol dugumleri, siperler, pencere/cati noktalari,
kamyon (oyuncu + Price + 7), 4 Panzer II + 4 Crusader yollari, Alman/Ingiliz
spawner'lari, betik noktalari. Her spawner/node bosluk denetiminden gecer.

SAYILAR (kullanici): koy 15 | savunma 6 dalga x 10 = 60 | 4 Panzer + 30 piyade |
4 Crusader | 20 Ingiliz takviye | Price + 7.
"""
import math

YARICAP = (('tree_desertpalm', 40), ('tree_desertbushy', 40), ('vehicle_', 190), ('haycart', 100), ('military_sandbag', 115), ('egypt_prop_well', 70),
           ('prop_crate', 36), ('prop_barrel', 22), ('furniture_northafrica_longtable', 60),
           ('furniture_northafrica_armoire', 50), ('furniture_northafrica', 30), ('egypt_prop_vase', 18),
           ('egypt_prop_cloth', 0), ('brush_', 0))

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

    def avluda(x, y):
        return -1000 < x < 1000 and -1000 < y < 1000

    def zz(x, y, ust=8):
        if avluda(x, y):
            return round(ZK + 1 + ust, 1)
        return round(yuk(x, y) + ust, 1)

    IC = {'ikikat': (-900, 300, -360, 820), 'ev': (380, -820, 880, -380)}

    def ic_serbest(x, y, r, oda):
        x0, y0, x1, y1 = IC[oda]
        if not (x0 + 16 + r <= x <= x1 - 16 - r and y0 + 16 + r <= y <= y1 - 16 - r):
            return False
        for (m, mx, my) in G.MODELLER:
            rr = yaricap(m)
            if rr and math.hypot(x - mx, y - my) < rr + r:
                return False
        return True

    def serbest(x, y, r=26, oda=None):
        if oda is not None:
            return ic_serbest(x, y, r, oda)
        if not G.icinde(x, y) and G.yol_mes_ham(x, y, 'konvoy') > 200:
            return False
        for ad, v in G.YAPILAR.items():
            if v[0] - r - 14 <= x <= v[2] + r + 14 and v[1] - r - 14 <= y <= v[3] + r + 14:
                return False
        for (m, mx, my) in G.MODELLER:
            rr = yaricap(m)
            if rr and abs(x - mx) < rr + r and abs(y - my) < rr + r and math.hypot(x - mx, y - my) < rr + r:
                return False
        for (kx, ky, kr) in G.KAYALAR:
            if math.hypot(x - kx, y - ky) < kr + r + 10:
                return False
        mx_, my_, _ = G.MERDIVEN
        if abs(x - mx_) < 30 + r and abs(y - my_) < 30 + r:
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
        if avluda(x, y):
            return True
        z = yuk(x, y)
        return all(abs(yuk(x + dx, y + dy) - z) < 55 for (dx, dy) in ((adim, 0), (-adim, 0), (0, adim), (0, -adim)))

    # =====================================================================
    # 1. SIPERLER (dis) ve PENCERE / CATI NOKTALARI
    # =====================================================================
    SIPER = {'koy': [], 'dis': []}
    def siper(grup, tur, x, y, yaw, r=24):
        p = yer_bul(x, y, r, None, 80)
        if not p or not egim_ok(*p, adim=50):
            return None
        e = ent(tur, origin=(p[0], p[1], zz(*p)), angles=(0, yaw, 0))
        if e is not None:
            SIPER[grup].append((p[0], p[1], zz(*p), yaw))
        return p
    # bina koseleri ve kum torbalari arkasi (dis yuz)
    for ad, (x0, y0, x1, y1, _g) in list(G.YAPILAR.items()):
        if ad.endswith('_ust'):
            continue
        for (x, y, yaw) in ((x0 - 50, y0 - 50, 225), (x1 + 50, y0 - 50, 315), (x0 - 50, y1 + 50, 135), (x1 + 50, y1 + 50, 45)):
            siper('koy', 'node_cover_crouch', x, y, yaw)
    for (m, mx, my) in G.MODELLER:
        if m.startswith('military_sandbag') or m.startswith('prop_crate') or m.startswith('egypt_prop_well') or \
           (m.startswith('vehicle_') and math.hypot(mx, my) < 1100) or m == 'haycart':
            for (dx, dy) in ((0, 80), (0, -80), (80, 0), (-80, 0)):
                siper('koy', 'node_cover_crouch', mx + dx, my + dy, round(math.degrees(math.atan2(-dy, -dx))) % 360)
    # pencere arkalari (girilebilir binalar) -> script_origin 'pencere' (+ cover node)
    PEN = []
    def pencere(oda, x, y, yaw):
        q = yer_bul(x, y, 16, oda, 60)
        if q:
            ent('script_origin', targetname='pencere', script_noteworthy=oda, origin=(q[0], q[1], BZ + 4), angles=(0, yaw, 0))
            PEN.append((q[0], q[1], BZ + 4, oda))
    for x in (-800, -460):
        pencere('ikikat', x, 300 + 16 + 22, 270)
    for x in (-760, -500):
        pencere('ikikat', x, 820 - 16 - 22, 90)
    for y in (450, 680):
        pencere('ikikat', -900 + 16 + 22, y, 180)
    for y in (420, 720):
        pencere('ikikat', -360 - 16 - 22, y, 0)
    for x in (500, 760):
        pencere('ev', x, -820 + 16 + 22, 270)
    pencere('ev', 760, -380 - 16 - 22, 90)
    pencere('ev', 380 + 16 + 22, -700, 180)
    pencere('ev', 880 - 16 - 22, -600, 0)
    # EV ICI noktalar (pencere yetmezse; yalniz iki girilebilir ev)
    for (oda, x, y) in (('ikikat', -780, 420), ('ikikat', -520, 420), ('ikikat', -780, 680), ('ikikat', -520, 690), ('ikikat', -650, 560),
                        ('ev', 470, -560), ('ev', 800, -560), ('ev', 560, -700), ('ev', 760, -700)):
        q = yer_bul(x, y, 18, oda, 90)
        if q:
            ent('script_origin', targetname='ev_ic', script_noteworthy=oda, origin=(q[0], q[1], BZ + 4))
    # cati noktalari (GB binanin catisi, parapet arkasi)
    x0, y0, x1, y1 = G.CATI_EV
    CZ = G.MERDIVEN[2]
    CATI = [(x0 + 40, y0 + 60, 225), (x0 + 40, y1 - 60, 135), ((x0 + x1) / 2, y0 + 40, 270), ((x0 + x1) / 2, y1 - 40, 90),
            (x1 - 50, y0 + 60, 315), (x0 + 40, (y0 + y1) / 2, 180)]
    for (x, y, yaw) in CATI:
        ent('script_origin', targetname='cati_yer', origin=(round(x), round(y), CZ + 4), angles=(0, yaw, 0))

    # =====================================================================
    # 2. YOL DUGUMLERI
    # =====================================================================
    for x in range(-5400, 5401, 75):
        for y in range(-4500, 4501, 75):
            if avluda(x, y):
                continue
            km = math.hypot(x, y)
            adim = 150 if km < 2400 else 225          # acik colde seyrek (dugum sinirina pay)
            if x % adim or y % adim:
                continue
            if not G.icinde(x, y) or not serbest(x, y) or not egim_ok(x, y):
                continue
            ent('node_pathnode', origin=(x, y, zz(x, y)))
    for x in range(-960, 961, 75):                    # avlu: siki izgara
        for y in range(-960, 961, 75):
            if serbest(x, y, 22):
                ent('node_pathnode', origin=(x, y, zz(x, y)))
    for oda, (x0, y0, x1, y1) in IC.items():
        for x in range(int(x0) + 56, int(x1) - 55, 80):
            for y in range(int(y0) + 56, int(y1) - 55, 80):
                if serbest(x, y, 20, oda):
                    ent('node_pathnode', origin=(x, y, BZ + 8))
    # kapilar: ic + dis (rampa)
    for (x, y, dx, dy) in ((-630, 300, 0, -1), (-360, 560, 1, 0), (520, -380, 0, 1), (380, -520, -1, 0)):
        ent('node_pathnode', origin=(x - dx * 50, y - dy * 50, BZ + 8))
        ent('node_pathnode', origin=(x + dx * 110, y + dy * 110, zz(x + dx * 110, y + dy * 110)))
    # konvoy yolu boyu
    hat = G.KONVOY
    for i in range(len(hat) - 1):
        (ax, ay), (bx, by) = hat[i], hat[i + 1]
        n = max(1, int(math.hypot(bx - ax, by - ay) // 140))
        for k in range(n + 1):
            x, y = round(ax + (bx - ax) * k / n), round(ay + (by - ay) * k / n)
            if serbest(x, y, 20) and G.icinde(x, y):
                ent('node_pathnode', origin=(x, y, zz(x, y)))
    # cati: dugumler + el merdiveni (stok tankhunt ladder_up kalibi; >=40 aralik)
    mx_, my_, _ = G.MERDIVEN
    for (x, y, yaw) in CATI:
        ent('node_pathnode', origin=(round(x), round(y), CZ + 8))
    alt_x = mx_ + 14 + 34
    ust_x = mx_ - 40
    H.ent('node_negotiation_begin', origin=(round(alt_x), my_, zz(alt_x, my_)), angles=(0, 180, 0),
          animscript='ladder_up', targetname='cati_cik', target='cati_ust_dugum')
    H.ent('node_negotiation_end', origin=(round(ust_x), my_, CZ + 8), angles=(0, 180, 0), targetname='cati_ust_dugum')
    H.ent('node_negotiation_begin', origin=(round(ust_x - 46), my_, CZ + 8), angles=(0, 180, 0),
          animscript='ladder_down', targetname='cati_in', target='cati_alt_dugum')
    H.ent('node_negotiation_end', origin=(round(alt_x + 50), my_, zz(alt_x + 50, my_)), angles=(0, 0, 0), targetname='cati_alt_dugum')
    ent('node_pathnode', origin=(round(alt_x + 110), my_, zz(alt_x + 110, my_)))

    # =====================================================================
    # 3. ARACLAR
    # =====================================================================
    def arac_z(x, y):
        return round(yuk(x, y) + 16, 1)
    def arac(ad, grup, nokta, hiz, tur, model, binen=None, yerler=(), takim='allies', son_yaw=None):
        for i, (x, y) in enumerate(nokta):
            kv = {'origin': (round(x, 1), round(y, 1), arac_z(x, y)),
                  'targetname': ad + '_yol' if i == 0 else '%s_yol_%d' % (ad, i)}
            if i + 1 < len(nokta):
                kv['target'] = '%s_yol_%d' % (ad, i + 1)
            if i == 0:
                kv.update(spawnflags=1, speed=hiz, lookahead=1)
            if i == len(nokta) - 3:
                kv['speed'] = max(5, hiz // 2)
            if i == len(nokta) - 2 and ad == 'kamyon':
                kv['speed'] = 4                          # duraga yaklasirken iyice yavas
            H.ent('info_vehicle_node', **kv)
        (x0, y0), (x1, y1) = nokta[0], nokta[1]
        yaw = round(math.degrees(math.atan2(y1 - y0, x1 - x0)), 1)
        ek = {}
        if binen is not None:
            ek['script_vehicleride'] = binen
        H.ent('script_vehicle', targetname=ad, target=ad + '_yol', vehicletype=tur, model=model,
              script_vehiclespawngroup=grup, script_team=takim,
              origin=(round(x0, 1), round(y0, 1), arac_z(x0, y0) - 14), angles=(0, yaw, 0), **ek)
        L0 = math.hypot(x1 - x0, y1 - y0) or 1
        ux, uy = (x1 - x0) / L0, (y1 - y0) / L0
        for k, (yer, c, ekstra) in enumerate(yerler):
            yan = 70 if k % 2 == 0 else -70
            geri = 20 + (k // 2) * 60
            ox, oy = x0 + ux * geri - uy * yan, y0 + uy * geri + ux * yan
            say[c] = say.get(c, 0) + 1
            kv = dict(origin=(round(ox, 1), round(oy, 1), round(yuk(ox, oy) + 4, 1)), angles=(0, yaw, 0),
                      targetname=ad + '_asker', script_vehicleride=binen, script_startingposition=yer,
                      spawnflags=1, count=1)
            kv.update(ekstra)
            H.ent(c, **kv)
    BRIT = ['actor_ally_brit_africa_reg_rifle', 'actor_ally_brit_africa_reg_thompson', 'actor_ally_brit_africa_reg_bren',
            'actor_ally_brit_africa_reg_sten', 'actor_ally_brit_africa_reg_rifle', 'actor_ally_brit_africa_reg_thompson',
            'actor_ally_brit_africa_reg_rifle']
    # KAMYON: ~20 sn (kullanici); oyuncu kasada, sofor + Price + 7
    KH = G.KONVOY
    L = G.hat_uzunluk(KH)
    HIZ = 15                                                         # kullanici: baslangic 15
    yerler = [(0, 'actor_ally_brit_africa_reg_rifle', {}),
              (1, 'actor_ally_brit_africa_price', {'script_noteworthy': 'price', 'script_friendname': 'Cpt. Price'})]
    yerler += [(2 + i, BRIT[i], {}) for i in range(7)]
    arac('kamyon', 1, G.hat_kes(KH, 0, L), HIZ, 'blitz', 'xmodel/vehicle_opel_blitz_desert', binen=1, yerler=yerler)
    print('kamyon: yol %d, hiz %d mph (~%.1f sn)' % (L, HIZ, L / (HIZ * 17.6)))
    # CRUSADER (4): ayni yoldan, koyun dogusunda yelpaze; durunca batiya (Panzerlere) doner
    ana = G.hat_kes(KH, 0, G.hat_uzunluk(KH[:9]))                      # (2400,-200)'e kadar ortak yol
    ROTA = G.CR_ROTA                                                   # gen_kumtepe: kaya/agacsiz seritler
    for k, r_ in enumerate(ROTA):
        arac('crusader%d' % (k + 1), 2 + k, ana + r_, 14, 'crusader', 'xmodel/vehicle_crusader2')
    # PANZER II (4): batidan dort seritte
    for k, hat_ in enumerate(G.PANZER):
        n = G.hat_kes([(x, y) for (x, y) in hat_], 0, G.hat_uzunluk(hat_))
        arac('panzer%d' % (k + 1), 6 + k, n, 7, 'panzer2', 'xmodel/vehicle_panzer_ii', takim='axis')

    YP = G.YP_ROTA
    for k, ad in enumerate(('kuzey', 'bati', 'guney', 'dogu')):
        n = G.hat_kes(YP[ad], 0, G.hat_uzunluk(YP[ad]))
        yer = [(0, 'actor_axis_afrikakorp_reg_kar98', {}), (1, 'actor_axis_afrikakorp_reg_mp40', {})]
        yer += [(2 + i, ['actor_axis_afrikakorp_reg_kar98', 'actor_axis_afrikakorp_reg_mp40', 'actor_axis_afrikakorp_reg_g43'][i % 3], {})
                for i in range(6)]
        arac('yarim%d' % (k + 1), 10 + k, n, 12, 'germanhalftrack', 'xmodel/vehicle_halftrack_mg_desert', binen=10 + k,
             yerler=yer, takim='axis')

    # =====================================================================
    # 4. SPAWNER'LAR
    # =====================================================================
    ALMAN = ['actor_axis_afrikakorp_reg_kar98', 'actor_axis_afrikakorp_reg_mp40', 'actor_axis_afrikakorp_reg_kar98',
             'actor_axis_afrikakorp_reg_g43', 'actor_axis_afrikakorp_reg_mp40', 'actor_axis_afrikakorp_reg_kar98']
    def sp(c, x, y, oda=None, aci=90, z=None, **kv):
        if z is None:
            p = yer_bul(x, y, 28, oda, 220)
            if p and oda is None and not egim_ok(*p, adim=40):
                for (dx, dy) in ((60, 0), (-60, 0), (0, 60), (0, -60), (120, 0), (-120, 0), (0, 120), (0, -120)):
                    q = yer_bul(p[0] + dx, p[1] + dy, 28, oda, 60)
                    if q and egim_ok(*q, adim=40):
                        p = q
                        break
            if not p:
                raise SystemExit('SPAWNER YERI YOK: %s %s %s' % (c, x, y))
            z = (BZ + 4) if oda else (zz(*p, ust=4))
        else:
            p = (x, y)
        kv = {k: v for k, v in kv.items() if v is not None}
        kv.setdefault('angles', (0, aci, 0))
        say[c] = say.get(c, 0) + 1
        return H.ent(c, origin=(round(p[0]), round(p[1]), round(z, 1)), **kv)
    # KOY (15): pencereler, cati, avlu
    n = 0
    for (x, y, z, oda) in PEN[:7]:
        sp(ALMAN[n % 5] if n else 'actor_axis_afrikakorp_officer_mp40', x, y, oda, 90, targetname='koy', script_aigroup='koy', spawnflags=1, count=1)
        n += 1
    for (x, y, yaw) in CATI[:3]:
        sp(ALMAN[n % 5], round(x), round(y), None, yaw, z=CZ + 4, targetname='koy', script_aigroup='koy', script_noteworthy='cati', spawnflags=1, count=1)
        n += 1
    for (x, y) in ((-150, -480), (180, 600), (-560, -120), (560, 120), (0, 140)):
        sp(ALMAN[n % 6], x, y, None, 90, targetname='koy', script_aigroup='koy', spawnflags=1, count=1)
        n += 1
    assert n == 15
    # DALGA: tepelerin arkasi (K, G, B), gorus disi; GSC 30 sn'de bir 10'ar kullanir
    DALGA = []
    for (x, y) in ((-1800, 4300), (200, 4500), (2200, 4100), (-3600, 3800), (-4900, 1200), (-5000, -1000),
                   (-4400, -3200), (-1800, -4400), (600, -4500), (2400, -4200), (3900, 3200), (-3000, 4300)):
        p = yer_bul(x, y, 28, None, 400)
        if p and egim_ok(*p, adim=40):
            DALGA.append(p)
    assert len(DALGA) >= 9, DALGA
    for i, (x, y) in enumerate(DALGA):
        sp(ALMAN[i % 6], x, y, None, 0, targetname='dalga', spawnflags=1, count=1)
    # TANK PIYADESI (30): Panzer seritlerinin harita ici basi
    TP = 0
    for k, hat_ in enumerate(G.PANZER):
        for j, (dx, dy) in enumerate(((-200, 160), (-200, -160), (-380, 0), (-380, 200), (-380, -200), (-540, 90), (-540, -90), (-700, 0))):
            bx, by = hat_[5][0] - 100, hat_[5][1]
            p = yer_bul(bx + dx, by + dy, 28, None, 200)
            if p and G.icinde(*p):
                sp(ALMAN[(k + j) % 6], p[0], p[1], None, 0, targetname='tank_piyade', script_noteworthy=str(k + 1), spawnflags=1, count=1)
                TP += 1
    # INGILIZ TAKVIYESI (20): konvoy yolunun harita ici ucu (tepenin arkasi)
    IT = 0
    for j in range(15):
        p = yer_bul(4700 + (j % 5) * 90 - 180, -2150 + (j // 5) * 90 - 135, 26, None, 240)
        if p:
            sp(BRIT[j % len(BRIT)], p[0], p[1], None, 180, targetname='ingiliz', spawnflags=1, count=1)
            IT += 1
    assert IT == 15, IT

    # =====================================================================
    # 5. BETIK NOKTALARI
    # =====================================================================
    ent('script_origin', targetname='koy_orta', origin=(0, 0, ZK + 1))
    ent('script_origin', targetname='inis', origin=(KH[-1][0], KH[-1][1], zz(*KH[-1], ust=0)))
    for (x, y) in ((-150, -480), (180, 600), (-560, -120), (560, 120), (900, 0), (-900, -300), (0, 900), (0, -900)):
        p = yer_bul(x, y, 20, None, 120)
        if p:
            ent('script_origin', targetname='avlu_siper', origin=(p[0], p[1], zz(*p, ust=0)))
    # Panzer hedefleri: bina duvarlari ve avlu (atis noktalari)
    for (x, y, z) in ((-900, 500, BZ + 80), (-630, 300, BZ + 200), (-860, -600, BZ + 80), (-400, -500, BZ + 100),
                      (380, 500, BZ + 80), (380, -600, BZ + 80), (0, 0, ZK + 60), (-300, 250, ZK + 40)):
        ent('script_origin', targetname='tank_hedef', origin=(x, y, z))
    ent('script_origin', targetname='ust_hedef', origin=(-905, 560, G.UZ + 70))
    G.SAY = say
    print('pencere: %d, cati: %d, dalga noktasi: %d, tank piyadesi: %d' % (len(PEN), len(CATI), len(DALGA), TP))
    print('yerlesim:', ', '.join('%s %d' % kv for kv in sorted(say.items())))
