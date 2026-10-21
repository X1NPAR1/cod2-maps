# Asama 0 duman testi: derleme hattini ve malzeme yolunu dogrular.
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from kmap import Harita

KOK = r'F:\Activision\Call of Duty 2'
h = Harita()
# tankhunt worldspawn degerleri (olculdu)
h.ws.update({'_color': '1 .96 .98', 'ambient': '.0', 'sunlight': '1.15',
             'sundirection': '-42 -43 0', 'sundiffusecolor': '.9 .9 .96',
             'suncolor': '1 .96 .98', 'diffusefraction': '.40',
             '-contrastgain': '.4'})
h.oda_kabugu(-1024, -1024, 0, 1024, 1024, 1024, 16,
             'stalingradwinter_snow01', 'sky_tankhunt', 'sky_tankhunt')
h.kutu(-200, -200, 0, -72, -72, 128, 'stalingradwinter_woodplank01')
h.kutu(150, 100, 0, 278, 228, 96, 'stalingradwinter_woodplank02')
h.ent('info_player_start', origin=(0, -600, 8), angles=(0, 90, 0))
r = h.yaz(os.path.join(KOK, 'map_source', 'krasnoye_duman.map'))
print(r)
