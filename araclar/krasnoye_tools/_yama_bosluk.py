# tek seferlik yama: ent_krasnoye.py'ye bosluk denetimi
f = 'ent_krasnoye.py'
s = open(f, encoding='utf-8').read()

def R(a, b):
    global s
    assert a in s, ('BULUNAMADI', a[:70])
    s = s.replace(a, b)

yardim = '''
    # ---------------------------------------------------------------
    # BOSLUK DENETIMI (olculen: "Pathnode ... is in solid",
    # "bad node [9] in friendly chain at (600 200 8)" -> varil modeli)
    # ---------------------------------------------------------------
    MOD, CIT = G.MODELLER, G.CITLER
    def yaricap(m):
        for (on, r) in (('tree_', 44), ('military_hedgehog', 64), ('military_sandbag', 64),
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
'''
R("""    def zz(x, y, ust=8):
        return round(yuk(x, y) + ust, 1)
""", """    def zz(x, y, ust=8):
        return round(zemin(x, y) + ust, 1)
""" + yardim)
R("""            if bina_ici(x, y) or agac_yakin(x, y):
                continue""", """            if not serbest(x, y):
                continue""")
R("""        for w in (-120, 120):
            a = G.YOL_HAT
            ent('node_pathnode', origin=(round(px, 1), round(py + w, 1), zz(px, py + w)))""",
  """        for w in (-120, 120):
            if serbest(px, py + w):
                ent('node_pathnode', origin=(round(px, 1), round(py + w, 1), zz(px, py + w)))""")
R("""        for x in range(x0 + 56, x1 - 55, 96):
            for y in range(y0 + 56, y1 - 55, 96):
                ent('node_pathnode', origin=(x, y, zt))""",
  """        for x in range(x0 + 56, x1 - 55, 96):
            for y in range(y0 + 56, y1 - 55, 96):
                if serbest(x, y, 26, ad):
                    ent('node_pathnode', origin=(x, y, zt))""")
R("""        for (x, y, (ix, iy)) in kl:
            ent('node_pathnode', origin=(x + ix * 56, y + iy * 56, zt))
            ent('node_pathnode', origin=(x - ix * 72, y - iy * 72, zz(x - ix * 72, y - iy * 72)))""",
  """        for (x, y, (ix, iy)) in kl:
            p = yer_bul(x + ix * 56, y + iy * 56, 26, ad, 48)
            if p: ent('node_pathnode', origin=(p[0], p[1], zt))
            p = yer_bul(x - ix * 72, y - iy * 72, 26, None, 64)
            if p: ent('node_pathnode', origin=(p[0], p[1], zz(*p)))""")
R("""        ent('node_cover_crouch', origin=(x + 56, -812, zz(x + 56, -812)), angles=(0, 270, 0))""",
  """        p = yer_bul(x + 56, -800, 22, None, 48)
        if p: ent('node_cover_crouch', origin=(p[0], p[1], zz(*p)), angles=(0, 270, 0))""")
R("""        ent('node_cover_crouch', origin=(x, 1790, zz(x, 1790)), angles=(0, 270, 0))""",
  """        p = yer_bul(x, 1800, 22, None, 48)
        if p: ent('node_cover_crouch', origin=(p[0], p[1], zz(*p)), angles=(0, 270, 0))""")
R("""            nx, ny = round(x - dx * 40), round(y - dy * 40)
            ent('node_cover_stand', origin=(nx, ny, zt), angles=(0, yaw, 0))
            KOY_HEDEF.append((nx, ny, zt))""",
  """            p = yer_bul(round(x - dx * 48), round(y - dy * 48), 24, ad, 80)
            if not p: continue
            nx, ny = p
            ent('node_cover_stand', origin=(nx, ny, zt), angles=(0, yaw, 0))
            KOY_HEDEF.append((nx, ny, zt, ad))""")
R("""        ent('node_cover_crouch', origin=(x, y, zz(x, y)), angles=(0, 90, 0))
        KOY_HEDEF.append((x, y, zz(x, y)))""",
  """        p = yer_bul(x, y)
        if not p: continue
        ent('node_cover_crouch', origin=(p[0], p[1], zz(*p)), angles=(0, 90, 0))
        KOY_HEDEF.append((p[0], p[1], zz(*p), None))""")
R("""        ent('node_cover_crouch', origin=(x, y, zz(x, y)), angles=(0, 90, 0), targetname='tarla_siper')
        TARLA.append((x, y))""",
  """        p = yer_bul(x, y)
        if not p: continue
        ent('node_cover_crouch', origin=(p[0], p[1], zz(*p)), angles=(0, 90, 0), targetname='tarla_siper')
        TARLA.append(p)""")
R("""        for i, (x, y) in enumerate(noktalar):
            kv = {'origin': (x, y, zz(x, y)), 'angles': (0, yaw, 0)}""",
  """        noktalar = [yer_bul(x, y, 28, None, 240) for (x, y) in noktalar]
        noktalar = [p for p in noktalar if p]
        for i, (x, y) in enumerate(noktalar):
            kv = {'origin': (x, y, zz(x, y)), 'angles': (0, yaw, 0)}""")
