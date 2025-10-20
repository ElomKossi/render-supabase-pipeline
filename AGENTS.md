# Repository Guidelines

## Project Structure & Module Organization
Ce repo automatise des déploiements Render ↔ Supabase pour les données marché (Alpha Vantage) et météo (Open-Meteo) :
- `infra/render/` contient les blueprints Render (`cron-job.yaml` pour le marché, `cron-weather.yaml` pour la météo).
- `supabase/` contient la configuration Supabase et les schémas (`market_snapshots.sql`, `weather_snapshots.sql`).
- `pipeline/lib/market/` concentre la stack marché (config, client Alpha Vantage, transformation).
- `pipeline/lib/weather/` regroupe la stack météo (config, client Open-Meteo).
- `pipeline/lib/utils/` héberge les utilitaires partagés (`persist.py` pour Supabase).
- `pipeline/bin/` expose les exécutables (`fetch_market_data.py`, `fetch_weather_data.py`).
- `docs/` rassemble procédures et runbooks (`docs/cron-job.md`).
- `tests/` attend vos validations automatiques (`tests/pipeline/...`).

## Build, Test, and Development Commands
Depuis la racine :
```
pip install -r requirements.txt                 # Installer les dépendances
python pipeline/bin/fetch_market_data.py        # Ingestion Alpha Vantage
python pipeline/bin/fetch_weather_data.py       # Ingestion Open-Meteo
render blueprint deploy infra/render/cron-job.yaml --preview
render blueprint deploy infra/render/cron-weather.yaml --preview
```
Documentez toute nouvelle commande dans `docs/`.

## Coding Style & Naming Conventions
- Retrait : 2 espaces pour YAML/JSON, 4 espaces pour Python.
- Fonctions en `snake_case`, classes en `PascalCase`, fichiers en `kebab-case`. Préfixez les migrations/SQL par un timestamp si vous en ajoutez.
- Utilisez `ruff format` (à activer) et `ruff check` pour le linting Python ; `shellcheck` pour les scripts shell.
- Variables d’environnement en majuscules (`ALPHAVANTAGE_TIMEOUT`, `OPENMETEO_LATITUDE`, etc.).

## Testing Guidelines
- Placez les tests unitaires à côté des modules correspondants (`tests/pipeline/test_market_snapshot.py`, `tests/pipeline/test_weather_client.py`).
- Mockez les appels HTTP pour vérifier la transformation (`market.alpha.fetch_intraday`, `weather.client.build_snapshot`).
- Réinitialisez Supabase via `supabase db reset` avant les tests d’intégration ; entreposez les fixtures dans `tests/fixtures/`.
- Maintenez la CI rapide (<5 min) et ajoutez vos tests dans `.github/workflows/ci.yaml`.

## CI Pipeline
- Le workflow `.github/workflows/ci.yaml` s’exécute sur push/PR vers `main`, installe les dépendances, lance `ruff check` et `basedpyright`.
- Étendez-le avec vos suites de tests ou migrations dry-run pour garantir la qualité avant déploiement Render.

## Commit & Pull Request Guidelines
- Suivez Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`) avec des sujets ≤72 caractères.
- Relancez les commandes ci-dessus avant review et mentionnez toute manipulation de secrets/configs dans la PR.
- Documentez l’impact utilisateur, les logs Render notables et liez les issues associées.
- Ne commitez jamais `.env`; mettez à jour `.env.example` pour toute nouvelle variable.

## Security & Configuration Tips
- Stockez les secrets uniquement dans Render ou Supabase ; laissez les `.env` locaux ignorés.
- Faites tourner les clés/API par environnement et documentez leur emplacement dans `docs/secrets.md`.
- Vérifiez régulièrement les logs Render pour prévenir une fuite de secrets ou des taux d’erreur inhabituels.
