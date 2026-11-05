# Neolink Local

Porta in Home Assistant le telecamere **Reolink**, comprese quelle **a batteria
e P2P** (Argus, Go, Duo, videocitofoni…), come normali stream **RTSP locali**:
niente cloud, niente app, tutto resta sulla rete di casa. Le camere a batteria
si svegliano solo mentre le guardi e tornano a dormire appena chiudi.

## Cosa offre in più rispetto a Neolink originale

Basato su [Neolink](https://github.com/privatecoder/neolink) 0.7.19, con queste
migliorie:

| Area | Neolink Local |
|---|---|
| **Batteria** | Ogni player che si chiude rilascia la camera, anche se si era ricollegato mentre la camera si svegliava. Nell'originale la camera poteva restare collegata per sempre. |
| **Video condiviso** | Una sola connessione video verso la camera, condivisa da tutti i player. Un player che si ricollega (go2rtc lo fa spesso) riparte subito dall'ultimo fotogramma completo, senza schermo nero. |
| **Niente blocchi** | La chiusura di un player non interrompe più il video degli altri. Prima poteva lasciare un'immagine ferma fino a 60 secondi. |
| **Arresto pulito** | L'add-on si ferma in circa 1,5 secondi e lascia dormire le camere, invece di essere chiuso a forza dopo 10 secondi (`exit code 137`). |
| **Registro leggibile** | Un riepilogo per camera all'avvio invece di decine di righe ripetute. Gli avvisi di pacchetti persi indicano l'indirizzo della camera. |
| **Configurazione** | Ogni opzione è descritta in italiano. L'add-on parte con qualsiasi configurazione valida. |
| **Installazione** | Neolink è già incluso: pochi minuti, nessuna compilazione. |
| **Integrazione** | L'integrazione *Neolink Local* crea le camere da sola, con anteprime che non svegliano le camere e sensori di stato. |

## Installazione

1. **Impostazioni → Add-on → Raccolta add-on → ⋮ → Repository**, incolla
   `https://github.com/domotica-lab/neolink-local` e premi **Aggiungi**.
2. Cerca **Neolink Local** nella raccolta, aprilo e premi **Installa**.
3. Configura le camere (vedi sotto) e premi **Avvia**.

Funziona su PC/mini PC (amd64) e Raspberry Pi 4/5 (aarch64).

> Se hai anche l'add-on Neolink originale, **fermalo e disattivane l'avvio
> automatico**: usano le stesse camere.

## Configurazione

Esempio per una camera a batteria sulla rete di casa:

```yaml
log_level: info
bind: 0.0.0.0
bind_port: 8558
offline_timeout_secs: 0
stream_cache_path: /data/stream-cache.json
rtsp_users: []
mqtt:
  enabled: false
  discovery: false
  discovery_topic: homeassistant
cameras:
  - name: Ingresso
    username: admin
    password: "la-tua-password"
    uid: 95270000XXXXXXXX
    discovery: local
    connect_mode: on_demand
    relay_warm_seconds: 0
    startup_keyframe_wait_secs: 2
    udp_gap_skip_ms: 150
    stream: All
```

Metti la password **tra virgolette**, soprattutto se contiene simboli.
Ogni opzione ha una descrizione nella scheda **Configurazione** (attiva
*Mostra opzioni facoltative non utilizzate* per vederle tutte).

### Valori consigliati

| Opzione | Camere a batteria | Camere alimentate | Perché |
|---|---|---|---|
| `connect_mode` | `on_demand` | `always` | A batteria si collega solo mentre la guardi. |
| `relay_warm_seconds` | `0` | — | Scollega subito dopo la chiusura. |
| `discovery` | `local` | `local` | Trova la camera sulla rete di casa: più veloce e privato. |
| `startup_keyframe_wait_secs` | `2` | `2` | Mostra subito il video vero, senza schermo nero iniziale. |
| `udp_gap_skip_ms` | `150` | `150` | Su Wi-Fi riduce gli scatti dovuti ai pacchetti persi (predefinito 500). |

## Integrazione Neolink Local (consigliata)

L'integrazione **Neolink Local** crea da sola le camere in Home Assistant:

- un dispositivo per ogni camera, con entità camera pronta per dashboard e popup;
- **anteprime che non svegliano la camera**: la miniatura è l'ultima immagine
  vista, servita dall'add-on senza contattare la camera;
- sensori *Collegata* (la camera è sveglia) e *Spettatori* (quanti la guardano),
  e *Ultima immagine* (quando è stata vista l'ultima volta);
- **batteria** (%) e *In carica* per le camere a batteria: letti solo mentre
  guardi la camera, quindi non la svegliano. Mostrano l'ultimo valore letto
  (l'ora della lettura è negli attributi); compaiono dopo la prima apertura;
- le camere aggiunte o tolte nell'add-on compaiono o spariscono da sole.

**Installazione**

Con HACS: **HACS → ⋮ → Repository personalizzati**, incolla
`https://github.com/domotica-lab/neolink-local`, tipo **Integrazione**, poi
installa *Neolink Local* e riavvia Home Assistant.

Senza HACS: copia la cartella `custom_components/neolink_local` del repository
in `/config/custom_components/` e riavvia Home Assistant.

Poi: **Impostazioni → Dispositivi e servizi → Aggiungi integrazione →
Neolink Local**, lascia i valori proposti e conferma.

L'integrazione legge lo stato dall'add-on ogni 10 secondi tramite un'interfaccia
locale (porta 8559) raggiungibile **solo da questo Home Assistant**: non sveglia
le camere e non è visibile dal resto della rete.

## Usare gli stream senza l'integrazione

```
rtsp://<IP-di-Home-Assistant>:8558/<nome-camera>/main     alta qualità
rtsp://<IP-di-Home-Assistant>:8558/<nome-camera>/sub      leggero
rtsp://<IP-di-Home-Assistant>:8558/<nome-camera>/extern   bilanciato
```

Aggiungili con l'integrazione **Generic Camera** (Impostazioni → Dispositivi e
servizi → Aggiungi integrazione → *Generic Camera*), inserendo l'indirizzo nel
campo *URL dello stream*.

**Batteria:** le schede camera in modalità *live* o *auto* tengono sveglia la
camera finché la dashboard è aperta, anche su un tablet o sul telefono in
background. Usa schede con immagine statica e apri il video solo nel popup.

## Verificare che la camera torni a dormire

Apri la scheda **Registro**, apri e poi chiudi il popup della camera. Pochi
secondi dopo la chiusura devono comparire:

```
Portone::Main: Consumer closed, stopping camera stream task and releasing permit
Portone: All permits dropped, disconnecting from camera relay
```

L'ultima riga conferma che la camera è stata scollegata. Lo stream resta attivo
2 secondi dopo l'ultimo player, così una riconnessione immediata è istantanea.

## Leggere il registro

| Riga | Significato |
|---|---|
| `Permit acquired, connecting to camera relay` | Qualcuno ha aperto la camera: si sta collegando. |
| `Starting camera stream` | Avviato il video dalla camera. |
| `Joined the running camera stream (2 viewers…)` | Un altro player usa lo stesso video, senza disturbare la camera. |
| `first camera keyframe received; switching from keepalive to live` | Il video vero è arrivato. |
| `UDP payload gap from 192.168.1.64:…` | Un pacchetto video perso sul Wi-Fi di quella camera. Se è frequente, il segnale è debole. |
| `All permits dropped, disconnecting from camera relay` | La camera è stata rilasciata. |

## Risoluzione dei problemi

| Sintomo | Causa probabile e soluzione |
|---|---|
| L'add-on si ferma subito dopo l'avvio | Un'altra istanza usa la porta 8558 (ferma l'add-on originale), oppure una password è vuota o non tra virgolette. |
| `Login credentials were not accepted` | Password sbagliata: è quella dell'app Reolink per quella camera. |
| `Trying local discovery` ripetuto | La camera è su un'altra rete o VLAN: prova `discovery: remote`. |
| Il video impiega 5–10 secondi ad apparire | Normale per una camera addormentata: è il tempo di risveglio. |
| Il video va a scatti | Pacchetti persi sul Wi-Fi (righe `UDP payload gap`): imposta `udp_gap_skip_ms: 150` e migliora il segnale della camera. |
| La batteria cala anche senza guardare | Cerca nel registro `Factory received new client` mentre nessuno guarda: di solito è una scheda della dashboard in modalità live. |

## Crediti e licenza

Neolink è un progetto open source (licenza AGPL-3.0) di
[thirtythreeforty](https://github.com/thirtythreeforty/neolink),
[QuantumEntangledAndy](https://github.com/QuantumEntangledAndy/neolink) e
[privatecoder](https://github.com/privatecoder/neolink), da cui deriva anche
l'add-on originale [neolink-ha-addon](https://github.com/privatecoder/neolink-ha-addon).
Neolink Local non è affiliato a Reolink.
