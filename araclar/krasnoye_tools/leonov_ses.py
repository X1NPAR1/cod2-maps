# -*- coding: utf-8 -*-
"""
leonov_ses.py -- Komutan Leonov'un repliklerini uretir.

  1) edge-tts, ru-RU-DmitryNeural: Ingilizce metni Rus sesi okur -> dogal Rus
     aksanli Ingilizce (kullanici secimi).
  2) miniaudio ile mp3 -> PCM.
  3) numpy ile: 22050 Hz mono 16-bit (stok VO bicimi, olculdu:
     Voiceovers/RU/Tankhunt/*.wav = PCM 1 kanal 22050 Hz 16 bit),
     hafif alcak-kesim + sicak orta frekans + yumusak kompresor +
     kisa dis mekan yankisi. Telsiz/robot efekti YOK.
  4) main/sound/voiceovers/krasnoye/*.wav, main/soundaliases/krasnoye.csv,
     main/localizedstrings/krasnoye.str (Turkce altyazi + gorev metinleri).

Turkce karakter kurali (olculdu): Turk yamasi CoD2 fontunda yalniz
c-cedilla/o-umlaut/u-umlaut kullaniyor; s-cedilla, g-breve, dotless i,
I-dot YOK -> s, g, i, I'ya cevrilir.
"""
import os, sys, asyncio, io, wave
import numpy as np

KOK = r'F:\Activision\Call of Duty 2\main'
SES_DIR = os.path.join(KOK, 'sound', 'voiceovers', 'krasnoye')
SES = 'uk-UA-OstapNeural'   # ru-RU-DmitryNeural serviste kapali (olculdu: NoAudioReceived)

REPLIK = [  # (ad, ingilizce, turkce altyazi)
    ('giris', "Comrades! The fascists have taken Krasnoye. We take it back. House by house. Forward!",
     "Yoldaşlar! Faşistler Krasnoye'yi aldı. Geri alacağız. Ev ev. İleri!"),
    ('ilerle', "Keep moving! Use the fences, stay low!",
     "Durmayın! Çitleri siper alın, eğilin!"),
    ('evler', "Clear the houses! Grenade through the window, then go in!",
     "Evleri temizleyin! Önce pencereden bomba, sonra içeri!"),
    ('koy_temiz', "The village is ours! But do not celebrate. They will come back.",
     "Köy bizim! Ama sevinmeyin. Geri gelecekler."),
    ('savunma', "Everyone to the south line! Behind the sandbags, quickly!",
     "Herkes güney hattına! Kum torbalarının arkasına, çabuk!"),
    ('kamyon', "Truck on the western road! Infantry, get ready!",
     "Batı yolunda kamyon! Piyade geliyor, hazır olun!"),
    ('yaripalet', "Halftrack! Keep your heads down and kill the gunner!",
     "Yarı paletli! Başınızı eğin, makineliyi kullananı vurun!"),
    ('tank', "Tank! A panzer is coming down the road!",
     "Tank! Bir Panzer yoldan geliyor!"),
    ('bomba_al', "Comrade! Sticky bombs in the barn. Get them, now!",
     "Yoldaş! Ambarda yapışkan bombalar var. Hemen al!"),
    ('bomba_yapistir', "Get close to the panzer and stick it on the engine!",
     "Panzere yaklaş ve bombayı motoruna yapıştır!"),
    ('takviye', "Reinforcements are here! Fill the gaps in the line!",
     "Takviye geldi! Hattaki boşlukları doldurun!"),
    ('geri_cekiliyor', "They are falling back! Stay sharp, they are not finished!",
     "Geri çekiliyorlar! Tetikte olun, daha bitmedi!"),
    ('zafer', "The panzer is burning! Krasnoye stands! Well done, comrades!",
     "Panzer yanıyor! Krasnoye ayakta! Aferin yoldaşlar!"),
]

GOREV = [
    ('OBJ_KOY', "Krasnoye köyünü Almanlardan temizle."),
    ('OBJ_SAVUNMA', "Köyün güneyindeki savunma hattına geç."),
    ('OBJ_PUSKURT', "Alman karşı saldırısını püskürt."),
    ('OBJ_BOMBA', "Ambardaki yapışkan bombaları al."),
    ('OBJ_TANK', "Panzer II tankını yapışkan bombayla imha et."),
    ('BITTI', "Krasnoye savunuldu. Görev tamamlandı."),
]

def tr(s):
    """CoD2 fontu: s/g/i donusumu, c/o/u korunur; cp1254 (Turk yamasi ile ayni)."""
    for a, b in (('ş', 's'), ('Ş', 'S'), ('ğ', 'g'), ('Ğ', 'G'), ('ı', 'i'), ('İ', 'I')):
        s = s.replace(a, b)
    return s

async def tts(metin, yol):
    import edge_tts
    c = edge_tts.Communicate(metin, SES, rate='-6%', pitch='-6Hz', volume='+0%')
    await c.save(yol)

def mp3_pcm(yol):
    import miniaudio
    d = miniaudio.decode_file(yol, output_format=miniaudio.SampleFormat.SIGNED16,
                              nchannels=1, sample_rate=22050)
    return np.frombuffer(d.samples, dtype=np.int16).astype(np.float32) / 32768.0

