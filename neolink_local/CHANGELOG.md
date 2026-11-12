# Changelog

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
