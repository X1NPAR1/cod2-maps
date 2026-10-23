# birlestir.py -- gen_kasrelbab.py = _bas.py + kumtepe'nin denenmis yardimcilari + _govde.py
import os
D = os.path.dirname(os.path.abspath(__file__))
k = open(os.path.join(D, '..', 'kumtepe_tools', 'gen_kumtepe.py'), encoding='utf-8').read()

def parca(bas, son):
    i = k.index(bas)
    j = k.index(son, i)
    return k[i:j]

yard = []
yard.append(parca('# ---------------------------------------------------------------- yardimcilar',
                  '# ---------------------------------------------------------------- sinir (oynanabilir cokgen)'))
yard.append(parca('# ---------------------------------------------------------------- kayitlar',
                  '# ---------------------------------------------------------------- gorunmez sinir'))
yard.append(parca('# =========================================================================\n# BINA YAPICI',
                  '# =========================================================================\n# KOY: avlu'))
yard.append(parca('# kirik duvar: ust kenari ucgen/egik parcalar', '# 3) ilk atistan sonra'))
yard.append(parca('def zikzak_duvar(', '# kuzey duvar: x 660'))
metin = open(os.path.join(D, '_bas.py'), encoding='utf-8').read() + '\n' + '\n'.join(yard) + \
        open(os.path.join(D, '_govde.py'), encoding='utf-8').read()
open(os.path.join(D, 'gen_kasrelbab.py'), 'w', encoding='utf-8').write(metin)
print('gen_kasrelbab.py: %d satir' % metin.count('\n'))
