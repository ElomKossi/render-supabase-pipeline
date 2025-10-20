# Render Cron Jobs

Ce dépôt fournit deux pipelines de collecte :
1. **Market data** via Alpha Vantage.
2. **Weather data** via Open-Meteo.

## Prérequis communs
- Projet Supabase avec les tables nécessaires :
  - `supabase/sql/market_snapshots.sql`
  - `supabase/sql/weather_snapshots.sql`
- Compte Render avec accès Cron (plan Starter ou supérieur).
- Secrets Supabase (`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`).

## Structure du code
- Marché : `pipeline/bin/fetch_market_data.py` + `pipeline/lib/market/` (`config.py`, `alpha.py`, `snapshot.py`).
- Météo : `pipeline/bin/fetch_weather_data.py` + `pipeline/lib/weather/` (`config.py`, `client.py`).
- `pipeline/lib/utils/persist.py` mutualise l’écriture Supabase.

## Tests locaux
1. Copier `.env.example` vers `.env` et renseigner les sections Alpha Vantage et/ou Open-Meteo.
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Lancer l’ingestion souhaitée :
   ```bash
   python pipeline/bin/fetch_market_data.py       # marché
   python pipeline/bin/fetch_weather_data.py      # météo
   ```
   - Ajustez `ALPHAVANTAGE_TIMEOUT` si l’API bourse est lente.
   - Modifiez `OPENMETEO_TIMEOUT` ou la liste `OPENMETEO_HOURLY_VARS` selon vos besoins.

## Déploiement Render
### Marchés (Alpha Vantage)
1. Connecter le repo à Render puis déployer :
   ```bash
   render blueprint deploy infra/render/cron-job.yaml --preview
   ```
2. Dans Render, définir en variables protégées :
   - `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `ALPHAVANTAGE_API_KEY`.
   - Ajuster `MARKET_SYMBOLS`, `INTRADAY_INTERVAL`, `ALPHAVANTAGE_TIMEOUT`.
3. Promouvoir l’aperçu après validation.

### Météo (Open-Meteo)
1. Déployer le blueprint dédié :
   ```bash
   render blueprint deploy infra/render/cron-weather.yaml --preview
   ```
2. Définir dans Render :
   - `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`.
   - `OPENMETEO_LATITUDE`, `OPENMETEO_LONGITUDE`, `OPENMETEO_LOCATION`, `OPENMETEO_HOURLY_VARS`, `OPENMETEO_TIMEOUT`.
3. Vérifier les logs (`Stored weather snapshot ...`) avant promotion.

## Opérations
- Les jobs Alpha Vantage retentent automatiquement jusqu’à 5 fois sur timeout, erreurs 5xx ou limites de fréquence ; surveiller les logs pour des échecs répétés.
- Le job Open-Meteo s’exécute chaque heure (cron `0 * * * *` par défaut). Ajustez le `schedule` pour synchroniser avec votre cadence de reporting.
- Conserver un inventaire des secrets dans `docs/secrets.md` et les faire tourner régulièrement.
- Ajoutez des alertes Render (email/webhook) sur les échecs afin de vérifier rapidement Supabase.
