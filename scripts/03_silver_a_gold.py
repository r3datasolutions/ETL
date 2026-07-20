"""
03_silver_a_gold.py
------------------
Capa GOLD (modelo de negocio para Power BI).

Lee las tablas limpias de data/silver/ y construye un MODELO ESTRELLA
(dimensiones + hechos) en data/gold/, listo para conectar en Power BI.

Tablas resultantes:
  Dimensiones:
    - dim_customer : 1 fila por cliente (con Ciudad y Región)
    - dim_product  : 1 fila por producto
    - dim_date     : calendario 2025-2026 (con meses/días en español)
  Hechos:
    - fact_orders  : órdenes 2025 + 2026 unidas (grano: 1 orden)
    - fact_sales   : líneas de venta enriquecidas (grano: 1 línea)

Uso:
    source .venv/bin/activate
    python scripts/03_silver_a_gold.py
"""

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
DIR_SILVER = RAIZ / "data" / "silver"
DIR_GOLD = RAIZ / "data" / "gold"

MESES_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre",
    11: "Noviembre", 12: "Diciembre",
}
DIAS_ES = {
    0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
    4: "Viernes", 5: "Sábado", 6: "Domingo",
}


def leer(nombre: str) -> pd.DataFrame:
    return pd.read_csv(DIR_SILVER / f"{nombre}.csv")


def dim_customer() -> pd.DataFrame:
    """Cliente + su geografía (Ciudad, Región) vía Address y cities."""
    cm = leer("CUST_MASTER")
    addr = leer("Address")[["AddressID", "CityName"]]
    cities = leer("cities")  # CityName, RegionName

    dim = (cm
           .merge(addr, on="AddressID", how="left")
           .merge(cities, on="CityName", how="left")
           .rename(columns={"CityName": "City", "RegionName": "Region"}))

    return dim[["CustomerID", "CustomerName", "Segment", "AccountManager",
                "PaymentTerms", "City", "Region"]]


def dim_product() -> pd.DataFrame:
    """Catálogo de productos."""
    pr = leer("products")
    return pr[["ProductCode", "ProductName", "Brand", "SubcategoryName",
               "UnitPrice", "PrimarySupplier"]]


def dim_date() -> pd.DataFrame:
    """Calendario continuo que cubre todo el rango de datos."""
    rango = pd.date_range("2025-01-01", "2026-12-31", freq="D")
    d = pd.DataFrame({"_fecha": rango})
    d["Date"] = d["_fecha"].dt.strftime("%Y-%m-%d")
    d["Year"] = d["_fecha"].dt.year
    d["Quarter"] = "T" + d["_fecha"].dt.quarter.astype(str)
    d["MonthNum"] = d["_fecha"].dt.month
    d["MonthName"] = d["MonthNum"].map(MESES_ES)
    d["MonthYear"] = d["_fecha"].dt.strftime("%Y-%m")
    d["DayName"] = d["_fecha"].dt.dayofweek.map(DIAS_ES)
    return d.drop(columns="_fecha")


def fact_orders(mapa_cliente: pd.Series) -> pd.DataFrame:
    """Une ORDERS_2025 + ORDERS_2026 alineando el esquema común."""
    o25 = leer("ORDERS_2025")
    o26 = leer("ORDERS_2026")

    # Esquema común: descarta columnas de linaje solo-2025 (LegacyRef, SourceFile)
    comunes = [c for c in o25.columns if c in o26.columns]
    fo = pd.concat([o25[comunes], o26[comunes]], ignore_index=True)

    fo["OrderYear"] = pd.to_datetime(fo["OrderDate"], errors="coerce").dt.year
    # FK al cliente (las órdenes traen nombre, no ID)
    fo["CustomerID"] = fo["CustomerName"].map(mapa_cliente)
    return fo


def fact_sales(fo: pd.DataFrame) -> pd.DataFrame:
    """Líneas de venta enriquecidas con fecha y cliente de su orden."""
    oli = leer("order_line_items")
    enriquecidas = oli.merge(
        fo[["OrderID", "OrderDate", "CustomerID"]], on="OrderID", how="left")
    return enriquecidas


def procesar():
    DIR_GOLD.mkdir(exist_ok=True)
    print(f"Silver: {DIR_SILVER}\nGold:   {DIR_GOLD}\n")

    # Mapa nombre_cliente -> CustomerID (para poner la FK en los hechos)
    cm = leer("CUST_MASTER")
    mapa_cliente = cm.drop_duplicates("CustomerName").set_index("CustomerName")["CustomerID"]

    tablas = {
        "dim_customer": dim_customer(),
        "dim_product": dim_product(),
        "dim_date": dim_date(),
    }
    tablas["fact_orders"] = fact_orders(mapa_cliente)
    tablas["fact_sales"] = fact_sales(tablas["fact_orders"])

    for nombre, df in tablas.items():
        df.to_csv(DIR_GOLD / f"{nombre}.csv", index=False)
        print(f"✓ {nombre:<14} {df.shape[0]:>4} filas x {df.shape[1]:>2} cols")

    # --- Avisos de calidad ---
    print("\n--- Comprobaciones ---")
    fs = tablas["fact_sales"]
    prod_gold = set(tablas["dim_product"]["ProductName"])
    huerfanos = sorted(set(fs["ProductName"].dropna()) - prod_gold)
    if huerfanos:
        print(f"⚠ {len(huerfanos)} producto(s) en fact_sales sin ficha en dim_product:")
        for p in huerfanos:
            print(f"    - {p}")
    sin_cliente = int(tablas["fact_orders"]["CustomerID"].isna().sum())
    print(f"• Órdenes sin CustomerID mapeado: {sin_cliente}")

    print("\nListo: modelo estrella generado en data/gold/")


if __name__ == "__main__":
    procesar()
