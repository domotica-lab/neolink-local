# Changelog

## 1.0.12

- **Niente più disconnessioni per un singolo pacchetto illeggibile:** durante
  lo streaming, un solo pacchetto UDP rovinato o di tipo sconosciuto chiudeva la
  connessione con la camera (nel log `Connection Lost: BcUDP reciver dropped:
  NoneRecieved`), seguito da 3-7 secondi di riconnessione. Succedeva soprattutto
  con Wi-Fi debole. Ora il pacchetto viene scartato e il video continua; una
  volta al minuto il log indica quanti ne sono stati ignorati.
- Se la connessione si chiude davvero, il log ora ne scrive la causa reale
  (`UDP socket to … closed: …`).

## 1.0.11

- **Ricezione video più fluida:** i pacchetti ricevuti passavano al decoder
  attraverso una coda troppo piccola (100 pacchetti, meno di un fotogramma
  chiave). Quando si riempiva, neolink smetteva per un attimo di confermare i
  pacchetti alla camera, che lo interpretava come una connessione debole e
  rallentava o rispediva. Ora la coda è di 2048 pacchetti.
- Le conferme (ACK) alla camera stanno sempre in un solo pacchetto di rete.
- La riga `UDP loss from …` del log ora indica anche se la consegna al decoder
  si è bloccata (`delivery to decoder blocked`).

## 1.0.10

