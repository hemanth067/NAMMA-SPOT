# NammaSpot — Python/Kivy Prototype

A mobile-oriented local-help application built with Python, Kivy/KivyMD and MapView.

## Run on Windows/Linux/macOS

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Current prototype

- NammaSpot home screen
- Nearby service map
- Service category filters
- Demo service markers
- Help-request UI
- Provider dashboard
- Fallback/demo map behavior
- No API key required for the basic prototype

## Production backend

The next layer should replace `DEMO_PROVIDERS` with Firebase/Firestore:
- users
- serviceProviders
- helpRequests
- ratings
- serviceLocations

For Android APK packaging, use Buildozer on Linux/WSL. See `buildozer.spec`.

## Important

The demo coordinates are sample coordinates around Ranipet/Vellore-region Tamil Nadu and are not live business locations. Do not publish them as real providers.
