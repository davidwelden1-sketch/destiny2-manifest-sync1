# Simulation evidence and limitations

These modules are **arithmetic frameworks**, not calibrated Destiny 2 mechanics.

- `ttk.py` assumes constant RPM and instant hits; burst weapons require `burst.py`.
- `stacking.py` takes a caller-specified stacking policy. Destiny buff categories, overrides, caps, and activation conditions must be established separately.
- `survivability.py` uses input resistance fractions and shields. It does not assert in-game Frost Armor, Void Overshield, Stronghold, or other DR values.
- `cooldowns.py` is a simple recharge approximation, not a measured ability energy model.
- `falloff.py` uses a linear approximation, not Bungie's actual weapon curves.
- `rotations.py` calculates window-average DPS from explicitly timed events, without modeling reloads, swaps, ammo or animation constraints.
- `provenance.py` requires source URL, date, context and evidence status for any calibration records.
- No result is certified current or obtainable merely because its component exists in the manifest.
- Tests verify arithmetic consistency, not gameplay validity.
