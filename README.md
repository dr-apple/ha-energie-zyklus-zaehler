# Energie Zyklus Zähler

A small Home Assistant integration for the common "I have a lot of power-metered
smart plugs and want Day/Week/Month/Year consumption counters for each one"
situation — without hand-building four [`utility_meter`](https://www.home-assistant.io/integrations/utility_meter/)
helpers per plug and without a custom options dialog to remember.

## Why

Home Assistant's built-in `utility_meter` helper already does the actual
counting correctly — cycle resets, month lengths, leap years, and handling a
source sensor that occasionally resets to zero. There's no reason to
reimplement that. What's missing is a quick way to say *"for this energy
sensor, give me a Day counter and a Month counter, but skip Week and Year"* —
and to change your mind later without re-adding anything.

This integration is a thin, entity-based manager on top of `utility_meter`:

- Add an energy sensor once via **Settings → Devices & Services → Add
  Integration → "Energie Zyklus Zähler"**.
- You get a device page with four switches — **Tageszähler aktiv**,
  **Wochenzähler aktiv**, **Monatszähler aktiv**, **Jahreszähler aktiv** — all
  on by default.
- Each switch creates (or removes) the matching `utility_meter` entry behind
  the scenes, and its resulting counter sensor is folded onto the same
  device page — so everything for one plug lives in one place.
- Turn a switch off later and its counter disappears; turn it back on and it
  reappears with a fresh cycle, exactly like adding it new.

No options flow, no YAML, no separate settings screen — the switches on the
device page *are* the configuration.

## Installation

### HACS (custom repository)

1. HACS → Integrations → ⋮ → Custom repositories.
2. Add `https://github.com/dr-apple/ha-energie-zyklus-zaehler`, category
   "Integration".
3. Install "Energie Zyklus Zähler", restart Home Assistant.

### Manual

Copy `custom_components/energie_zyklus_zaehler` into your
`config/custom_components/` folder and restart Home Assistant.

## Setup

1. **Settings → Devices & Services → Add Integration → "Energie Zyklus
   Zähler"**.
2. Pick one of two sources:
   - **Echten Energiesensor verwenden** — pick any existing energy sensor
     (filtered to `device_class: energy`), optionally give it a name.
   - **Verbrauch simulieren** — for a device with no real power measurement
     but a known, roughly constant draw (a satellite distributor running
     24/7, an always-on network switch, ...): give it a name and a wattage.
     A `Simulierte Energie` sensor then accumulates kWh over time from that
     constant figure, exactly like a real total_increasing energy sensor —
     the wattage stays live-editable afterward via a `Simulierte Leistung`
     number entity on the same device page, no need to remove and re-add.
3. Repeat once per smart plug / energy sensor / simulated device you want
   counters for.
4. On each device page, toggle the four switches to pick which cycles you
   actually want for that source.

## Notes

- Each cycle's counter is a real `utility_meter` sensor (so it works with
  anything else that already expects one: the Energy dashboard, cost
  templates, statistics cards) — this integration only manages *which* of
  them exist for a given source.
- Removing the integration entry for a source removes every `utility_meter`
  entry it created for that source too — nothing is left orphaned.
- A real source sensor must report `state_class: total_increasing` (or
  `total`) and a `device_class: energy` — the same requirement `utility_meter`
  itself has. A simulated source already satisfies this by construction.
- Simulation assumes a *constant* load. For a device whose draw actually
  varies, add a real power-metered plug instead — this won't track spikes
  or idle periods.

## License

MIT — see [LICENSE](LICENSE).
