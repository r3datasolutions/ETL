# ETL — Arquitectura de Medallón (Bronze / Silver / Gold)

Proyecto de práctica que toma un conjunto de datos **en crudo** y lo hace pasar
por una **arquitectura de medallón** con Python (pandas), llevando un **registro
de versiones** en los puntos clave de cada capa. El resultado final alimenta un
análisis y visualización en **Power BI**.

Flujo: **Bronze (crudo) → Silver (limpio) → Gold (negocio) → Power BI**

---

## 🥉🥈🥇 Las capas del medallón

| Capa | Qué contiene | Formato |
|------|--------------|---------|
| 🥉 **Bronze** | Ingesta cruda: cada tabla tal como viene de la fuente, sin modificar | CSV (1 por tabla) |
| 🥈 **Silver** | Tablas limpias y estandarizadas: nulos, tipos, duplicados, nombres | CSV |
| 🥇 **Gold** | Tablas de negocio listas para Power BI: modelo estrella (hechos + dimensiones), agregados | CSV |

Cada capa **solo lee de la capa anterior y escribe en la suya** — nunca se
edita a mano. Así el proceso es 100 % reproducible por código.

---

## 📁 Estructura del proyecto

```
ETL/
├── data/
│   ├── bronze/       # Datos crudos: raw_tables.xlsx + 23 tablas en CSV (sin cambios)
│   ├── silver/       # Tablas limpias (1 CSV por entidad)
│   └── gold/         # Tablas de negocio, listas para Power BI
├── scripts/
│   ├── 00_explorar_datos.py    # Exploración (no modifica nada)
│   ├── 01_ingesta_bronze.py    # xlsx -> bronze/*.csv (extrae las 23 hojas)
│   ├── 02_bronze_a_silver.py   # limpieza (bronze → silver)
│   └── 03_silver_a_gold.py     # modelo estrella (silver → gold)
├── docs/
│   └── CHANGELOG.md  # Bitácora: qué cambió en cada versión
├── .venv/            # Entorno virtual (no se sube a git)
├── requirements.txt  # Librerías necesarias
└── README.md
```

## 📊 Datos de origen (Bronze)

`data/bronze/raw_tables.xlsx` — libro de Excel con **23 hojas** que simulan las
tablas de un negocio. El script `01_ingesta_bronze.py` las extrae a CSV. Grupos:

| Tablas | Descripción |
|--------|-------------|
| `CUST_MASTER`, `customer_contacts`, `user_details` | Clientes y contactos |
| `ORDERS_2025`, `ORDERS_2026`, `order_line_items` | Órdenes y sus líneas |
| `INVOICES`, `invoice_lines`, `payments` | Facturación y pagos |
| `products`, `subcategories`, `inventory` | Catálogo e inventario |
| `shipments`, `Sheet1` | Envíos |
| `CAMPAIGN_LOG`, `campaign_skus` | Campañas de marketing |
| `regions`, `cities`, `Address` | Geografía |
| `exchange_rates`, `sales_targets`, `security` | Referencia y control |

---

## 🔖 Estrategia de versionado

Cada **capa terminada** se marca con un *tag* de git para poder volver a ese
estado exacto en cualquier momento:

| Tag | Capa | Significado |
|-----|------|-------------|
| `v0-crudo` | 🥉 Bronze | Datos originales, sin tocar |
| `v1-silver` | 🥈 Silver | Tras limpieza (nulos, duplicados, tipos, formatos) |
| `v2-gold` | 🥇 Gold | Modelo de negocio listo para Power BI |

Ver el detalle de cada versión en [`docs/CHANGELOG.md`](docs/CHANGELOG.md).

---

## 🚀 Puesta en marcha

```bash
# 1. Activar el entorno virtual
source .venv/bin/activate

# 2. (Solo la primera vez, o al clonar en otra máquina) instalar librerías
pip install -r requirements.txt

# 3. Ejecutar los scripts en orden (bronze → silver → gold)
python scripts/01_ingesta_bronze.py     # xlsx  -> data/bronze/*.csv
python scripts/02_bronze_a_silver.py    # limpieza -> data/silver/*.csv
python scripts/03_silver_a_gold.py      # modelo  -> data/gold/*.csv
```

## 🔌 Conexión con Power BI

El modelo estrella vive en `data/gold/`. En Power BI: **Obtener datos → Carpeta →**
apunta a `data/gold/`, carga los 5 CSV y crea las relaciones:

- `fact_sales[CustomerID]` → `dim_customer[CustomerID]`
- `fact_sales[ProductName]` → `dim_product[ProductName]`
- `fact_sales[OrderDate]` → `dim_date[Date]`
- `fact_orders[CustomerID]` → `dim_customer[CustomerID]`
- `fact_orders[OrderDate]` → `dim_date[Date]`

## ⚙️ Convenciones

- **Bronze es de solo lectura**: nunca se edita a mano. Toda transformación se
  hace por código, para que el proceso sea 100 % reproducible.
- Cada script lee de una capa y escribe en la siguiente (`bronze → silver → gold`).
- Antes de cada tag, se anota el cambio en `docs/CHANGELOG.md`.
