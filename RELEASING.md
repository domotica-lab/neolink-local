# Releasing

1. **Core** (only if neolink itself changed): in `domotica-lab/neolink-local-core`
   set `VERSION` to the new number and push to `main`. GitHub builds and
   publishes `ghcr.io/domotica-lab/neolink-local:<version>` (amd64 + arm64).
   Wait for the "Build and Push Docker Image" run to finish.
2. **This repository**, in one commit:
   - `custom_components/neolink_local/manifest.json` → `"version"`
   - `neolink_local/config.yaml` → `version` (same number)
   - `neolink_local/build.yaml` → image tag, if the core changed
   - `neolink_local/CHANGELOG.md` → a `## <version>` section
3. Push to `main`. The **Release** workflow creates the tag and the GitHub
   release with that changelog section as notes. Home Assistant then offers the
   add-on update and HACS the integration update.

The workflow refuses to release if `manifest.json` and `config.yaml` carry
different versions, and does nothing if that release already exists.
