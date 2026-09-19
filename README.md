# OCR de factures PDF

Extrait la dernière ligne (ligne de total) de la 2ᵉ table de chaque facture PDF,
consolide le résultat dans un fichier Excel, puis compare chaque facture à la
précédente du même client. Le pipeline peut être lancé en ligne de commande ou
planifié quotidiennement avec Airflow (Docker).

## Structure du projet

```
.
├── src/
│   └── invoice_ocr/
│       ├── settings.py         # chemins (surchargeables via INVOICE_OCR_DATA_DIR)
│       ├── extraction.py       # lecture PDF (pdfplumber) + point d'entrée
│       ├── export.py           # nettoyage des montants + écriture Excel
│       └── comparison.py       # comparaison d'une facture à la précédente du même client
├── airflow/
│   ├── dags/
│   │   └── invoice-ocr-dag.py  # DAG quotidien : extraction puis comparaison
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── start.sh
│   └── .env.example            # variables à copier dans .env
├── data/
│   ├── input/                  # PDF à traiter
│   ├── output/                 # output.xlsx et result.xlsx — généré, non versionné
│   └── rejected/               # PDF illisibles ou incomplets — généré, non versionné
├── pyproject.toml              # métadonnées et points d'entrée
└── requirements.txt
```

## Installation et utilisation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate
pip install -e .

invoice-ocr            # data/input/*.pdf -> data/output/output.xlsx
invoice-ocr-compare    # output.xlsx -> data/output/result.xlsx (écart de Gross Worth)
```

Les chemins sont relatifs au dossier courant : lancer les commandes depuis la
racine du projet. `INVOICE_OCR_DATA_DIR` redirige le dossier `data/` (utilisé par
le conteneur Airflow).

Un PDF sans date, sans client, avec une ligne de total inattendue ou illisible est
déplacé dans `data/rejected/` et n'arrête pas le lot. Si aucune facture n'est
exploitable, l'extraction échoue explicitement.

## Airflow (Docker)

```bash
cd airflow
cp .env.example .env    # renseigner AIRFLOW_ADMIN_USER et AIRFLOW_ADMIN_PASSWORD
docker compose up --build
```

L'interface est disponible sur <http://localhost:8081>. Le dossier `data/` est
monté dans le conteneur ; la base et les logs Airflow restent dans des volumes
nommés, hors du dépôt.
