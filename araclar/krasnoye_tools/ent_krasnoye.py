# -*- coding: utf-8 -*-
"""
ent_krasnoye.py -- ASAMA 2: yerlesim. Butun anahtar adlari stok Sovyet
haritalarinin d3dbsp entity lump'indan olculdu:

  friendly_wave : trigger_multiple targetname "friendly_wave" -> target = ally
                  spawner'lar (spawnflags 1, target "player")       [cityhall]
  arac          : script_vehicle vehicletype/model/target/script_vehiclespawngroup
                  /script_vehicleride/script_team axis/script_turret  [moscow,
                  trainyard, tankhunt, downtown_assault]
  arac dugumu   : info_vehicle_node, ilki spawnflags 1 + speed + lookahead
  binen asker   : spawnflags 1, script_vehicleride N, target = inis sonrasi dugum
  zincir        : node -> target -> node ... (oyuncuya setfriendlychain ile)
  bolge         : script_aigroup -> waittill_aigroupcleared  [trainyard_obj]
"""
import math

def yerlestir(G):
    H, yuk = G.H, G.yukseklik
    YAP, AGAC = G.YAPILAR, G.AGAC
    PX0, PX1, PY0, PY1 = G.PX0, G.PX1, G.PY0, G.PY1
    TZ = G.TEMEL_Z
    say = {}

    DUGUM = []
    def ent(sinif, **kv):
        # ayni yere iki dugum: motor "Duplicate linking nodes" der (olculdu)
        if sinif.startswith('node_'):
            x, y = kv['origin'][0], kv['origin'][1]
            if any(abs(x - a) < 24 and abs(y - b) < 24 for (a, b) in DUGUM):
                if 'targetname' not in kv:
                    return None
                # adli dugum (zincir/hedef): silinemez, bos komsu yere kaydir
                # (olculen: koy_hedef_14 ve _15 ayni noktada -> "Duplicate linking nodes")
                for k in range(1, 12):
                    nx, ny = x + 40 * k, y
                    if not any(abs(nx - a) < 24 and abs(ny - b) < 24 for (a, b) in DUGUM):
                        kv['origin'] = (nx, ny, kv['origin'][2]); break
        if sinif.startswith('node_'):
            DUGUM.append((kv['origin'][0], kv['origin'][1]))
        say[sinif] = say.get(sinif, 0) + 1
        return H.ent(sinif, **kv)

    def tetik(sinif, x0, y0, z0, x1, y1, z1, **kv):
        bl = []
        H.kutu(x0, y0, z0, x1, y1, z1, 'trigger', 'trigger', alt='trigger', hedef=bl)
        say[sinif] = say.get(sinif, 0) + 1
        return H.ent(sinif, brushlar=bl, **kv)

    def zz(x, y, ust=8):
        return round(zemin(x, y) + ust, 1)

    # ---------------------------------------------------------------
    # BOSLUK DENETIMI (olculen: "Pathnode ... is in solid",
    # "bad node [9] in friendly chain at (600 200 8)" -> varil modeli)
    # ---------------------------------------------------------------
    MOD, CIT = G.MODELLER, G.CITLER
    MOD.append(('crate01_snow', -560, -122))     # bomba kasasi (asagida eklenir)
    for (dx, dy) in ((-70, 40), (0, 64), (70, 40)):  # MG yuvasi kum torbalari
        MOD.append(('military_sandbag', -450 + dx, 1050 + dy))
    def yaricap(m):
        for (on, r) in (('tree_destroyed_snow_fallen', 150), ('tree_destoyed', 70),
                        ('vehicle_', 170), ('caen_barbedwire', 100), ('prop_rubble', 70),
                        ('tree_', 44), ('military_hedgehog', 64), ('military_sandbag', 64),
                        ('haycart', 110), ('prop_haybale', 56), ('crate', 44), ('prop_crate', 44),
                        ('prop_barrel', 26), ('prop_firebarrel', 26), ('powerpole', 20),
                        ('furniture_bed', 70), ('furniture_long', 80), ('furniture', 40),
                        ('prop_potbelly', 34), ('prop_stove', 40), ('brush_', 0)):
            if m.startswith(on):
                return r
        return 36
    def seg_mes(px, py, xa, ya, xb, yb):
        dx, dy = xb - xa, yb - ya
        t = max(0.0, min(1.0, ((px - xa) * dx + (py - ya) * dy) / float(dx * dx + dy * dy)))
        return math.hypot(px - xa - dx * t, py - ya - dy * t)
    def serbest(x, y, r=26, ic=None):
        if x > 360 and y > 2340:            # barikatin dogusu: kapali alan
            return False
        for (m, mx, my) in MOD:
            rr = yaricap(m)
            if rr and abs(x - mx) < rr + r and abs(y - my) < rr + r and math.hypot(x - mx, y - my) < rr + r:
                return False
        for (xa, ya, xb, yb) in CIT:
            if seg_mes(x, y, xa, ya, xb, yb) < r + 8:
                return False
        for ad, (x0, y0, x1, y1, acik) in YAP.items():
            if x0 - r - 12 <= x <= x1 + r + 12 and y0 - r - 12 <= y <= y1 + r + 12:
                if ad == ic and acik and x0 + 16 + r <= x <= x1 - 16 - r and y0 + 16 + r <= y <= y1 - 16 - r:
                    continue
                return False
        return True
    def yer_bul(x, y, r=26, ic=None, en=200):
        if serbest(x, y, r, ic):
            return (x, y)
        for rad in range(16, en + 1, 16):
            n = max(8, int(rad / 8))
            for k in range(n):
                a = 2 * math.pi * k / n
                px, py = round(x + rad * math.cos(a)), round(y + rad * math.sin(a))
                if serbest(px, py, r, ic):
                    return (px, py)
        return None
    def zemin(x, y):
        """mesh 128'lik ucgenlerle aradeger alir: cevre 4 kosenin EN YUKSEGI."""
        A = 128
        i = math.floor((x - G.SX0) / A); j = math.floor((y - G.SY0) / A)
        k = [yuk(G.SX0 + (i + a) * A, G.SY0 + (j + b) * A) for a in (0, 1) for b in (0, 1)]
        ek = 3 if G.yol_mesafe(x, y) < 200 else 0
        return max(k + [yuk(x, y)]) + ek

    def bina_ici(x, y, pay=40):
        for ad, (x0, y0, x1, y1, acik) in YAP.items():
            if x0 - pay <= x <= x1 + pay and y0 - pay <= y <= y1 + pay:
                return ad
        return None

    def agac_yakin(x, y, r=56):
        return any(abs(x - ax) < r and abs(y - ay) < r for (ax, ay) in AGAC)

    # =====================================================================
    # 1. YOL DUGUMLERI
    # =====================================================================
    ADIM = 160
    for x in range(PX0 + 96, PX1 - 95, ADIM):
        for y in range(PY0 + 96, PY1 - 95, ADIM):
            if not serbest(x, y):
                continue
            if yuk(x, y) > 260:                 # dik kenar yamaclari
                continue
            ent('node_pathnode', origin=(x, y, zz(x, y)))
    # harita disi: Alman yolu koridoru (dalga ve kamyon piyadesi buradan gelir)
    for (px, py) in G.yol_ornek(160):
        if px >= PX0 + 96 or px < -3650:          # en bati uc: dik yamac, AI gitmez
            continue
        for w in (-120, 120):
            if serbest(px, py + w):
                ent('node_pathnode', origin=(round(px, 1), round(py + w, 1), zz(px, py + w)))
    # acik evler + ambar ici, kapi gecisleri
    for ad, (x0, y0, x1, y1, acik) in YAP.items():
        if not acik:
            continue
        zt = (8 if ad == 'ambar' else TZ) + 8
        for x in range(x0 + 56, x1 - 55, 96):
            for y in range(y0 + 56, y1 - 55, 96):
                if serbest(x, y, 26, ad):
                    ent('node_pathnode', origin=(x, y, zt))
    KAPILAR = {   # (x, y, ic yonu) -- gen_krasnoye'deki kapi merkezleri
        'ev1': [(-1100, 540, (0, 1))], 'ev3': [(-1158, -100, (-1, 0))],
        'ev4': [(742, 300, (1, 0))], 'depo': [(1650, 1778, (0, -1))],
        'ambar': [(-250, -374, (0, 1)), (-250, 74, (0, -1))],
    }
    for ad, kl in KAPILAR.items():
        zt = (8 if ad == 'ambar' else TZ) + 8
        for (x, y, (ix, iy)) in kl:
            p = yer_bul(x + ix * 56, y + iy * 56, 26, ad, 48)
            if p: ent('node_pathnode', origin=(p[0], p[1], zt))
            p = yer_bul(x - ix * 72, y - iy * 72, 26, None, 64)
            if p: ent('node_pathnode', origin=(p[0], p[1], zz(*p)))

    # =====================================================================
    # 2. SIPER DUGUMLERI
    # =====================================================================
    # savunma hatti (kum torbalarinin kuzeyi, guneye bakar)
    for x in list(range(-1300, -200, 112)) + list(range(260, 1400, 112)):
        p = yer_bul(x + 56, -800, 22, None, 48)
        if p: ent('node_cover_crouch', origin=(p[0], p[1], zz(*p)), angles=(0, 270, 0))
    # sovyet siperi
    for x in range(-860, 861, 112):
        p = yer_bul(x, 1800, 22, None, 48)
        if p: ent('node_cover_crouch', origin=(p[0], p[1], zz(*p)), angles=(0, 270, 0))
    # Alman koy savunmasi: acik evlerin pencere arkalari (disari bakar)
    PENCERE = {
        'ev1': [(-1260, 540, 270), (-940, 540, 270), (-1324, 700, 180)],
        'ev3': [(-1350, -276, 270), (-1350, 76, 90), (-1542, -100, 180)],
        'ev4': [(850, 140, 270), (1050, 140, 270), (950, 460, 90), (1158, 300, 0)],
        'ambar': [(-504, -374, 270), (4, -374, 270), (-504, 74, 90), (4, 74, 90)],
    }
    KOY_HEDEF = []
    for ad, pl in PENCERE.items():
        zt = (8 if ad == 'ambar' else TZ) + 8
        for (x, y, yaw) in pl:
            dx, dy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
            p = yer_bul(round(x - dx * 56), round(y - dy * 56), 34, ad, 80)
            if not p: continue
            nx, ny = p
            ent('node_cover_stand', origin=(nx, ny, zt), angles=(0, yaw, 0))
            KOY_HEDEF.append((nx, ny, zt, ad))
    # koy dis siperleri (cit, kuyu, araba arkasi) -- kuzeye bakar (Sovyet gelis yonu)
    for (x, y) in [(-1150, 360), (-800, 360), (300, 580), (40, 220), (-700, 120),
                   (1300, -260), (1500, -260), (560, 40),
                   (-1250, 1000), (-900, 950), (100, 1250), (450, 1200), (1100, 1300),
                   (1550, 700), (-1750, 150), (-1450, 250), (800, -20), (-150, 520),
                   (250, 450), (1200, 650)]:
        p = yer_bul(x, y)
        if not p: continue
        ent('node_cover_crouch', origin=(p[0], p[1], zz(*p)), angles=(0, 90, 0))
        KOY_HEDEF.append((p[0], p[1], zz(*p), None))
    # tarla siperleri (saldiran Almanlar icin, kuzeye bakar)
    TARLA = []
    for (x, y) in [(-1400, -1400), (-1250, -1420), (1350, -1820), (1200, -1800), (-650, -2100),
                   (750, -1400), (-2050, -1080), (-1900, -1060), (2000, -1260), (900, -2250),
                   (-1000, -1400), (-300, -2100), (1500, -1500), (-1700, -2300), (300, -1700)]:
        p = yer_bul(x, y)
        if not p: continue
        ent('node_cover_crouch', origin=(p[0], p[1], zz(*p)), angles=(0, 90, 0), targetname='tarla_siper')
        TARLA.append(p)

    # =====================================================================
    # 3. DOST ZINCIRLERI (fc1 siper, fc2 koy kuzeyi, fc3 meydan, fc4 savunma)
    # =====================================================================
    def zincir(ad, noktalar, yaw=270):
        noktalar = [yer_bul(x, y, 28, None, 240) for (x, y) in noktalar]
        noktalar = [p for p in noktalar if p]
        for i, (x, y) in enumerate(noktalar):
            kv = {'origin': (x, y, zz(x, y)), 'angles': (0, yaw, 0)}
            kv['targetname'] = ad if i == 0 else '%s_%d' % (ad, i)
            if i + 1 < len(noktalar):
                kv['target'] = '%s_%d' % (ad, i + 1)
            ent('node_pathnode', **kv)
    zincir('fc0', [(-420, 2520), (-260, 2500), (-100, 2480), (60, 2500), (200, 2520)])   # cemberden cikis
    zincir('fc1', [(-500, 1830), (-300, 1830), (-100, 1830), (100, 1830), (300, 1830), (500, 1830)])
    zincir('fc2', [(-1300, 1250), (-700, 1300), (-200, 1350), (400, 1350), (900, 1250), (1300, 1300)])
    zincir('fc3', [(-1000, 120), (-600, 200), (200, 250), (600, 200), (1200, 100), (1500, 400)])
    zincir('fc4', [(-1150, -780), (-750, -780), (-400, -780), (400, -780), (750, -780), (1150, -780)])

    # =====================================================================
    # 4. SOVYET EKIP + TAKVIYE
    # =====================================================================
    def sp(c, x, y, ic=None, ust=4, **kv):
        p = yer_bul(x, y, 28, ic, 200)
        if not p:
            print('UYARI: spawner yeri bulunamadi', c, x, y); return
        if ic == 'ambar':
            z = 8
        elif ic:
            z = TZ
        else:
            z = zemin(*p)
        kv = {k: v for k, v in kv.items() if v is not None}
        kv.setdefault('angles', (0, 270, 0))
        ent(c, origin=(p[0], p[1], round(z + ust, 1)), **kv)
    # demolition.d3dbsp'deki Leonov birebir: actor_ally_rus_commissar_ppsh,
    # "Lt. Leonov", spawnflags 7 (SPAWNER|FORCESPAWN|UNDELETABLE)
    sp('actor_ally_rus_commissar_ppsh', -200, 2700, targetname='leonov', spawnflags=7, count=1,
       script_friendname='Lt. Leonov')
    EKIP = ['actor_ally_rus_reg_ppsh', 'actor_ally_rus_reg_mosin', 'actor_ally_rus_reg_svt40',
            'actor_ally_rus_reg_ppsh', 'actor_ally_rus_reg_pps42', 'actor_ally_rus_reg_mosin']
    for i, c in enumerate(EKIP):
        x = -330 + i * 110 if i < 3 else 150 + (i - 3) * 110
        sp(c, x, 1900, targetname='ekip', spawnflags=1, count=1)
    TAKVIYE_C = ['actor_ally_rus_reg_ppsh', 'actor_ally_rus_reg_svt40', 'actor_ally_rus_reg_mosin',
                 'actor_ally_rus_reg_pps42']
    # kuzey sirtinin arkasi (oyuncu gorus disi)
    for i in range(4):
        x = -1700 + i * 380            # barikatin (x=420) BATISINDA
        sp(TAKVIYE_C[i], x, 3000, targetname='takviye_kuzey', target='player', spawnflags=1)
    # depo ici (kapisi kuzeye bakar, savunma hattindan gorulmez)
    for i, (x, y) in enumerate([(1560, 1610), (1650, 1610), (1740, 1610)]):
        sp(TAKVIYE_C[i], x, y, ic='depo', targetname='takviye_depo', target='player', spawnflags=1,
           angles=(0, 90, 0))
    # friendly_wave tetikleri: kuzey yari -> sirt arkasi, guney yari -> depo
    tetik('trigger_multiple', PX0 + 32, 300, -128, PX1 - 32, PY1 - 32, 1200,
          targetname='friendly_wave', target='takviye_kuzey')
    tetik('trigger_multiple', PX0 + 32, PY0 + 32, -128, PX1 - 32, 300, 1200,
          targetname='friendly_wave', target='takviye_kuzey')   # tek takviye noktasi

    # =====================================================================
    # 5. KOY SAVUNUCULARI (script_aigroup "koy")
    # =====================================================================
    KOY = [('actor_axis_snow_wehr_reg_kar98k', 'ev1', 0), ('actor_axis_snow_wehr_reg_mp40', 'ev1', 1),
           ('actor_axis_snow_wehr_reg_kar98k', 'ev1', 3), ('actor_axis_snow_wehr_reg_mp40', 'ev3', 4),
           ('actor_axis_snow_wehr_reg_kar98k', 'ev3', 5), ('actor_axis_snow_wehr_reg_mp40', 'ev4', 7),
           ('actor_axis_snow_wehr_reg_kar98k', 'ev4', 8), ('actor_axis_snow_wehr_officer_mp40', 'ev4', 9),
           ('actor_axis_snow_wehr_reg_mg42portable', 'ambar', 13), ('actor_axis_snow_wehr_reg_kar98k', 'ambar', 14),
           ('actor_axis_snow_wehr_reg_kar98k', 'dis', 15), ('actor_axis_snow_wehr_reg_mp40', 'dis', 16),
           ('actor_axis_snow_wehr_reg_kar98k', 'dis', 17), ('actor_axis_snow_wehr_reg_mp40', 'dis', 18),
           ('actor_axis_snow_wehr_reg_kar98k', 'dis', 19), ('actor_axis_snow_wehr_reg_mp40', 'dis', 21),
           ('actor_axis_snow_wehr_reg_kar98k', 'dis', 22), ('actor_axis_snow_wehr_reg_mp40', 'dis', 23),
           ('actor_axis_snow_wehr_reg_G43', 'dis', 24), ('actor_axis_snow_wehr_reg_kar98k', 'dis', 25),
           ('actor_axis_snow_wehr_reg_mp40', 'dis', 26), ('actor_axis_snow_wehr_reg_kar98k', 'dis', 27),
           ('actor_axis_snow_wehr_reg_mp40', 'dis', 28), ('actor_axis_snow_wehr_reg_G43', 'dis', 29),
           ('actor_axis_snow_wehr_reg_kar98k', 'dis', 30), ('actor_axis_snow_wehr_officer_mp40', 'dis', 31)]
    # MG42 yuvasi (koyun kuzey agzi, kuzeye bakar). Stok kural (_spawner.gsc
    # mg42setup_gun): mg42portable spawner'in target'i misc_turret OLMALI.
    MGX, MGY = -450, 1050
    MGZ = zemin(MGX, MGY)
    for (dx, dy, yaw) in ((-70, 40, 90), (0, 64, 0), (70, 40, 90)):
        H.ent('misc_model', model='xmodel/military_sandbag_snow_longsection',
              origin=(MGX + dx, MGY + dy, round(MGZ, 1)), angles=(0, yaw, 0))
    ent('misc_turret', targetname='koy_mg', model='xmodel/weapon_mg42', weaponinfo='mg42_bipod_duck',
        origin=(MGX, MGY + 30, round(MGZ + 2, 1)), angles=(0, 90, 0), leftarc=50, rightarc=50)
    for i, (c, yer, h) in enumerate(KOY):
        if 'mg42portable' in c:
            sp(c, MGX, MGY - 60, targetname='koy_alman', script_aigroup='koy', spawnflags=1,
               count=1, target='koy_mg', angles=(0, 90, 0))
            continue
        hx, hy, hz, hic = KOY_HEDEF[h % len(KOY_HEDEF)]
        tn = 'koy_hedef_%d' % i
        # her spawner kendi siper dugumunde doğar ve oraya baglidir
        p = yer_bul(hx + 36, hy, 24, hic, 120)
        if p:
            ent('node_pathnode', origin=(p[0], p[1], hz), targetname=tn)
        sp(c, hx - 36, hy, ic=hic, targetname='koy_alman', script_aigroup='koy', spawnflags=1,
           count=1, target=tn if p else None)

    # =====================================================================
    # 6. ARACLAR (harita disi bati yolu)
    # =====================================================================
    P = list(reversed(G.YOL_HAT))           # bati (harita disi) -> koy
    def arac_yolu(ad, son, hiz, cikis=None, dongu=None):
        nok = P[:son + 1] + (cikis or []) + (dongu or [])
        ince = []
        for i in range(len(nok) - 1):
            (ax, ay), (bx, by) = nok[i], nok[i + 1]
            n = max(1, int(math.hypot(bx - ax, by - ay) // 260))
            for k in range(n):
                t = k / float(n); ince.append((ax + (bx - ax) * t, ay + (by - ay) * t))
        ince.append(nok[-1])
        dongu_bas = None
        if dongu:
            # dongunun ilk noktasina en yakin ince ornek
            dx, dy = dongu[0]
            dongu_bas = min(range(len(ince)), key=lambda k: math.hypot(ince[k][0] - dx, ince[k][1] - dy))
            ince.append(dongu[0])                       # donguyu kapat
        for i, (x, y) in enumerate(ince):
            kv = {'origin': (round(x, 1), round(y, 1), zz(x, y, 16)),
                  'targetname': ad if i == 0 else '%s_%d' % (ad, i)}
            if i + 1 < len(ince):
                kv['target'] = '%s_%d' % (ad, i + 1)
            elif dongu:
                kv['target'] = '%s_%d' % (ad, dongu_bas + 1)   # sonsuz devriye
            if i == 0:
                kv.update(spawnflags=1, speed=hiz, lookahead=1)
            if i == len(ince) - 3:
                kv['speed'] = max(4, hiz // 2)     # varisa dogru yavasla
            ent('info_vehicle_node', **kv)
        (x0, y0), (x1, y1) = ince[0], ince[1]
        return (x0, y0), round(math.degrees(math.atan2(y1 - y0, x1 - x0)), 1)

    def arac(ad, tip, model, grup, son, hiz, binen=None, ekstra=None, cikis=None, dongu=None):
        (x, y), yaw = arac_yolu(ad + '_yol', son, hiz, cikis, dongu)
        kv = dict(targetname=ad, target=ad + '_yol', vehicletype=tip, model=model,
                  script_vehiclespawngroup=grup, script_team='axis',
                  origin=(round(x, 1), round(y, 1), zz(x, y, 2)), angles=(0, yaw, 0))
        if binen is not None:
            kv['script_vehicleride'] = binen
        if ekstra:
            kv.update(ekstra)
        ent('script_vehicle', **kv)
        return (x, y)

    # P indeksleri: 0 (-3990,-1520) ... 4 (-1800,-1760) 5 (-1100,-1800) 6 (-500,-1560) 7 (-120,-1250) 8 (0,-900)
    # Her arac yoldan AYRI bir cep'e cekilip durur; arkadaki onune takilmaz.
    #   kamyon    : P[4]=(-1800,-1760) sonrasi yolun KUZEYINE cekilir
    #   yaripalet : P[5]=(-1100,-1800) sonrasi yolun GUNEYINE cekilir
    #   tank      : ana yoldan savunma hattina kadar (P[8]=(0,-900))
    k = arac('kamyon', 'blitz', 'xmodel/vehicle_opel_blitz_snow', 1, 4, 30, binen=1,
             cikis=[(-1950, -1700), (-1820, -1480)])   # yolun ~280 kuzeyi; direk/tel temiz
    y_ = arac('yaripalet', 'germanhalftrack', 'xmodel/vehicle_halftrack_mg_snow', 2, 5, 10, binen=2,
              cikis=[(-1350, -1880), (-1150, -2120), (-1040, -2030)])
    # ^ yolun ~240 GUNEYINDE durur (tank yolunu kapatmaz), burnu/MG kuzeydogu
    #   = kum torbalarina doner. Tum arac yollari engel olcumunden gecti.
    # Tank koyun icine girer ve ambarin cevresinde 5 noktalik DONGU devriyesi
    # atar (kullanici). Noktalar evlere/kuyuya/citlere en az ~150 birim acik.
    # Eski dongu ahir ile kuyu arasindaki ~90 birimlik araliktan geciyordu
    # (tank ahirin/kum torbalarinin icinden geciyordu -- kullanici). Yeni
    # dongu ahirin GUNEYI ile kum torbasi hatti arasindaki acik bantta;
    # tank govdesi 110 birim yaricapla bina/kum torbasi/cit olcumu temiz.
    TANK_DONGU = [(0, -640), (450, -640), (250, -560), (-500, -570), (-950, -660)]
    # Stok _vehicle.gsc vehicle_paths_setup yolu SONUNA kadar yurur; kapali
    # halka sonsuz dongu -> "exceeded maximum number of script variables"
    # (olculdu). Bu yuzden: ana yol A'da biter, devriye AYRI ve ACIK uclu
    # zincir (A..E..A'); GSC her turda attachpath ile basa baglar.
    t_ = arac('tank', 'panzer2', 'xmodel/vehicle_panzer_ii_winter', 3, 7, 6,
              ekstra={'script_turret': 1},
              cikis=[(-60, -1330), (0, -1000), TANK_DONGU[0]])   # elektrik diregini ve torba boslugunu ortalar
    dz = TANK_DONGU + [TANK_DONGU[0]]
    ince = []
    for i in range(len(dz) - 1):
        (ax, ay), (bx, by) = dz[i], dz[i + 1]
        n = max(1, int(math.hypot(bx - ax, by - ay) // 200))
        for m in range(n):
            t = m / float(n); ince.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    ince.append(dz[-1])
    for i, (x, y) in enumerate(ince):
        kv = {'origin': (round(x, 1), round(y, 1), zz(x, y, 16)),
              'targetname': 'tank_dongu' if i == 0 else 'tank_dongu_%d' % i}
        if i + 1 < len(ince):
            kv['target'] = 'tank_dongu_%d' % (i + 1)
        if i == 0:
            kv.update(speed=3, lookahead=1)
        ent('info_vehicle_node', **kv)
    for i, (x, y) in enumerate(TANK_DONGU):        # GSC duraklama noktalari
        ent('script_origin', targetname='tank_durak', origin=(x, y, zz(x, y, 16)))
    # binen askerler (harita disinda, aracin yaninda bekler)
    for i in range(6):
        c = 'actor_axis_snow_wehr_reg_kar98k' if i % 2 else 'actor_axis_snow_wehr_reg_mp40'
        tx, ty = TARLA[i % len(TARLA)]
        sp(c, k[0] - 60 + (i % 3) * 48, k[1] + 180 + (i // 3) * 48, spawnflags=1, script_vehicleride=1,
           script_startingposition=i, targetname='kamyon_asker', script_aigroup='saldiri1',
           target='tarla_siper')
    for i in range(4):
        c = 'actor_axis_snow_wehr_reg_kar98k' if i % 2 else 'actor_axis_snow_wehr_reg_mp40'
        sp(c, y_[0] - 60 + i * 48, y_[1] + 260, spawnflags=1, script_vehicleride=2,
           script_startingposition=i, targetname='yaripalet_asker', script_aigroup='saldiri2',
           target='tarla_siper')
    # piyade dalga spawner'lari (harita disi, ormanda yol kenari)
    # Spawner'lar TAM yol koridoru dugumlerinin uzerinde (eskiden ormandaydi,
    # yol bulamayip dogdugu yerde kaliyordu -- kullanici).
    DALGA = []
    for (px, py) in G.yol_ornek(160):
        if -3650 <= px <= -2750:
            for w in (-90, 0, 90):
                # (-3333,-1970): g_connectpaths "in solid" olcumu (yamac)
                if serbest(px, py + w) and math.hypot(px + 3333, py + w + 1970) > 40:
                    DALGA.append((round(px, 1), round(py + w, 1)))
    assert len(DALGA) >= 12, len(DALGA)
    # her dalga 5 spawner; GSC her partide bunlari count=1 ile yeniden kullanir
    # tank dalgasi ayni anda 12 asker dogurur -> 12 spawner (kullanici)
    for d in (1, 2, 3):
        for i, (x, y) in enumerate(DALGA[:12 if d == 3 else 5]):
            c = ['actor_axis_snow_wehr_reg_kar98k', 'actor_axis_snow_wehr_reg_mp40',
                 'actor_axis_snow_wehr_reg_G43'][(i + d) % 3]
            sp(c, x, y, targetname='dalga%d' % d,
               spawnflags=1, count=1, angles=(0, 0, 0))
    # mg42portable asker MG'sini kurarken 'mg42_bipod_stand' tareti dogurur;
    # motor: "cannot spawn turret ... unless one instance placed in map"
    # (kullanici hatasi). Stok cozum: haritada bir ornek -- oyun alani disinda.
    ent('misc_turret', model='xmodel/weapon_mg42', weaponinfo='mg42_bipod_stand',
        origin=(-3800, -2350, zz(-3800, -2350, 0)), angles=(0, 0, 0))

    # =====================================================================
    # 7. YAPISKAN BOMBA (tankhunt kalibi)
    # =====================================================================
    for i in range(3):                       # tank_explosives bunlari tanka tasir
        tetik('trigger_use', 3400 + i * 64, 4300, 1800, 3432 + i * 64, 4332, 1832, targetname='sticky_trigger')
    bx, by = -560, -120                      # ambar ici, kasalarin yaninda
    # stok newvillers: ust uste crate01 z farki 26 -> kasa ustu = 8 + 26
    tetik('trigger_use', bx - 40, by - 42, 8, bx + 40, by + 38, 80, targetname='yapiskan_al')
    ent('script_model', model='xmodel/weapon_stickybomb_obj', targetname='yapiskan_model',
        origin=(bx, by - 2, 35), angles=(0, 30, 0))
    ent('misc_model', model='xmodel/crate01_snow', origin=(bx, by - 2, 8), angles=(0, 0, 0))

    print('yerlesim:', ', '.join('%s %d' % kv for kv in sorted(say.items())))