R("""    ent('actor_ally_rus_commissar_ppsh', targetname='leonov', spawnflags=1, count=1,
        script_friendname='Lt. Leonov', origin=(60, 1830, zz(60, 1830, 0)), angles=(0, 270, 0))""",
  """    def sp(c, x, y, ic=None, ust=4, **kv):
        p = yer_bul(x, y, 28, ic, 200)
        if not p:
            print('UYARI: spawner yeri bulunamadi', c, x, y); return
        if ic == 'ambar':
            z = 8
        elif ic:
            z = TZ
        else:
            z = zemin(*p)
        kv.setdefault('angles', (0, 270, 0))
        ent(c, origin=(p[0], p[1], round(z + ust, 1)), **kv)
    sp('actor_ally_rus_commissar_ppsh', 60, 1880, targetname='leonov', spawnflags=1, count=1,
       script_friendname='Lt. Leonov')""")
R("""        ent(c, targetname='ekip', spawnflags=1, count=1, origin=(x, 1860, zz(x, 1860, 0)),
            angles=(0, 270, 0))""", """        sp(c, x, 1900, targetname='ekip', spawnflags=1, count=1)""")
R("""        ent(TAKVIYE_C[i], targetname='takviye_kuzey', target='player', spawnflags=1,
            origin=(x, 2900, zz(x, 2900, 0)), angles=(0, 270, 0))""",
  """        sp(TAKVIYE_C[i], x, 2900, targetname='takviye_kuzey', target='player', spawnflags=1)""")
R("""        ent(TAKVIYE_C[i], targetname='takviye_depo', target='player', spawnflags=1,
            origin=(x, y, TZ), angles=(0, 90, 0))""",
  """        sp(TAKVIYE_C[i], x, y, ic='depo', targetname='takviye_depo', target='player', spawnflags=1,
           angles=(0, 90, 0))""")
R("""        hx, hy, hz = KOY_HEDEF[min(h, len(KOY_HEDEF) - 1)]""",
  """        hx, hy, hz, hic = KOY_HEDEF[min(h, len(KOY_HEDEF) - 1)]""")
R("""        ent('node_pathnode', origin=(hx + 1, hy + 1, hz), targetname=tn)
        ent(c, targetname='koy_alman', script_aigroup='koy', spawnflags=1, count=1,
            target=tn, origin=(hx, hy, hz - 8), angles=(0, 270, 0))""",
  """        p = yer_bul(hx + 36, hy, 24, hic, 120)
        if p:
            ent('node_pathnode', origin=(p[0], p[1], hz), targetname=tn)
        sp(c, hx - 36, hy, ic=hic, targetname='koy_alman', script_aigroup='koy', spawnflags=1,
           count=1, target=tn if p else None)""")
R("""        ent(c, spawnflags=1, script_vehicleride=1, script_startingposition=i,
            targetname='kamyon_asker', script_aigroup='saldiri1', origin=(k[0] - 60 + (i % 3) * 40, k[1] - 140 - (i // 3) * 40, zz(k[0], k[1], 0)),
            target='tarla_siper')""",
  """        sp(c, k[0] - 60 + (i % 3) * 48, k[1] + 180 + (i // 3) * 48, spawnflags=1, script_vehicleride=1,
           script_startingposition=i, targetname='kamyon_asker', script_aigroup='saldiri1',
           target='tarla_siper')""")
R("""        ent(c, spawnflags=1, script_vehicleride=2, script_startingposition=i,
            targetname='yaripalet_asker', script_aigroup='saldiri2', origin=(y_[0] - 40 + i * 30, y_[1] + 160, zz(y_[0], y_[1], 0)),
            target='tarla_siper')""",
  """        sp(c, y_[0] - 60 + i * 48, y_[1] + 260, spawnflags=1, script_vehicleride=2,
           script_startingposition=i, targetname='yaripalet_asker', script_aigroup='saldiri2',
           target='tarla_siper')""")
R("""            ent(c, targetname='dalga%d' % d, script_aigroup='saldiri%d' % d, spawnflags=1, count=1, target='tarla_siper',
                origin=(x + d * 24, y + d * 24, zz(x, y, 0)), angles=(0, 0, 0))""",
  """            sp(c, x + d * 48, y + d * 48, targetname='dalga%d' % d, script_aigroup='saldiri%d' % d,
               spawnflags=1, count=1, target='tarla_siper', angles=(0, 0, 0))""")
R("""                  origin=(round(x, 1), round(y, 1), zz(x, y, 0)), angles=(0, yaw, 0))""",
  """                  origin=(round(x, 1), round(y, 1), zz(x, y, 2)), angles=(0, yaw, 0))""")
open(f, 'w', encoding='utf-8').write(s)
print('yama tamam')
