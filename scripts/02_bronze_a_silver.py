"""
02_bronze_a_silver.py
--------------------
Capa SILVER (limpieza y estandarización).

Lee cada tabla de data/bronze/ y le aplica reglas de limpieza generales,
escribiendo el resultado en data/silver/. NUNCA modifica bronze.

Reglas aplicadas a cada tabla:
  1. Quitar espacios sobrantes en columnas de texto.
  2. Eliminar columnas técnicas de staging (hash_key, source_id).
  3. Eliminar columnas 100 % vacías (p. ej. GiftMessage).
  4. Normalizar columnas de fecha a formato ISO 'YYYY-MM-DD'.
  5. Eliminar filas duplicadas exactas.
  6. Anonimizar columnas con datos personales (ver scripts/anonimizar.py).
Reglas específicas:
  - 'Sheet1' se excluye por ser un duplicado exacto de 'shipments'.

Uso:
    source .venv/bin/activate
    python scripts/02_bronze_a_silver.py
"""

from pathlib import Path

import pandas as pd

from anonimizar import anonimizar

RAIZ = Path(__file__).resolve().parent.parent
DIR_BRONZE = RAIZ / "data" / "bronze"
DIR_SILVER = RAIZ / "data" / "silver"

# Tablas de bronce que NO pasan a silver (duplicados u obsoletas)
EXCLUIR = {"Sheet1"}  # duplicado exacto de 'shipments'

# Columnas técnicas de staging que se eliminan si aparecen
COLS_TECNICAS = {"hash_key", "source_id"}

# Columnas que representan una fecha completa (se normalizan a 'YYYY-MM-DD').
# 'Period' queda fuera a propósito: es un mes ('YYYY-MM'), no una fecha.
COLS_FECHA = {
    "StartDate", "EndDate", "Date", "InvoiceDate",
    "OrderDate", "ShipDate", "DeliveryDate", "PayDate",
}


def limpiar_tabla(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Aplica las reglas de limpieza y devuelve (df_limpio, lista_de_cambios)."""
    cambios: list[str] = []

    # 1) Quitar espacios sobrantes en textos
    for col in df.columns:
        if pd.api.types.is_string_dtype(df[col]):
            df[col] = df[col].str.strip()

    # 2) Eliminar columnas técnicas de staging
    tecnicas = [c for c in df.columns if c in COLS_TECNICAS]
    if tecnicas:
        df = df.drop(columns=tecnicas)
        cambios.append(f"col. técnicas eliminadas: {tecnicas}")

    # 3) Eliminar columnas 100 % vacías
    vacias = [c for c in df.columns if df[c].isna().all()]
    if vacias:
        df = df.drop(columns=vacias)
        cambios.append(f"col. vacías eliminadas: {vacias}")

    # 4) Normalizar fechas a 'YYYY-MM-DD' (los valores inválidos quedan como nulos)
    fechas = [c for c in df.columns if c in COLS_FECHA]
    for col in fechas:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")
    if fechas:
        cambios.append(f"fechas normalizadas: {fechas}")

    # 5) Eliminar filas duplicadas exactas
    n_dup = int(df.duplicated().sum())
    if n_dup:
        df = df.drop_duplicates()
        cambios.append(f"filas duplicadas eliminadas: {n_dup}")

    # 6) Anonimizar datos personales (PII)
    df, pii = anonimizar(df)
    if pii:
        cambios.append(f"🔒 PII anonimizada: {pii}")

    return df, cambios


def procesar():
    DIR_SILVER.mkdir(exist_ok=True)
    print(f"Bronze: {DIR_BRONZE}\nSilver: {DIR_SILVER}\n")

    for archivo in sorted(DIR_BRONZE.glob("*.csv")):
        nombre = archivo.stem
        if nombre in EXCLUIR:
            print(f"⊘ {nombre:<20} excluido (duplicado de 'shipments')")
            continue

        df = pd.read_csv(archivo)
        forma_ini = df.shape
        limpio, cambios = limpiar_tabla(df)
        limpio.to_csv(DIR_SILVER / f"{nombre}.csv", index=False)

        resumen = " | ".join(cambios) if cambios else "sin cambios estructurales"
        print(f"✓ {nombre:<20} {forma_ini[0]}x{forma_ini[1]} -> "
              f"{limpio.shape[0]}x{limpio.shape[1]}  | {resumen}")

    print("\nListo: capa Silver generada en data/silver/")


if __name__ == "__main__":
    procesar()
