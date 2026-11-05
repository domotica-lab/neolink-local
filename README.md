# Neolink Local

Reolink cameras — including **battery and P2P models** (Argus, Go, Duo,
doorbells…) — in Home Assistant as **local RTSP streams**, with no cloud.
Battery cameras wake up only while someone watches and go back to sleep as soon
as the player closes.

This repository contains:

| | |
|---|---|
| [`neolink_local/`](neolink_local) | Home Assistant **add-on** (amd64, aarch64) |
| [`custom_components/neolink_local/`](custom_components/neolink_local) | Home Assistant **integration**: cameras, thumbnails that never wake a camera, *Connected*, *Viewers*, *Battery* and *Charging* sensors |

The add-on runs [Neolink Local core](https://github.com/domotica-lab/neolink-local-core),
an unofficial fork of [Neolink](https://github.com/privatecoder/neolink).

## Install

**Add-on:** Settings → Add-ons → Add-on store → ⋮ → Repositories → add
`https://github.com/domotica-lab/neolink-local`, then install **Neolink Local**.

**Integration:** HACS → ⋮ → Custom repositories → add
`https://github.com/domotica-lab/neolink-local` as *Integration*, install
**Neolink Local**, restart Home Assistant, then Settings → Devices & services →
Add integration → **Neolink Local** (keep the suggested values).
Without HACS, copy `custom_components/neolink_local` to
`/config/custom_components/`.

Full documentation (Italian) is in the add-on's **Documentation** tab and in
[`neolink_local/DOCS.md`](neolink_local/DOCS.md).

## What is different from Neolink

- Battery cameras in `on_demand` mode always disconnect after the last viewer
  leaves (in the original they could stay connected forever after a player
  reconnect, draining the battery).
- One shared camera stream for all players; a reconnecting player restarts
  from the last keyframe instead of a black screen, and closing one player no
  longer freezes the others.
- Faster wake-up: the camera is also asked directly at its last known IP.
- Clean shutdown in about 1.5 s; readable logs.
- Status API used by the integration; the battery is read only while the camera
  is already awake.

## Italiano

Telecamere Reolink, anche a batteria, in Home Assistant senza cloud.
Installazione: aggiungi `https://github.com/domotica-lab/neolink-local` come
repository degli add-on (e come repository personalizzato HACS per
l'integrazione). La guida completa è nella scheda **Documentazione**
dell'add-on.

## License and credits

AGPL-3.0, like Neolink. Neolink is by
[thirtythreeforty](https://github.com/thirtythreeforty/neolink),
[QuantumEntangledAndy](https://github.com/QuantumEntangledAndy/neolink) and
[privatecoder](https://github.com/privatecoder/neolink). The add-on is derived
from [neolink-ha-addon](https://github.com/privatecoder/neolink-ha-addon).
**Not an official Neolink release and not affiliated with Reolink.**
