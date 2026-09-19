"""Chemins et noms de fichiers, dossier data redirigeable via INVOICE_OCR_DATA_DIR."""

import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("INVOICE_OCR_DATA_DIR", "data"))
DATA_INPUT = DATA_DIR / "input"
DATA_OUTPUT = DATA_DIR / "output"
DATA_REJECTED = DATA_DIR / "rejected"

OUTPUT_FILENAME = "output.xlsx"
RESULT_FILENAME = "result.xlsx"
