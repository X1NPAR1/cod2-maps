# -*- coding: utf-8 -*-
"""
ses_kur.py -- Leonov seslendirmesi + muzik alias'lari.

Kullanici istegi: "sesler duygusuz/ruhsuz, daha profesyonel olsun, tonlama,
bagirma". Kaynak: CoD2'nin KENDI Sovyet seslendirmeleri (gercek seslendirme
sanatcilari, Rus aksanli Ingilizce). Leonov'un sesi = Tegmen Volsky
(downtown_assault / downtown_sniper / cityhall). Altyazi = ayni repligin
resmi (Turk yamasindaki) subtitle referansi -> ses ve yazi birebir uyar.

Stok alias'lar loadspec ile kendi bolumlerine kisitli (cityhall,
downtown_sniper...) -> krasnoye'de calmazlar. Bu yuzden AYNI wav'a isaret
eden yeni alias'lar loadspec 'krasnoye' ile tanimlanir.

Muzik (kullanici: "Sovyet 2. bolumun baslangic muzigi ve 1. bolumun sonundaki
muzik"): demolition.gsc music_tensionfragments -> soviet_tension_fragment01;
moscow.gsc end_main -> soviet_victory_light01 (iw_sound2.csv'den dosyalari).
"""
import csv, io, os, re, zipfile, glob

ANA = r'F:\Activision\Call of Duty 2\main'
HAM = r'F:\Activision\cod2_analiz\ham'

LEONOV = {   # krasnoye repligi -> stok alias
    'giris':           'downtownassault_volsky_movein',
    'ilerle':          'cityhall_vsk_wemusthold',
    'evler':           'downtownassault_volsky_clearapt1',
    'koy_temiz':       'cityhall_vsk_itsover',
    'savunma':         'downtownsniper_volsky_preparecounter',
    'kamyon':          'downtownsniper_volsky_startingattackloud',
    'yaripalet':       'downtownsniper_volsky_enemyhalftrackapp',
    'tank':            'downtownsniper_volsky_findantitank',
    'bomba_al':        'downtownassault_volsky_letsgo',
    'bomba_yapistir':  'downtownassault_volsky_fromtheside',
    'geri_cekiliyor':  'downtownsniper_volsky_enemyretreating',
    'zafer':           'cityhall_vsk_takenit',
}
ASKER = {    # Leonov disi, en yakin dost asker soyler
    'takviye':         'downtownsniper_rs1_reinforcementscoming1',
}
# tankhunt yanasma sahnesi + kapak sesi: stok alias'lar loadspec ile baska
# bolumlere kisitli -> "unknown sound alias" (kullanici hatasi). AYNI adla
# loadspec krasnoye kopyasi (stok da ayni adi bolum bolum tekrar tanimlar).
AYNI = ['commissar_charge_attack', 'commissar_charge_killfascists',
        'demolition_rs4_motherrussia', 'moscow_rs3_fireinthehole', 'tank_hatch',
        # demolition savunma acilisi: Alman "hurra" kalabaligi + komiser
        'walla_german_large', 'walla_german_large_layer', 'demolition_rs1_countingonus']
MUZIK = {
    'krasnoye_muzik_giris': 'soviet_tension_fragment01',
    'krasnoye_muzik_zafer': 'soviet_victory_light01',
    # bolum boyunca muzik (kullanici: "cok muziksiz"): stok demolition/
    # downtown_sniper/trainyard Sovyet parcalari
    'krasnoye_muzik_koy': 'soviet_charge01',              # koy baskini
    'krasnoye_muzik_hazirlik': 'soviet_tension_medium01', # savunmaya gecis
    'krasnoye_muzik_tank': 'soviet_cresc01',              # tanka tirmanis (tek sefer)
}
TEK_SEFER = ('krasnoye_muzik_giris', 'krasnoye_muzik_tank')
GOREV = [
    ('OBJ_KOY', "Krasnoye köyünü Almanlardan temizle."),
    ('OBJ_SAVUNMA', "Köyün güneyindeki savunma hattına geç."),
    ('OBJ_PUSKURT', "Alman karşı saldırısını püskürt."),
    ('OBJ_BOMBA', "Ambardaki yapışkan bombaları al."),
    ('OBJ_TANK', "Panzer II tankını yapışkan bombayla imha et."),
    ('BITTI', "Krasnoye savunuldu. Görev tamamlandı."),
    # tanitim ekrani (stok introscreen.str bicimi: ""Baslik"", yer, tarih, bilgi)
    ('INTRO_TITLE', '"Krasnoye Kolhozu"'),
    ('INTRO_PLACE', "Stalingrad Cephesi, S.S.C.B."),
    ('INTRO_DATE', "14 Aralık 1942"),
    ('INTRO_INFO', "Kalaç Yakınları, Saat 07:40"),
]

