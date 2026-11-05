# Neolink Local (integrazione)

Crea in Home Assistant le telecamere servite dall'add-on **Neolink Local**.

- Un dispositivo per camera con entità camera (video RTSP dall'add-on).
- Anteprime che **non svegliano** la camera: l'immagine è l'ultima vista dall'add-on.
- Sensori: *Collegata*, *Spettatori*, *Ultima immagine*, *Batteria* e *In carica* (letti solo mentre la camera è già sveglia; compaiono dopo la prima apertura).
- Camere aggiunte o tolte nell'add-on compaiono o spariscono da sole.
- Opzione per scegliere lo stream riprodotto: main, sub o extern.

## Installazione

1. Con HACS: aggiungi `https://github.com/domotica-lab/neolink-local` come repository personalizzato (tipo Integrazione) e installa *Neolink Local*. Senza HACS: copia questa cartella in `/config/custom_components/neolink_local/`.
2. Riavvia Home Assistant.
3. Impostazioni → Dispositivi e servizi → Aggiungi integrazione → **Neolink Local**.
   Con l'add-on sullo stesso Home Assistant lascia i valori proposti
   (`127.0.0.1`, porta `8559`).

Richiede l'add-on Neolink Local 1.0.2 o successivo. L'icona dell'integrazione compare da Home Assistant 2026.3 in poi.
