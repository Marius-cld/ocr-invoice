#!/usr/bin/env bash
# Migre la base, écrit le mot de passe admin puis lance les composants Airflow.
set -euo pipefail

airflow db migrate

python - <<'PY' > "${AIRFLOW_HOME}/simple_auth_manager_passwords.json.generated"
import json, os
print(json.dumps({os.environ["AIRFLOW_ADMIN_USER"]: os.environ["AIRFLOW_ADMIN_PASSWORD"]}))
PY

airflow api-server -p 8080 &
airflow dag-processor &
airflow scheduler &

# Si un composant s'arrête, le conteneur s'arrête aussi et restart: always le relance
wait -n
exit 1
