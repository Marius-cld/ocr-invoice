"""Compare le montant de chaque facture à la précédente du même client."""

import logging

import pandas as pd

from invoice_ocr.settings import DATA_OUTPUT, OUTPUT_FILENAME, RESULT_FILENAME

logger = logging.getLogger(__name__)

AMOUNT_COL = "Gross Worth"


def compare_to_previous_invoice(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute la date, le montant précédents du même client et l'écart avec la facture courante."""
    result = df.sort_values(["Client", "Date"]).copy()

    grouped = result.groupby("Client")
    result["Date precedente"] = grouped["Date"].shift(1)
    result["Montant precedent"] = grouped[AMOUNT_COL].shift(1)

    result["Ecart"] = result[AMOUNT_COL] - result["Montant precedent"]
    result["Ecart %"] = (result["Ecart"] / result["Montant precedent"] * 100).round(2)

    columns = ["Client", "Date", AMOUNT_COL, "Date precedente", "Montant precedent", "Ecart", "Ecart %"]
    return result[columns].reset_index(drop=True)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    df = pd.read_excel(DATA_OUTPUT / OUTPUT_FILENAME)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df[AMOUNT_COL] = pd.to_numeric(df[AMOUNT_COL], errors="coerce")

    invalid = df["Date"].isna() | df[AMOUNT_COL].isna()
    if invalid.any():
        logger.warning("Ignoré (date ou montant invalide) : %s", ", ".join(df.loc[invalid, "Document"]))
        df = df[~invalid]

    compare_to_previous_invoice(df).to_excel(DATA_OUTPUT / RESULT_FILENAME, index=False)


if __name__ == "__main__":
    main()
