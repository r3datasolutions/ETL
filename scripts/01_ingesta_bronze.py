"""
01_ingesta_bronze.py
--------------------
Capa BRONZE (ingesta cruda).

Extrae cada hoja del libro de Excel original a un CSV independiente dentro de
data/bronze/, SIN aplicar ninguna transformación. El objetivo del bronce es
tener una copia fiel de la fuente, pero ya en un formato tabla-por-archivo con
el que las siguientes capas (silver, gold) puedan trabajar cómodamente.

Uso:
    source .venv/bin/activate
    python scripts/01_ingesta_bronze.py
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO_FUENTE = RAIZ / "data" / "bronze" / "raw_tables.xlsx"
DIR_BRONZE = RAIZ / "data" / "bronze"


def ingestar():
    print(f"Fuente: {ARCHIVO_FUENTE}\n")
    libro = pd.ExcelFile(ARCHIVO_FUENTE)

    for hoja in libro.sheet_names:
        df = pd.read_excel(libro, hoja)
        destino = DIR_BRONZE / f"{hoja}.csv"
        # index=False para no añadir una columna de índice artificial
        df.to_csv(destino, index=False)
        print(f"✓ {hoja:<20} -> {destino.name:<24} ({df.shape[0]} filas)")

    print(f"\nListo: {len(libro.sheet_names)} tablas extraídas a data/bronze/")


if __name__ == "__main__":
    ingestar()