- **Collegamento più rapido delle camere a batteria:** neolink non prova più il
  TCP sulle camere a batteria (non ce l'hanno), che prima potevano perdere fino
  a 1,5 secondi a ogni collegamento. Le riconosce dal livello di batteria che
  riportano.
- **Meno blocchi dell'immagine:** l'attesa per un pacchetto perso ora arriva al
  massimo a 1,2 secondi (prima 2). I log hanno mostrato che la camera rispedisce
  il pacchetto dopo circa 0,8 secondi; aspettare di più bloccava l'immagine
  senza recuperare quasi niente.

## 1.0.9

- **Meno immagini rovinate su Wi-Fi debole:** le camere Reolink rispediscono un
  pacchetto perso con un loro ritardo, e spesso arrivava subito dopo i 500 ms di
  `udp_gap_skip_ms`, quando neolink l'aveva già saltato. Ora neolink se ne
  accorge e aspetta il tempo giusto per ogni camera (al massimo 2 secondi), poi
  torna a 500 ms quando non serve più. Una volta al minuto il log mostra una riga
  `UDP loss from …` con i pacchetti saltati e quelli arrivati in ritardo.

## 1.0.8

- **Il TCP automatico ora funziona anche con le camere in modalità `always`:**
  nella 1.0.7 neolink non conosceva ancora l'indirizzo delle camere quando
  queste si collegavano all'avvio, quindi restavano in UDP. Ora gli indirizzi
  salvati vengono caricati prima, e il TCP viene provato anche sull'indirizzo
  appena trovato (prima installazione o camera che ha cambiato IP).

## 1.0.7

- **Le camere alimentate usano il TCP da sole, come l'app Reolink:** con il solo
  `uid` neolink usava sempre l'UDP, dove ogni pacchetto perso sulla Wi-Fi diventa
  un'immagine rovinata (`UDP payload gap` nel log). Ora prova prima il TCP
  sull'ultimo indirizzo noto della camera, che rispedisce da solo i pacchetti
  persi. Neolink controlla che a quell'indirizzo ci sia proprio la camera giusta;
  le camere a batteria continuano a usare l'UDP. Non serve cambiare la
  configurazione: nel log compare `MEDIA PATH: TCP over LAN`.

## 1.0.6

- **Niente più video bloccato (e log pieno di errori `header.msg_id: 3`) se si
  perde il primo pacchetto di un flusso:** prima tutti i fotogrammi successivi
  venivano letti come testo e scartati finché la camera non si riconnetteva. Ora
  il flusso viene riconosciuto come video e l'immagine riparte al fotogramma
  chiave successivo.

## 1.0.5

- **Meno immagini rovinate (macchie grigie/viola) su Wi-Fi debole:** un pacchetto
  video perso veniva a volte saltato subito, senza aspettare che la camera lo
  rispedisse. Ora ogni pacchetto perso ha tutto il tempo di `udp_gap_skip_ms`.
- **Meno disconnessioni** con `Connection Lost: ... Magic invalid` quando si perde
  un pacchetto durante un fotogramma chiave.
- Documentazione: il valore consigliato di `udp_gap_skip_ms` è ora `500` (non
  più `150`, che causava le macchie). Se lo avevi impostato a 150, alzalo a 500.

## 1.0.4

- **Disponibile su GitHub**: si installa aggiungendo il repository
  `https://github.com/domotica-lab/neolink-local` e si aggiorna con un clic.
  Funziona anche su Raspberry Pi (aarch64).
- Integrazione installabile da HACS (repository personalizzato).
- **Apertura più rapida delle camere a batteria:** neolink si ricorda l'indirizzo
  IP di ogni camera e la cerca anche direttamente lì, oltre al messaggio a
  tutta la rete. L'indirizzo è salvato su disco e vale anche dopo un riavvio.
- Il registro mostra quanto dura ogni fase dell'apertura, per esempio
  `Local discovery: ... answered in 900 ms (asked at its last address)` e
  `Portone: Connected and logged in (2.1s: found in 0.9s, login 1.2s)`.

## 1.0.3

- *Ultima immagine* non torna più "Sconosciuto" dopo un riavvio: usa l'immagine
  salvata su disco.
- Il registro mostra ogni lettura della batteria (es. `Giardino: battery 76% (none)`),
  oppure `no battery reading` se la camera non la fornisce.
- Integrazione 1.0.3: tolto anche dai dispositivi già creati il "Firmware: 1.0.0"
  (era la versione dell'add-on, non della camera).

## 1.0.2

- **Batteria nell'integrazione:** nuovi sensori *Batteria* (%) e *In carica*
  per ogni camera a batteria. Il livello viene letto solo mentre la camera è
  già sveglia perché qualcuno la guarda (subito all'apertura, poi ogni 5
  minuti), quindi non la sveglia mai. L'ultimo valore resta visibile mentre la
  camera dorme ed è salvato su disco, così sopravvive ai riavvii. Negli
  attributi: ora della lettura, pannello solare, temperatura.

## 1.0.1

- Registro più pulito: le righe tecniche ripetute (collegamenti RTSP, code,
  smontaggio degli indirizzi all'arresto) sono ora visibili solo con
  `log_level: debug`.
- Integrazione 1.0.1: icona e logo propri; la scheda della camera non mostra più
  un "Firmware" che era in realtà la versione dell'add-on; *Ultima immagine* è
  ora tra i sensori diagnostici.

## 1.0.0

Prima versione di **Neolink Local**, basata su Neolink 0.7.19.

**Batteria**
- Ogni player che si chiude rilascia la camera, anche se si era ricollegato
  mentre la camera si svegliava. Dopo la chiusura compare
  `All permits dropped, disconnecting from camera relay` e la camera torna a
  dormire. Nell'originale poteva restare collegata per sempre.

**Video**
- Una sola connessione video per camera, condivisa da tutti i player. Chi si
  ricollega riparte subito dall'ultimo fotogramma completo, senza schermo nero.
- La chiusura di un player non ferma più il video degli altri (prima l'immagine
  poteva restare ferma fino a 60 secondi).

**Integrazione Home Assistant**
- Nuova integrazione *Neolink Local*: crea le camere da sola, con anteprime
  che non svegliano le camere e sensori *Collegata*, *Spettatori* e
  *Ultima immagine*.
- Interfaccia di stato locale (porta 8559, raggiungibile solo da questo Home
  Assistant). Opzioni `api_port` e `api_bind`.

**Add-on**
- Neolink già compilato: si installa in pochi minuti.
- Arresto pulito in circa 1,5 secondi invece della chiusura forzata
  (`exit code 137`).
- L'add-on parte con qualsiasi configurazione valida.
- Registro più leggibile: riepilogo per camera all'avvio; gli avvisi di
  pacchetti persi indicano l'indirizzo della camera.
- Icona, logo e descrizione in italiano e inglese di ogni opzione.
