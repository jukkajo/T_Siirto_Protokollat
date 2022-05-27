from yhdista_sok import yhdista_sok
import PakettiGen as pgen
import select as sel
import os
#parametrit
host = "127.0.0.1"
cmd_portti = 69
tied_portti = 6969

#data
tavu_lkm = 512
#muu
tavu_lkm2 = 600
tavu_lkm3 = 516

rt="rt"
wt="wt"
#opkoodit
opk = [1, 2, 3, 4, 5]
nt = bytes(opk[0])

def WRQ_tapahtuma(tied, osoite):
    soketti = yhdista_sok(host, tied_portti)
    tied_sisalto = b''
    ack_paketti = pgen.palauta_ACK((nt + nt))
    soketti.sendto(ack_paketti, osoite)
    y, b = 1, 1
    ack2 = pgen.palauta_ACK((nt + bytes([opk[0]]))) #ack 1
    ind = 0    
    while True:
        
        #timeoutin implementointi
        while True:
             #r_data = sel.select([soketti], e, r, b)
             r_data = sel.select([soketti], [], [], y)
             
             if r_data[0]:
                 while True:
                     data = soketti.recvfrom(tavu_lkm2)
                     #ei pitäisi komplikaatioita tulla tästä
                     osoite = data
                     print("data liikkuu")
                     if pgen.varmista_data(data, b) == True:
                         print("Dataa liikkuu!")
                         break
                     else:
                         print("Data-paketti oli virheellinen, uudelleen lähetetään viimeisin 'ack'")
                         soketti.sendto(ack2, osoite)
                         print("1")
                 break
                 

             else:
                 while ind < 5:
                     print("Data-paketin lähetys keskeytyi, uudelleen lähetetään...")
                     soketti.sendto(ack2, osoite)
                     ind += 1
                 print("Ohjelma ei toimi odotetusti, keskeytetään")
        
        soketti.sendto(pgen.palauta_ACK(data[2:4]), osoite)
        tied_sisalto += data[4:]
        b += 1

        # 'The end of a transfer is marked by a DATA packet that contains
        # between 0 and 511 bytes of data (i.e., Datagram length < 516)'
        if len(data) < tavu_lkm3:
            t=tied_sisalto.decode()
            tied2 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), tied), wt)
            tied2.write(t)
            tied2.close()
            print("Tiedoston lukun onnistui!")
        break

        
def RRQ_tapahtuma(puskuri, tied):
    soketti = yhdista_sok(host, tied_portti)
    tavut = tied.read()
    b = 1
    data = puskuri.encode()
    osoite = puskuri
    
    #512 tavun paketteja
    for i in range(0, len(data), tavut_lkm):
           # tässä b = block
           paketti = pgen.palauta_DATA(data[i:i + tavu_lkm], b)
           soketti.sendto(paketti, osoite)
           while True:
               #readlist, writelist, exceptionlist, timeout
               r_data = sel.select([soketti], w, e, b)
 
               #eka tavu != tyhjä, niin aloitetaan
               if r_data[0]:
                   while True:
                       vastaus = soketti.recv(tavu_lkm2)
                       if pgen.varmista_ack(vastaus, b) == True:
                           break
                       else:
                           print("Ack-paketti oli virheellinen, uudelleen lähetetään viimeisin 'block'")
                           soketti.sendto(paketti, osoite)
                           break

               else:
                   soketti.sendto(paketti, osoite)
                   print("Ack-paketin lähetys keskeytyi, uudelleen lähetetään...")
           b += 1
    print("Tiedosto lähetetty onnistuneesti!")
    soketti.close()

        
def kaynnista():
    soketti = yhdista_sok(host, cmd_portti)
    print("Soketti alustettu, kuunnellaan yhteyspyyntöjä")
    
    while True:
        puskuri, osoite = soketti.recvfrom(tavu_lkm2)
        if puskuri:
            tavu_2 = puskuri[1:2]
            
            #tarkastetaan, mikä koodi tavussa 2 wrq tai rrq
            if tavu_2 == bytes([opk[0]]):
                #jos 
                tied_nimi = pgen.palauta_req_info(puskuri)
                try:
                    tiedosto = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), tied_nimi), rt)
                #valmis poikkeus
                except FileNotFoundError:
                    print("Ei kyseistä tiedostoa, suljetaan soketti...")
                    soketti.close()
                    break

                RRQ_tapahtuma(puskuri, tiedosto)
 
            elif tavu_2 == bytes([opk[1]]):
                print("jep")
                pri = pgen.palauta_req_info(puskuri)
                WRQ_tapahtuma(pri, osoite)
