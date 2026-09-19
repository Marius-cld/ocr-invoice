"""Lit les factures PDF et exporte date, client et ligne de total vers un fichier Excel."""

import datetime as dt
import logging
import re
import shutil
from pathlib import Path

import pdfplumber

from invoice_ocr.export import InvoiceRow, export_to_xlsx
from invoice_ocr.settings import DATA_INPUT, DATA_OUTPUT, DATA_REJECTED, OUTPUT_FILENAME

logger = logging.getLogger(__name__)

DATE_RE = re.compile(r"Date of issue:\s*(\d{2}/\d{2}/\d{4})")
TOTAL_CELLS = 4  # Type, Net Worth, VAT, Gross Worth


def extract_invoice_date(text: str) -> dt.date | None:
    """Extrait la date de facture (JJ/MM/AAAA), ou None si absente ou invalide."""
    match = DATE_RE.search(text)
    if match is None:
        return None
    try:
        return dt.datetime.strptime(match.group(1), "%d/%m/%Y").date()
    except ValueError:
        return None


def extract_client_name(page: pdfplumber.page.Page) -> str | None:
    """Nom du client cherché par position sous le label 'Client:', pas par regex."""
    words = page.extract_words()
    label = next((w for w in words if w["text"] == "Client:"), None)
    if label is None:
        return None

    below_label = [w for w in words if w["x0"] > label["x0"] - 5 and w["top"] > label["top"]]
    if not below_label:
        return None

    name_top = min(w["top"] for w in below_label)
    return " ".join(w["text"] for w in below_label if abs(w["top"] - name_top) < 1)


def extract_totals(page: pdfplumber.page.Page) -> list[str] | None:
    """Cellules non vides de la dernière ligne de la 2ᵉ table ; None si la forme est inattendue."""
    tables = page.extract_tables()
    if len(tables) < 2:
        return None

    for row in reversed(tables[1]):
        cells = [cell for cell in row if cell and cell.strip()]
        if cells:
            # Un nombre de cellules différent décalerait les montants sous les mauvaises colonnes
            return cells if len(cells) == TOTAL_CELLS else None
    return None


def read_invoice(pdf_path: Path) -> InvoiceRow:
    """Lit une facture ; lève ValueError si une donnée obligatoire manque."""
    with pdfplumber.open(pdf_path) as pdf:
        if not pdf.pages:
            raise ValueError("PDF sans page")
        page = pdf.pages[0]
        totals = extract_totals(page)
        date = extract_invoice_date(page.extract_text() or "")
        client = extract_client_name(page)

    if totals is None:
        raise ValueError("ligne de total introuvable ou inattendue")
    if date is None:
        raise ValueError("date introuvable")
    if client is None:
        raise ValueError("client introuvable")
    return InvoiceRow(pdf_path.stem, date, client, totals)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    rows: list[InvoiceRow] = []
    for pdf_path in sorted(DATA_INPUT.glob("*.pdf")):
        try:
            rows.append(read_invoice(pdf_path))
        except Exception as exc:  # un PDF illisible ne doit pas bloquer le lot
            logger.warning("Rejeté %s : %s", pdf_path.name, exc)
            DATA_REJECTED.mkdir(parents=True, exist_ok=True)
            shutil.move(pdf_path, DATA_REJECTED / pdf_path.name)

    if not rows:
        raise RuntimeError(f"Aucune facture exploitable dans {DATA_INPUT}")

    output_file = DATA_OUTPUT / OUTPUT_FILENAME
    export_to_xlsx(rows, output_file)
    logger.info("%d facture(s) exportée(s) vers %s", len(rows), output_file)


if __name__ == "__main__":
    main()