def tr(s):
    for a, b in (('ş', 's'), ('Ş', 'S'), ('ğ', 'g'), ('Ğ', 'G'), ('ı', 'i'), ('İ', 'I')):
        s = s.replace(a, b)
    return s

def alias_oku(dosya):
    rows = list(csv.reader(io.open(os.path.join(HAM, 'soundaliases', dosya), encoding='latin-1')))
    hdr, d = None, {}
    for r in rows:
        if not r or r[0].startswith('#'):
            continue
        if r[0] == 'name':
            hdr = r; continue
        if hdr and r[0] not in d:
            d[r[0]] = dict(zip(hdr, r))
    return hdr, d

def main():
    hdr, vo = alias_oku('iw_voiceovers2.csv')
    _, snd = alias_oku('iw_sound2.csv')
    satir = [','.join(hdr)]

    def ekle(yeni, kaynak, ek=None):
        a = dict(kaynak)
        a['name'] = yeni
        a['loadspec'] = 'krasnoye'
        if ek:
            a.update(ek)
        satir.append(','.join(a.get(k, '') for k in hdr))

    eksik = []
    for ad, src in list(LEONOV.items()) + list(ASKER.items()):
        if src not in vo:
            eksik.append(src); continue
        ekle('krasnoye_leonov_' + ad if ad in LEONOV else 'krasnoye_asker_' + ad, vo[src])
    for yeni, src in MUZIK.items():
        if src not in snd:
            eksik.append(src); continue
        # zafer muzigi dongude calar (kullanici)
        ekle(yeni, snd[src], None if yeni in TEK_SEFER else {'loop': 'looping'})
    _, req = alias_oku('iw_requests.csv')
    for ad in AYNI:
        kaynak = vo.get(ad) or snd.get(ad) or req.get(ad)
        if kaynak is None:
            eksik.append(ad); continue
        # hurra: kullanici "cok yuksek gelmedi" -> tam ses, uzaktan duyulur
        ekle(ad, kaynak, {'vol_min': '1', 'vol_max': '1', 'dist_min': '2000', 'dist_max': '12000'}
             if ad.startswith('walla') else None)
    if eksik:
        raise SystemExit('STOK ALIAS BULUNAMADI: %s' % eksik)

    # wav dosyalari gercekten iwd'de mi?
    var = set()
    for p in glob.glob(os.path.join(ANA, '*.iwd')):
        for n in zipfile.ZipFile(p).namelist():
            var.add(n.lower())
    for s in satir[1:]:
        f = s.split(',')[2]
        yol = ('sound/' + f).lower()
        print('%-34s %-58s %s' % (s.split(',')[0], f, 'OK' if yol in var else '!! YOK'))

    with open(os.path.join(ANA, 'soundaliases', 'krasnoye.csv'), 'w', encoding='latin-1', newline='\r\n') as f:
        f.write('\n'.join(satir) + '\n')

    o = ['VERSION             "1"', 'CONFIG              "C:\\trees\\cod2\\bin\\StringEd.cfg"',
         'FILENOTES           "krasnoye"', '']
    for ref, t in GOREV:
        o += ['REFERENCE           %s' % ref, 'LANG_ENGLISH        "%s"' % tr(t), '']
    o.append('ENDMARKER')
    with open(os.path.join(ANA, 'localizedstrings', 'krasnoye.str'), 'wb') as f:
        f.write('\r\n'.join(o).encode('cp1254') + b'\r\n')
    # artik kullanilmayan TTS wav'lari (Ostap) kaldir
    d = os.path.join(ANA, 'sound', 'voiceovers', 'krasnoye')
    if os.path.isdir(d):
        for x in os.listdir(d):
            os.remove(os.path.join(d, x))
        os.rmdir(d)
    print('alias: %d  gorev metni: %d' % (len(satir) - 1, len(GOREV)))

if __name__ == '__main__':
    main()