def bikuad(x, b, a):
    y = np.zeros_like(x); x1 = x2 = y1 = y2 = 0.0
    for i in range(len(x)):
        v = b[0] * x[i] + b[1] * x1 + b[2] * x2 - a[1] * y1 - a[2] * y2
        x2, x1, y2, y1 = x1, x[i], y1, v
        y[i] = v
    return y

def hp(fs, f, q=0.707):
    import math
    w = 2 * math.pi * f / fs; al = math.sin(w) / (2 * q); c = math.cos(w)
    b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]; a = [1 + al, -2 * c, 1 - al]
    return [v / a[0] for v in b], [1.0, a[1] / a[0], a[2] / a[0]]

def peak(fs, f, g_db, q=1.0):
    import math
    A = 10 ** (g_db / 40.0); w = 2 * math.pi * f / fs; al = math.sin(w) / (2 * q); c = math.cos(w)
    b = [1 + al * A, -2 * c, 1 - al * A]; a = [1 + al / A, -2 * c, 1 - al / A]
    return [v / a[0] for v in b], [1.0, a[1] / a[0], a[2] / a[0]]

def isle(x, fs=22050):
    x = bikuad(x, *hp(fs, 110))                    # bas gurultusu, mikrofon gumbu
    x = bikuad(x, *peak(fs, 260, 2.5, 0.9))        # gogus sesi, sicaklik
    x = bikuad(x, *peak(fs, 2600, 3.0, 1.2))       # ses netligi (kumanda tonu)
    # yumusak kompresor (RMS zarfi)
    zarf = np.sqrt(np.convolve(x * x, np.ones(441) / 441.0, mode='same') + 1e-9)
    esik = 0.10
    kazanc = np.where(zarf > esik, (esik + (zarf - esik) / 3.0) / zarf, 1.0)
    x = x * kazanc
    # kisa dis mekan yankisi (tek yansima + hafif kuyruk), %12
    y = x.copy()
    for gec, g in ((int(0.045 * fs), 0.12), (int(0.11 * fs), 0.06), (int(0.19 * fs), 0.03)):
        y[gec:] += g * x[:-gec]
    # sessizlik kirp + 120 ms bas/son pay
    i = np.where(np.abs(y) > 0.01)[0]
    if len(i):
        y = y[max(0, i[0] - int(0.05 * fs)): i[-1] + int(0.25 * fs)]
    y = np.concatenate([np.zeros(int(0.12 * fs)), y, np.zeros(int(0.12 * fs))])
    y = y / (np.max(np.abs(y)) + 1e-9) * 0.89     # -1 dBFS tepe
    return (y * 32767).astype(np.int16)

def wav_yaz(yol, s, fs=22050):
    with wave.open(yol, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(fs)
        w.writeframes(s.tobytes())

def main():
    os.makedirs(SES_DIR, exist_ok=True)
    tmp = os.path.join(os.path.dirname(__file__), 'ses_tmp')
    os.makedirs(tmp, exist_ok=True)
    for ad, en, _ in REPLIK:
        mp3 = os.path.join(tmp, ad + '.mp3')
        if not os.path.isfile(mp3) or '--yeniden' in sys.argv:
            asyncio.run(tts(en, mp3))
        pcm = mp3_pcm(mp3)
        out = isle(pcm)
        wav_yaz(os.path.join(SES_DIR, 'leonov_%s.wav' % ad), out)
        print('%-16s %5.2f sn' % (ad, len(out) / 22050.0))

    # ---- soundalias (iw_voiceovers2.csv basligi ve sutun degerleri birebir) ----
    bas = ('name,sequence,file,vol_min,vol_max,vol_mod,pitch_min,pitch_max,dist_min,dist_max,'
           'channel,type,probability,loop,masterslave,loadspec,subtitle,compression,'
           'secondaryaliasname,volumefalloffcurve,startdelay,speakermap,reverb,lfe percentage')
    satir = [bas]
    for ad, _, _ in REPLIK:
        satir.append('krasnoye_leonov_%s,,Voiceovers/krasnoye/leonov_%s.wav,0.99,0.99,voiceover,,,360,6000,'
                     'voice,streamed,,,master,krasnoye,KRASNOYE_LEONOV_%s' % (ad, ad, ad.upper()))
    os.makedirs(os.path.join(KOK, 'soundaliases'), exist_ok=True)
    with open(os.path.join(KOK, 'soundaliases', 'krasnoye.csv'), 'w', encoding='ascii', newline='\r\n') as f:
        f.write('\n'.join(satir) + '\n')

    # ---- localizedstrings/krasnoye.str ----
    o = ['VERSION             "1"', 'CONFIG              "C:\\trees\\cod2\\bin\\StringEd.cfg"',
         'FILENOTES           "krasnoye"', '']
    for ad, _, t in REPLIK:
        o += ['REFERENCE           LEONOV_%s' % ad.upper(), 'LANG_ENGLISH        "Leonov: %s"' % tr(t), '']
    for ref, t in GOREV:
        o += ['REFERENCE           %s' % ref, 'LANG_ENGLISH        "%s"' % tr(t), '']
    o.append('ENDMARKER')
    os.makedirs(os.path.join(KOK, 'localizedstrings'), exist_ok=True)
    with open(os.path.join(KOK, 'localizedstrings', 'krasnoye.str'), 'wb') as f:
        f.write('\r\n'.join(o).encode('cp1254') + b'\r\n')
    print('alias:', len(satir) - 1, ' str:', len(REPLIK) + len(GOREV))

if __name__ == '__main__':
    main()
