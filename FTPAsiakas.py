

import sys
import re
import socket as s
from Latauspalkki import palkki
from time import sleep

k = ["USER", "PASS", "QUIT", "PASV", "RETR", "LIST"]
#kontrolliyhteyden portti
k_portti = 21 #21
host = "127.0.1.1"
#muut komennot / koodit
kom = ["220", "227", "331", "230", "550", "150"]

class Error(Exception):
    pass

def kommunikointi(soketti):
    puskuri = soketti.recv(1024)
    if kom[0] not in puskuri.decode():
        print(puskuri)
        sys.exit("Palvelin ei vastaa")

    try:
        kayttaja = input("Kayttaja: ")
        vastaa = k[0] + " " + kayttaja + "\n"
        soketti.send(str.encode(vastaa))
        vastaus = soketti.recv(1024)
        if kom[2] not in vastaus.decode():
            raise Error
        salasana = input("Salasana: ")
        soketti.send(str.encode(k[1] + " " + salasana + "\n"))
        vastaus2 = soketti.recv(1024)
        if kom[2] not in vastaus.decode():
            raise Error
        print("Kirjautuminen onnistui! Ohjelma valmiina komennoille, näet ne kirjoittamalla esim: 'h'")
            
    except Error:
        soketti.close()
        sys.exit("Kirjautuminen ei onnistunut")

    #kuunnellaan syötteitä käyttäjältä, kunnes antaa sopivia käskyjä
    while True:
        komento = kayttajan_syote()
        #kättely
        if komento == k[2]:
            soketti.send(str.encode(k[2] + " \n"))
            soketti.close()
            sys.exit()
            print("Yhteys suljettu")
        elif k[5] in komento:
            #pyydetään palvelinta kuuntelemaan ei de factoa data porttia
            pas_soketti = tilan_vaihto(soketti)
            print("Passiivisessa tilassa!")
            soketti.send(str.encode(komento + " \n"))
            pal_vast = soketti.recv(1024).decode()
            if kom[4] in pal_vast:
                print("Antamaasi hakemistoa ei löytynyt!")
            elif kom[5] in pal_vast:
                #jos 150 palvelimelta, niin kuunnellaan passiivista väylää
                pas_vast = pas_soketti.recv(1024)

                if pas_vast:
                    #tulostetaan mitä hakemistossa
                    print(pas_vast.decode())
                else:
                    print("Hakemistoa on tyhjä!")
                pas_soketti.close()

            elif k[4] in pal_vast:
                dat_sok = tilan_vaihto(soketti)
                soketti.send(str.encode(pal_vast + " \n"))
                p_vast = soketti.recv(1024).decode()
                print("ju",p_vast)
                if kom[5] in p_vast:
                    pa_vast = dat_sok.recv(1024).decode()
                    print(p_vast)
                   # tiedosto = open()
                    
                elif kom[4] in p_vast:
                    print("Antamaasi tiedostoa ei löytynyt!")
                else:
                    print("Palvelin ei toimi oletetusti. Vastasi siis: ", p_vast)
               
#tilanvaihto aktiivista passiiviin
def tilan_vaihto(soketti):
    soketti.send(str.encode(k[3] + " \n"))
    
    while True:
        vastaus = soketti.recv(1024).decode()
        if kom[1] in vastaus:
            print(vastaus)
            break
        
    mjono = vastaus[vastaus.find('(') + 1:vastaus.find(')')]
    t = mjono.split(',') 
    data_osoite = t[0] + '.' + t[1] + '.' + t[2] + '.' + t[3]
    data_portti = (int(t[4]) * 256) + int(t[5])
    soketti_pas = s.socket(s.AF_INET, s.SOCK_STREAM)
    print("Yhdistämme osoitteeseen: ", data_osoite, ", portin: ", data_portti, " kautta.")
    soketti_pas.connect((data_osoite, data_portti))
    return soketti_pas
    
def testaa_s(s,luku):
    t = False
    merkit = ""

    #LIST
    if luku == 1:
        merkit = "^LIST( \/([A-z0-9-_+]+\/)*)?$"

    #RETR
    elif luku == 2:
        merkit = "^RETR (\/([A-z0-9-_+]+\/)*)?([a-zA-Z0_9]+)?.*$"
   
    if re.search(merkit, s):
        t = True   
    return t

def kayttajan_syote():
    syote = input()
    vastaa = ""

    if syote == "h" or syote == "H":
        print("Käytettävät komennot: ( QUIT, RETR <SP> <pathname>, LIST [<SP><path>] ), esimerkit komennoista LIST ja RETR saat kirjoittamalla: 'esim'")
    elif syote == "esim":
        print("Esimerkit:\nLIST /mnt/c/FTP/ftp/\nRETR /mnt/c/FTP/ftp/testi.txt")
        
    elif k[2] in syote:
        vastaa = k[2]
        print("Vastasimme: ", vastaa)

    
    elif k[5] in syote:
        if len(syote) > (len(k[4]) + 1):
            luku = 1 
            if testaa_s(syote,luku) == True:
                vastaa = syote
                print("Vastasimme: ", vastaa)
            else:
                print("Komennossasi (LIST) kiellettyjä/ylimääräisiä merkkejä!")
            
    elif k[4] in syote:
        if len(syote) > (len(k[4]) + 1):
            luku = 2
            if testaa_s(syote,luku) == True:
                vastaa = syote
                print("Vastasimme: ", vastaa)
            else:
                print("Komennossasi (RETR) kiellettyjä/ylimääräisiä merkkejä!")
    else:
        print("Kirjoitit: ", syote, ", se ei vastaa käytettäviä komentoja: QUIT, RETR <SP> <pathname>, LIST [<SP><path>], esimerkkejä saat kirjoittamalla: 'esim'")
   
    return vastaa
    
if __name__ == "__main__":
    sy = input("Tämä on simppeli FTP-asiakasohjelma! \nYhdistetäänkö palvelimeen " + host + " portin " + str(k_portti) + "  kautta? (k / e)\n")
    if sy != "k" or sy != "K":
        print("Soketin alustus...")

        #tämä on täysin turha ja resursseja syövä, mutta tulipahan kokeiltua
        for i in range(20):
            sleep(0.05)
            palkki(i+1, 20, tila='Tila:', palkin_pituus=60, merkki="¤")

        soketti = s.socket(s.AF_INET, s.SOCK_STREAM)
        soketti.connect((host, k_portti))
        print("\nYhdistetty!")
        kommunikointi(soketti)
    
    else:
        print("Emme yhdistäneet!")
