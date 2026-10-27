# -*- coding: utf-8 -*-
"""
ent_sidirezegh.py -- yerlesim: yol dugumleri (meydan ~72, karargah ici iki kat), siperler,
pencere noktalari (zemin + ust kat), Price + 6 Ingiliz, dalga spawner'lari (K/D/G yollarinin
harita ici basi, tumsek arkasi), yari paletli (D), Panzer II (G), Ingiliz kurtarma kamyonlari (B),
betik noktalari.
SAYILAR (kullanici): dalga 1 = 12 | dalga 2 = 18 + yari paletli | dalga 3 = 24 + Panzer II
(panzerschreck ile) | Price + 6.
"""
import math

YARICAP = (('tree_desertpalm', 40), ('tree_desertbushy', 40), ('vehicle_', 190), ('haycart', 100), ('military_sandbag', 110),
           ('egypt_prop_well', 70), ('prop_crate', 36), ('prop_barrel', 22), ('furniture_northafrica_longtable', 60),
           ('furniture_northafrica_armoire', 50), ('furniture_northafrica', 30), ('egypt_prop_vase', 18), ('brush_', 0))

def yerlestir(G):
    H, yuk = G.H, G.yukseklik
    say = {}
    ZK, BZ, UZ = G.ZK, G.BZ, G.UZ
    KX0, KY0, KX1, KY1 = G.KX0, G.KY0, G.KX1, G.KY1
    DUGUM = []

    def ent(sinif, **kv):
        if sinif.startswith('node_'):
            x, y, z = kv['origin']
            if any(abs(x - a) < 36 and abs(y - b) < 36 and abs(z - c) < 60 for (a, b, c) in DUGUM):
                return None
            DUGUM.append(kv['origin'])
        say[sinif] = say.get(sinif, 0) + 1
        return H.ent(sinif, **kv)

    def yaricap(m):
        for (on, r) in YARICAP:
            if m.startswith(on):
                return r
        return 30

    def meydanda(x, y):
        return abs(x) < G.MY - 10 and abs(y) < G.MY - 10

    def zz(x, y, ust=8):
        if meydanda(x, y):
            return round(ZK + ust, 1)
        return round(yuk(x, y) + ust, 1)

    def kat_serbest(x, y, r, kat):
        if not (KX0 + 16 + r <= x <= KX1 - 16 - r and KY0 + 16 + r <= y <= KY1 - 16 - r):
            return False
        mx0, my0, mx1, my1 = G.MD
        if mx0 - r - 8 <= x <= mx1 + r + 8 and my0 - r - 30 <= y <= my1 + r + 8:
            return False                                  # merdiven/bosluk
        esya = G.EV_ESYA if kat == 0 else G.UST_ESYA
        for (m, mx, my, _yaw) in esya:
            if math.hypot(x - mx, y - my) < yaricap(m) + r:
                return False
        return True

    def serbest(x, y, r=26, kat=None):
        if kat is not None:
            return kat_serbest(x, y, r, kat)
        if not G.icinde(x, y) and G.giris_mes(x, y) > 200:
            return False
        for ad, v in G.YAPILAR.items():
            if v[0] - r - 14 <= x <= v[2] + r + 14 and v[1] - r - 14 <= y <= v[3] + r + 14:
                return False
        for (m, mx, my) in G.MODELLER:
            rr = yaricap(m)
            if rr and math.hypot(x - mx, y - my) < rr + r:
                return False
        for (kx, ky, kr) in G.KAYALAR:
            if math.hypot(x - kx, y - ky) < kr + r + 10:
                return False
        return True

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
        if meydanda(x, y):
            return True
        z = yuk(x, y)
        return all(abs(yuk(x + dx, y + dy) - z) < 55 for (dx, dy) in ((adim, 0), (-adim, 0), (0, adim), (0, -adim)))

    # =====================================================================
    # 1. PENCERELER (savunma noktalari) -- zemin ve ust kat
    # =====================================================================
    PEN = []
    def pencere(kat, x, y, yaw):
        z = (BZ if kat == 0 else UZ) + 4
        q = yer_bul(x, y, 16, kat, 60)
        if q:
            ent('script_origin', targetname='pencere', script_noteworthy=str(kat), origin=(q[0], q[1], z), angles=(0, yaw, 0))
            ent('node_cover_crouch_window' if False else 'node_cover_stand', origin=(q[0], q[1], z + 4), angles=(0, yaw, 0))
            PEN.append((q[0], q[1], z, kat, yaw))
    d = 16 + 26
    for x in (-190, 190):
        pencere(0, x, KY0 + d, 270)
    for x in (-40, -200):
        pencere(0, x, KY1 - d, 90)
    for y in (-130, 110):
        pencere(0, KX1 - d, y, 0)
    pencere(0, KX0 + d + 90, 160, 180)
    for x in (-190, 0, 190):
        pencere(1, x, KY0 + d, 270)
        pencere(1, x, KY1 - d, 90)
    for y in (-130, 0, 130):
        pencere(1, KX1 - d, y, 0)
    for y in (-110, 120):
        pencere(1, KX0 + d + 90, y, 180)

    # =====================================================================
    # 2. YOL DUGUMLERI
    # =====================================================================
    # meydan: siki (IW newvillers medyan 53; burada 72)
    for x in range(-1368, 1369, 72):
        for y in range(-1368, 1369, 72):
            if serbest(x, y, 22):
                ent('node_pathnode', origin=(x, y, zz(x, y)))
    # karargah ici: iki kat
    for kat, z in ((0, BZ + 8), (1, UZ + 8)):
        for x in range(KX0 + 48, KX1 - 47, 64):
            for y in range(KY0 + 48, KY1 - 47, 64):
                if serbest(x, y, 18, kat):
                    ent('node_pathnode', origin=(x, y, z))
    # merdiven: 12 basamak x ~12 birim (gorunmez rampa yok); dugumler basamak ustlerinde
    mx0, my0, mx1, my1 = G.MD
    xm = (mx0 + mx1) / 2.0
    NB = G.NB
    run = (my1 - my0) / float(NB)
    rise = (UZ - BZ) / float(NB)
    ent('node_pathnode', origin=(round(xm), round(my0 - run - 40), BZ + 8))         # onden giris
    for k in range(0, 5):                                                             # rampa ustu
        yy = my0 + 14 + ((my1 - run) - (my0 + 14)) * k / 4.0
        zt = BZ + rise + (UZ - BZ - rise) * (yy - my0) / float((my1 - run) - my0)
        ent('node_pathnode', origin=(round(xm), round(yy), round(zt + 8, 1)), targetname='merdiven_%d' % k)
    ent('node_pathnode', origin=(round(xm), my1 + 36, UZ + 8))
    # kapilar kapali (kullanici): yalniz ic dugum
    for (x, y, dy) in ((0, KY0, -1), (150, KY1, 1)):
        ent('node_pathnode', origin=(x, y - dy * 48, BZ + 8))
    # dis: acik col (seyrek), yollar boyu
    for x in range(-4500, 4501, 75):
        for y in range(-4700, 4701, 75):
            if meydanda(x, y):
                continue
            km = G.meydan_mes(x, y)
            adim = 150 if km < 1200 else 225
            if x % adim or y % adim:
                continue
            if not G.icinde(x, y) or not serbest(x, y) or not egim_ok(x, y):
                continue
            ent('node_pathnode', origin=(x, y, zz(x, y)))
    for ad, (hat, gen) in G.YOLLAR.items():
        L = G.hat_uzunluk(hat)
        m = 0.0
        while m <= L:
            (ax, ay) = G.hat_nokta(hat, m)
            (bx, by) = G.hat_nokta(hat, min(L, m + 20))
            d = math.hypot(bx - ax, by - ay) or 1
            ux, uy = (bx - ax) / d, (by - ay) / d
            for yan in (-150, 0, 150):
                x, y = round(ax - uy * yan), round(ay + ux * yan)
                if G.icinde(x, y) and not meydanda(x, y) and serbest(x, y, 20) and egim_ok(x, y, 60):
                    ent('node_pathnode', origin=(x, y, zz(x, y)))
            m += 150
    # siperler: karargah koseleri, kum torbalari, sandiklar, pazar
    for (x, y, yaw) in ((KX0 - 50, KY0 - 50, 225), (KX1 + 50, KY0 - 50, 315), (KX0 - 50, KY1 + 50, 135), (KX1 + 50, KY1 + 50, 45)):
        p = yer_bul(x, y, 24, None, 80)
        if p:
            ent('node_cover_crouch', origin=(p[0], p[1], zz(*p)), angles=(0, yaw, 0))
    for (m, mx, my) in G.MODELLER:
        if m.startswith(('military_sandbag', 'prop_crate', 'egypt_prop_well', 'vehicle_', 'haycart')) and meydanda(mx, my):
            for (dx, dy) in ((0, 90), (0, -90), (90, 0), (-90, 0)):
                p = yer_bul(mx + dx, my + dy, 22, None, 60)
                if p:
                    ent('node_cover_crouch', origin=(p[0], p[1], zz(*p)), angles=(0, round(math.degrees(math.atan2(-dy, -dx))) % 360, 0))

    # =====================================================================
    # 3. ARACLAR
    # =====================================================================
    def arac_z(x, y):
        return round(yuk(x, y) + 16, 1) if not meydanda(x, y) else round(ZK + 17, 1)
    ARAC_YOL = {}
    def yumusat(nokta, tur=3):
        # kullanici: araclar x-isini gibi donmesin -> koseler Chaikin ile yuvarlanir
        for _ in range(tur):
            y = [nokta[0]]
            for (a, b) in zip(nokta, nokta[1:]):
                y.append((a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25))
                y.append((a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75))
            y.append(nokta[-1])
            nokta = y
        out = [nokta[0]]                                   # 120'den sik dugum olmasin
        for q in nokta[1:-1]:
            if math.hypot(q[0] - out[-1][0], q[1] - out[-1][1]) >= 220:
                out.append(q)
        return out + [nokta[-1]]
    def arac(ad, grup, nokta, hiz, tur, model, binen=None, yerler=(), takim='axis', halka=None, duraklar=()):
        nokta = yumusat(nokta)
        n_gir = len(nokta)
        if halka:
            nokta = nokta + halka
        ARAC_YOL[ad] = list(nokta)
        for i, (x, y) in enumerate(nokta):
            kv = {'origin': (round(x, 1), round(y, 1), arac_z(x, y)),
                  'targetname': ad + '_yol' if i == 0 else '%s_yol_%d' % (ad, i)}
            if i + 1 < len(nokta):
                kv['target'] = '%s_yol_%d' % (ad, i + 1)
            if halka and i == n_gir:
                kv['targetname'] = '%s_halka' % ad                 # GSC halkayi buradan izler
                kv['speed'] = 6
            if i == 0:
                kv.update(spawnflags=1, speed=hiz, lookahead=1)
            if not halka and i == len(nokta) - 3:
                kv['speed'] = max(5, hiz // 2)
            if halka and i + 1 == n_gir:
                kv['target'] = '%s_halka' % ad
            H.ent('info_vehicle_node', **kv)
        (x0, y0), (x1, y1) = nokta[0], nokta[1]
        yaw = round(math.degrees(math.atan2(y1 - y0, x1 - x0)), 1)
        ek = {'script_turret': 0} if takim == 'axis' else {}
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
                      targetname=ad + '_asker', script_vehicleride=binen, script_startingposition=yer, spawnflags=1, count=1)
            kv.update(ekstra)
            H.ent(c, **kv)
    def yol_sonu(hat, durak):
        """yolun harita disi basindan meydan agzindaki durak noktasina (ters yon)."""
        ters = list(reversed(hat))
        L = G.hat_uzunluk(ters)
        tam = G.hat_kes(ters, 0, L)
        r = math.hypot(*durak)
        out = []
        for p in tam:
            if math.hypot(p[0], p[1]) < r:
                a = out[-1]
                ra, rp = math.hypot(*a), math.hypot(*p)
                t = (ra - r) / (ra - rp)
                out.append((a[0] + (p[0] - a[0]) * t, a[1] + (p[1] - a[1]) * t))
                return out
            out.append(p)
        return out
    ALMAN = ['actor_axis_afrikakorp_reg_kar98', 'actor_axis_afrikakorp_reg_mp40', 'actor_axis_afrikakorp_reg_kar98',
             'actor_axis_afrikakorp_reg_g43', 'actor_axis_afrikakorp_reg_mp40', 'actor_axis_afrikakorp_reg_kar98']
    # kullanici: 60 Alman + 2 yari paletli + 1 kamyon + Panzer; araclar kapi agzinin disinda durur,
    # harita disi kanyonlarda dogar (gorus disi)
    # stok _truck / _halftrack: 9 yer (0 = surucu); kullanici: kac kisi binebiliyorsa o kadar
    yer = [(i, ALMAN[i % 6], {}) for i in range(9)]
    arac('alman_kamyon', 5, yol_sonu(G.YOL_K, (0, 1850)), 20, 'blitz', 'xmodel/vehicle_opel_blitz_desert', binen=5, yerler=yer)
    yer = [(i, ALMAN[(i + 1) % 6], {}) for i in range(9)]
    arac('yarim', 1, yol_sonu(G.YOL_D, (1050, 0)), 12, 'germanhalftrack', 'xmodel/vehicle_halftrack_mg_desert', binen=1, yerler=yer)
    yer = [(i, ALMAN[(i + 2) % 6], {}) for i in range(9)]
    arac('yarim2', 6, yol_sonu(G.YOL_D, (2400, 0)) + [(2150, 120), (1900, 120), (1640, 110)], 12, 'germanhalftrack', 'xmodel/vehicle_halftrack_mg_desert', binen=6, yerler=yer)
    # Panzer: guney kapisindan girer, karargahin cevresinde donguyle tur atar (kullanici), her dugumde 5 sn
    HALKA = [(round(580 * math.cos(math.radians(a))), round(500 * math.sin(math.radians(a)))) for a in range(270, 270 - 360, -20)]   # ev ile pazar/kuyu arasi elips
    arac('panzer', 2, yol_sonu(G.YOL_G, (0, 1300)) + [(0, -760)], 8, 'panzer2', 'xmodel/vehicle_panzer_ii', halka=(HALKA[1:] + HALKA) * 5)        # stok _vehicle dongulu yolu kaldirmaz (olculdu): 5 tur acik
    BRIT = ['actor_ally_brit_africa_reg_rifle', 'actor_ally_brit_africa_reg_thompson', 'actor_ally_brit_africa_reg_bren',
            'actor_ally_brit_africa_reg_sten', 'actor_ally_brit_africa_reg_rifle', 'actor_ally_brit_africa_reg_thompson']
    # final: Ingiliz kamyonu batidan kapidan girer, karargahin guney kapisi onunde kasasi kapiya donuk durur
    # durak (0,-880) GSC'de setspeed(0) ile; sonra donup bati kapisindan harita disina (resumespeed)
    # cikis: guney kapisindan duz, guney yolu boyunca harita disina (bina yok)
    _gir = yol_sonu(G.YOL_B, (1400, 0))
    _cik = list(reversed(yol_sonu(G.YOL_G, (0, 1300))))
    yol = _gir + [(-950, -200), (-640, -560), (-280, -760), (0, -830), (0, -880), (0, -1100)] + _cik[1:]   # Panzer halkasindaki enkazdan uzak (kullanici: enkaz kalsin)
    arac('kurtarma', 3, yol, 12, 'blitz', 'xmodel/vehicle_opel_blitz_desert', takim='allies', binen=3,
         yerler=[(i, BRIT[i % 6], {}) for i in range(6)])   # kullanici: sofor + kasada 5 Ingiliz
    # kullanici: kamyon geldikten 5 sn sonra 3 sn arayla 5 Crusader, harita disindan yollarla gelir:
    # 1 koyun icine (bati kapisi), 2 kuzeyde yol kenari, 3 yari paletlilerin geldigi dogu yolu,
    # 4 Alman kamyonunun arkasi (kuzey yolu), 5 Panzer'in geldigi guney yolu (kenarda: final kamyonu cikar)
    def yan_cek(yol, yan, ileri=160):
        (ax, ay), (bx, by) = yol[-2], yol[-1]
        d = math.hypot(bx - ax, by - ay) or 1
        ux, uy = (bx - ax) / d, (by - ay) / d
        return yol + [(bx + ux * ileri - uy * yan, by + uy * ileri + ux * yan)]
    CRUS = [yol_sonu(G.YOL_B, (1400, 0)) + [(-1380, 260), (-1250, 620)],
            yan_cek(yol_sonu(G.YOL_K, (0, 2800)), 380),
            yol_sonu(G.YOL_D, (2650, 0)),
            yol_sonu(G.YOL_K, (0, 2250)),
            yan_cek(yol_sonu(G.YOL_G, (0, 2450)), 300, -60)]
    for k_, yol_c in enumerate(CRUS):
        arac('crusader%d' % (k_ + 1), 7 + k_, yol_c, 18, 'crusader', 'xmodel/vehicle_crusader2', takim='allies')
    # CARPISMA DENETIMI (kullanici: arac hicbir seyle ic ice girmesin): yol boyunca 20'de bir ornek
    sorun = []
    def _seg(a_, b_):
        L_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
        n_ = max(1, int(L_ / 20))
        return [(a_[0] + (b_[0] - a_[0]) * t / n_, a_[1] + (b_[1] - a_[1]) * t / n_) for t in range(n_ + 1)]
    for ad_, yol_ in ARAC_YOL.items():
        if ad_ == 'panzer':
            yol_ = yol_[:len(yol_) - 18 * 4]                # tekrar eden halka turlarini bir kez denetle
        for a_, b_ in zip(yol_, yol_[1:]):
            for (qx, qy) in _seg(a_, b_):
                if math.hypot(qx, qy) > 1500 and not ad_.startswith('crusader'):
                    if abs(qx) > 1700 or abs(qy) > 1700:
                        continue                            # kasaba disi yol: binalar yok
                for (m_, mx_, my_) in G.MODELLER:
                    if m_.startswith(('tree_desertbushy', 'grass', 'bush')):
                        continue
                    if math.hypot(qx - mx_, qy - my_) < 110:
                        sorun.append((ad_, m_, round(mx_), round(my_)))
                for yad_, (x0_, y0_, x1_, y1_, _ic) in G.YAPILAR.items():
                    if x0_ - 80 < qx < x1_ + 80 and y0_ - 80 < qy < y1_ + 80:
                        if yad_.startswith('sur') or yad_.startswith('kule'):
                            continue                        # kapi acikliklarindan gecilir (engel sur icinde)
                        sorun.append((ad_, yad_, round(qx), round(qy)))
    # Crusader duraklari diger araclarin yolundan uzak mi
    for ad_, yol_ in ARAC_YOL.items():
        if not ad_.startswith('crusader'):
            continue
        cx_, cy_ = yol_[-1]
        for ad2, yol2 in ARAC_YOL.items():
            if ad2 != 'kurtarma':
                continue
            for a_, b_ in zip(yol2, yol2[1:]):
                for (qx, qy) in _seg(a_, b_):
                    if math.hypot(qx - cx_, qy - cy_) < 260:
                        sorun.append((ad_, 'yol:' + ad2, round(qx), round(qy)))
    for (qa, qb) in zip(ARAC_YOL['kurtarma'], ARAC_YOL['kurtarma'][1:]):
        for (qx, qy) in _seg(qa, qb):
            for (hx, hy) in HALKA:
                if math.hypot(qx - hx, qy - hy) < 230:
                    sorun.append(('kurtarma', 'panzer_enkaz_yeri', round(qx), round(qy)))
    sorun = sorted(set(sorun))
    print('ARAC CARPISMA: %d' % len(sorun))
    import collections
    g_ = collections.defaultdict(list)
    for s_ in sorun:
        g_[(s_[0], s_[1])].append((s_[2], s_[3]))
    for k_, v_ in sorted(g_.items()):
        xs = [q[0] for q in v_]; ys = [q[1] for q in v_]
        print('   ', k_, len(v_), 'x', min(xs), max(xs), 'y', min(ys), max(ys))
    _bt = []
    H.kutu(-90, -660, ZK, 90, -560, ZK + 120, 'trigger', 'trigger', alt='trigger', hedef=_bt)       # kasa arkasi (kuzey)
    H.ent('trigger_use', brushlar=_bt, targetname='kamyon_bin')

    # =====================================================================
    # 4. SPAWNER'LAR
    # =====================================================================
    def sp(c, x, y, kat=None, aci=90, z=None, **kv):
        if z is None:
            p = yer_bul(x, y, 28, kat, 220)
            if not p:
                raise SystemExit('SPAWNER YERI YOK: %s %s %s' % (c, x, y))
            z = ((BZ if kat == 0 else UZ) + 4) if kat is not None else zz(*p, ust=18)
        else:
            p = (x, y)
        kv = {k: v for k, v in kv.items() if v is not None}
        kv.setdefault('angles', (0, aci, 0))
        say[c] = say.get(c, 0) + 1
        return H.ent(c, origin=(round(p[0]), round(p[1]), round(z, 1)), **kv)
    # Price + 6: karargah ici (iki kat)
    sp('actor_ally_brit_africa_price', 60, -60, 0, 270, targetname='price', script_friendname='Cpt. Price', spawnflags=1, count=1)
    for i, (x, y, kat) in enumerate(((-150, -150, 0), (220, 60, 0), (60, 160, 0), (-150, -150, 1), (200, -40, 1), (-60, 150, 1))):
        sp(BRIT[i], x, y, kat, 90, targetname='ingiliz', script_noteworthy=str(kat), spawnflags=1, count=1)
    # DALGA: K / D / G yollarinin uzerinde, sehirden 2500-3600 uzakta (tumsek arkasi, gorus disi);
    # kullanici: dogduklari yerde sabit duruyorlardi -> yol koridorunun dugumlerine dogarlar
    for ad, hat in (('kuzey', G.YOL_K), ('dogu', G.YOL_D), ('guney', G.YOL_G)):
        L = G.hat_uzunluk(hat)
        n = 0
        m = 0.0
        while m <= L and n < 6:
            (x, y) = G.hat_nokta(hat, m)
            r = math.hypot(x, y)
            if 4000 <= r <= 5600 and G.icinde(x, y):
                for yan in ((-90, 90) if n < 5 else (0,)):
                    (bx, by) = G.hat_nokta(hat, min(L, m + 20))
                    d = math.hypot(bx - x, by - y) or 1
                    px, py = x - (by - y) / d * yan, y + (bx - x) / d * yan
                    p = yer_bul(px, py, 28, None, 120)
                    if p and egim_ok(*p, adim=40) and n < 6:
                        sp(ALMAN[n % 6], p[0], p[1], None, 0, targetname='dalga', script_noteworthy=ad, spawnflags=1, count=1)
                        n += 1
            m += 160
        if n < 4:
            raise SystemExit('DALGA YERI AZ %s %d' % (ad, n))

    # =====================================================================
    # 5. BETIK NOKTALARI
    # =====================================================================
    ent('script_origin', targetname='meydan', origin=(0, 0, ZK + 1))
    ent('script_origin', targetname='karargah', origin=(0, 0, BZ))
    for ad, (x, y) in (('kuzey', (0, 1500)), ('dogu', (1500, 0)), ('guney', (0, -1500)), ('bati', (-1500, 0))):
        ent('script_origin', targetname='agiz', script_noteworthy=ad, origin=(x, y, ZK + 1))
    for (x, y) in ((-600, -420), (600, -420), (650, 300), (-600, 350), (0, -650), (0, 650), (-900, -200), (900, 120)):
        p = yer_bul(x, y, 20, None, 120)
        if p:
            ent('script_origin', targetname='meydan_siper', origin=(p[0], p[1], zz(*p, ust=0)))
    x, y, z = G.PS_YER
    ent('script_origin', targetname='panzerschreck_yer', origin=(x, y, z), angles=(0, 90, 0))
    for (x, y, z) in ((0, KY0, BZ + 180), (-200, KY0, BZ + 60), (200, KY0, BZ + 200), (KX1, 0, BZ + 120), (0, -900, ZK + 40)):
        ent('script_origin', targetname='tank_hedef', origin=(x, y, z))
    ent('script_origin', targetname='kapi_tekme', origin=(18, KY0 + 16 + 34, BZ), angles=(0, 270, 0))
    G.SAY = say
    G.PEN = PEN
    print('pencere: %d' % len(PEN))
    print('yerlesim:', ', '.join('%s %d' % kv for kv in sorted(say.items())))
