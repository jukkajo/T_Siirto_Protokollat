from yhdista_sok import yhdista_sok
import PakettiGen
import select as sel
import os
from Latauspalkki import palkki
host = "127.0.0.1"
tavu_lkm1, tavu_lkm2, tavu_lkm3 = 600, 516, 512
portti = 69
k=["WRQ","RRQ"]

t_out = 1
rt = "rt"
wt = "wt"

def laheta_tied(v_osoite, tied_nimi, luku, paketti, soketti):
    try:
        tiedosto = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), tied_nimi), rt)
        while True:
            
            tied_data = tiedosto.read().encode()
            block = 1
        
            osoite_n_data = time_out(v_osoite, luku, paketti, soketti)
            #1,2
            for i in range(0, len(tied_data), tavu_lkm2):
                print("Iteraatio: ", i)
                t_data_paketti = PakettiGen.palauta_DATA(tied_data[i:i + tavu_lkm2], block)
                soketti.sendto(t_data_paketti, osoite)
                #latauspalkki visualisoimaan prosessia
                palkki(i+1, len(tied_data), tila='Tila:', palkin_pituus=60, merkki="+")


                osoite_n_data = time_out(v_osoite, 1, t_data_paketti, soketti)
                block += 1

            print("Tiedosto lähetetty!")
            break    

    except FileNotFoundError:
        print("Tiedostoa ei löydy, kirjoitithan sen oikein?")

def vastaanota_tied(v_osoite, tied_nimi, luku, paketti, soketti):
   block = 1
   sisalto = b''
   
   #tarkasta tämä ja poista kommentti
   soketti.sendto(paketti, v_osoite)
   #v_osoite, data, r_data
   while True:
       
       osoite_n_data = time_out(v_osoite, luku, paketti, soketti)
       print("Timeout ok")
       v_paketti = PakettiGen.palauta_ACK(osoite_n_data[1][2:4])
       soketti.sendto(v_paketti, osoite_n_data[0])
       sisalto += osoite_n_data[1][4:]
       block += 1

       if len(osoite_n_data[1]) < tavu_lkm2:
           tied = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), tied_nimi), rt)
           tied.write(sisalto.decode())
           tied.close()
           print("Tiedoston luku onnistui!")
           break

           
    
#laita palauttamaan data ja osoite!
def time_out(v_osoite, luku, v_paketti, soketti):
    v_osoite, data = b'', b''
    #while True:
    while True:
        #soketti listaksi selectille
        r_data = sel.select([soketti],[],[],t_out)
        if r_data[0]:
            while True:
                    
                data, osoite = soketti.recvfrom(tavu_lkm1)
                v_osoite = osoite
                #data_vai_ack = False

                tunniste = 0
                #wrq, varm ack
                if luku == 1:
                    
                    if PakettiGen.varmista_ack(data, tunniste) == True:
                        print("Ack-0-paketti validi!")
                        break
                    
                    else:
                        print("Ack-0-paketti oli virheellinen, uudelleen lähetetään...")
                #rrq, varm data
                elif luku == 2:
                
                    if PakettiGen.varmista_data(data, tunniste) == True:
                        print("Data-paketti oli validi")
                        break
                    else:
                        print("Data-paketti oli virheellinen, uudelleen lähetetään...")

                elif luku == 3:
                    print("Virheellinen Ack-paketti, uudelleenlähetetään viimeisin 'block'")

                soketti.sendto(v_paketti, v_osoite)
                break
                
            else:
                if luku == 1:
                    print("Ack-0 / 'timed out', uudelleen lähetetään...")
                elif luku == 2:
                    print("Viimeisin paketti / 'timed out', uudelleen lähetetään...")
                elif luku == 3:           
                    print("Ack-paketti / 'timed out', uudelleen viimeisin data-paketti lähetetään...")
                soketti.sendto(v_paketti, v_osoite)
    return [v_osoite, data]
                    
def laheta_wrq_rrq(komento,luku,soketti):
    tied_nimi = input("Anna tiedostonnimi: ")
    paketti = PakettiGen.palauta_RRQ_tai_WRQ(tied_nimi, komento)
    #viimeisin
    v_osoite  = (host,portti)
    soketti.sendto(paketti, v_osoite)

    if luku == 1:
        print("Aloitetaan lähetys-prosessi")
        laheta_tied(v_osoite, tied_nimi, luku, paketti, soketti)
    else:
        vastaanota_tied(v_osoite, tied_nimi, luku, paketti, soketti)    

if __name__ == "__main__":
    soketti = yhdista_sok(host, portti)
    print("Soketti alustettu, yhdistetty hostiin: ", host, " portin: ", portti, " kautta!")
    komento = input("Anna 'rrq' pyytääksesi tiedostoa tai 'wrq' siirtääksesi tiedoston: ")
    while True:
        if komento.upper() == k[0]:
            laheta_wrq_rrq(komento, 1, soketti)
 
        elif komento.upper() == k[1]:
            laheta_wrq_rrq(komento, 2, soketti)
        else:
            print("Väärä komento, oikeat: 'wrq' tai 'rrq'")
        
