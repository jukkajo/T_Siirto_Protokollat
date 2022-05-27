import sys
from time import sleep

def palkki(iteraatiot, kaikki_iter, tila='', palkin_pituus=60, merkki=''):
    kaytetty_palkki = int(round(palkin_pituus * iteraatiot / float(kaikki_iter)))

    pros = round(100.0 * iteraatiot / float(kaikki_iter), 1)
    palkki = merkki * kaytetty_palkki + ' ' * (palkin_pituus - kaytetty_palkki)
    formaatti = "%s <%s> %s%s"
    
    form_lista = formaatti % (tila, palkki, pros, '%')
    print('\b' * len(form_lista), end='')
    sys.stdout.write(form_lista)
    sys.stdout.flush()

#käyttö:
#items = list(range(0,50))
#l = len(items)
#for i, item in enumerate(items):
#    sleep(0.2)
#    palkki(i+1, l, tila='Tila:', palkin_pituus=60, merkki="¤")
