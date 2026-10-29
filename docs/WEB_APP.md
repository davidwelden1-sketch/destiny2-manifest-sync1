# Destiny 2 Build Lab website

This repository now includes an initial interactive Streamlit dashboard in `web_app.py`.

## Run locally

```bash
python -m pip install -r requirements-web.txt
python -m streamlit run web_app.py
```

The terminal displays a local browser address. This is not a deployed public website.

## Included

- Class and activity selectors
- Constant-rate PvP TTK model using user-entered damage and health
- Hypothetical damage-resistance stacking and effective-health calculations
- Basic ability cooldown model
- Four-phase project status

## Limitations

All calculator inputs are hypothetical unless separately sourced and validated.
This version does **not** search the full Bungie manifest, verify current Artifact
selections, certify obtainability, run exhaustive build discovery, or authenticate
collaborators. A hosted deployment requires a hosting service and configuration.

For Streamlit Community Cloud, select this GitHub repository, branch `main`,
entrypoint `web_app.py`, and ensure the deployment installs
`requirements-web.txt` (or copy the dependency into `requirements.txt`).
