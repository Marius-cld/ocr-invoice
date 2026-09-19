# si-project-ocr-invoice

Extrait la dernière ligne (ligne de total) de la 2ᵉ table de chaque facture PDF,
consolide le résultat dans un fichier Excel, puis compare chaque facture à la
précédente du même client.

## Structure

```
si-project-ocr-invoice/
├── pyproject.toml         # dépendances et points d'entrée
├── data/
│   ├── input/             # PDF à traiter
│   ├── output/            # output.xlsx et result.xlsx (générés, non versionnés)
│   └── rejected/          # PDF illisibles ou incomplets, déplacés ici (généré)
└── invoice_ocr/
    ├── settings.py        # chemins (surchargeables via INVOICE_OCR_DATA_DIR)
    ├── extraction.py      # lecture PDF (pdfplumber) + point d'entrée
    ├── export.py          # nettoyage des montants + écriture Excel
    └── comparison.py      # comparaison d'une facture à la précédente du même client
```

## Utilisation

```bash
pip install -e .
invoice-ocr            # data/input/*.pdf -> data/output/output.xlsx
invoice-ocr-compare    # output.xlsx -> data/output/result.xlsx (écart de Gross Worth)
```

Les chemins sont relatifs au dossier courant ; `INVOICE_OCR_DATA_DIR` les redirige
(utilisé par le conteneur Airflow de `si-docker-airflow`).

Un PDF sans date, sans client, avec une ligne de total inattendue ou illisible est
déplacé dans `data/rejected/` et n'arrête pas le lot. Si aucune facture n'est
exploitable, l'extraction échoue explicitement.
