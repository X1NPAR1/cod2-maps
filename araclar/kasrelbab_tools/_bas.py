# -*- coding: utf-8 -*-
"""
gen_kasrelbab.py -- CoD2 SP 'kasrelbab' (Operation Silent Dawn, Kasr el-Bab, Misir, 2 Kasim 1942, safak).

Duzen (dunya birimi, kuzey = +Y; gok kutusu 20480 x 16384):
  GB  : baslangic sirti -- tek agac + cali obegi (oyuncu gizlenir); arkasinda takviye vadisi
  G   : konvoy yolu (bati vadisinden girer, dogu-guneyde harita disina kivrilir)
  Orta: gozetleme kulubesi (2 Alman, telsiz)
  KD  : surlu kasaba (3200 x 2600): bati buyuk kapi, dogu cikis kapisi, 10 bina
        (4 girilebilir), meydan, minare, 3 flak88; cikis yolu doguya kivrilir
Skill kurallari (cod2-map-maker): uc katman sinir, kivrik gizli yollar, kapi 64x88,
pencere 46..88 '+' kasa, esyalara clip, dugum >= 40 aralik, yikilir parcalar gok kutusu
icinde (aydinlik) ayri brushmodel; her doku/model iwd'de dogrulanir (onizleme: kb_atlas).
Bu dosya _bas.py + kumtepe yardimcilari + _govde.py birlestirilerek URETILIR (birlestir.py).
"""
import os, sys, math, random, zipfile, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kmap import Harita, OLCEK

KOK = r'F:\Activision\Call of Duty 2'
HARITA = 'kasrelbab'

# ---------------------------------------------------------------- malzemeler (onizlendi)
KUM = 'egypt_roughdirt_04'
YOL = 'duhoc_dirt_road'
KAYA = 'egypt_rock_1'
DIS = 'egypt_plaster_exteriorwall03'
DIS2 = 'egypt_plaster_stucco1'
DIS3 = 'egypt_brick_sand_generic1'
IC = 'egypt_plaster_interiorwall2'
TABAN = 'egypt_concrete_floor2'
CATI = 'egypt_gravel_roof1'
TAS = 'egypt_sandstone_generic1'
SUR = 'egypt_sandstone_wall2'
SUR_BANT = 'egypt_sandstone_towerwalltrim'
TRIM = 'egypt_wood_generic1'
KIRIS = 'egypt_wood_beam'
KAPI_M = 'egypt_wood_door2'
BUYUK_KAPI = 'egypt_wood_door1'
KAPAK = 'egypt_wood_shutters1'
TAVAN = 'egypt_wood_ceiling1'
GOK = 'sky_elalamein'
CAULK = 'caulk'
SINIR = 'clip_player'
for m_, o_ in ((KUM, (512, 512)), (YOL, (256, 256)), (DIS, (256, 256)), (DIS2, (256, 256)), (DIS3, (256, 256)),
               (IC, (256, 256)), (TABAN, (256, 256)), (CATI, (256, 256)), (TAS, (512, 256)), (SUR, (256, 256)),
               (SUR_BANT, (256, 32)), (TRIM, (64, 128)), (KIRIS, (128, 128)), (TAVAN, (256, 256)), (KAYA, (256, 256))):
    OLCEK[m_] = o_

H = Harita()
# safak: alcak, pembe-turuncu gunes, hafif kum sisi
H.ws.update({'_color': '1 .82 .70', 'ambient': '.24', 'sunlight': '1.15',
             'sundirection': '-12 70 0', 'sundiffusecolor': '1 .76 .62',
             'suncolor': '1 .70 .52', 'diffusefraction': '.55',
             '-contrastgain': '.4', 'northyaw': '90'})
