# ETL — Limpieza, Transformación y Versionado de Datos

Proyecto de práctica que toma un conjunto de datos **en crudo** y le aplica
procesos de **limpieza** y **transformación** con Python (pandas), llevando un
**registro de versiones** en los puntos clave del proceso. El resultado final
alimenta un análisis y visualización en **Power BI**.

Flujo: **crudo → limpieza → transformación → análisis → Power BI**

---

## 📁 Estructura del proyecto

```
ETL/
├── data/
│   ├── raw/          # Datos EN CRUDO — nunca se modifican (fuente de verdad)
│   ├── interim/      # Datos intermedios (limpieza parcial)
│   └── processed/    # Datos finales, listos para Power BI
├── scripts/          # Scripts de Python (.py) de limpieza y transformación
├── docs/
│   └── CHANGELOG.md  # Bitácora: qué cambió en cada versión
├── .venv/            # Entorno virtual (no se sube a git)
├── requirements.txt  # Librerías necesarias
└── README.md
```

## 📊 Datos de origen

`data/raw/raw_tables.xlsx` — libro de Excel con **23 hojas** que simulan las
tablas de un negocio (ventas, clientes, productos, etc.). Principales:

| Hoja | Descripción |
|------|-------------|
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

Cada **etapa clave** se marca con un *tag* de git para poder volver a ese
estado exacto de los datos en cualquier momento:

| Tag | Significado |
|-----|-------------|
| `v0-crudo` | Datos originales, sin tocar |
| `v1-limpio` | Tras limpieza (nulos, duplicados, tipos, formatos) |
| `v2-transformado` | Tras transformaciones (uniones, columnas nuevas, agregaciones) |
| `v3-listo-analisis` | Dataset final que alimenta Power BI |

Ver el detalle de cada versión en [`docs/CHANGELOG.md`](docs/CHANGELOG.md).

---

## 🚀 Puesta en marcha

```bash
# 1. Activar el entorno virtual
source .venv/bin/activate

# 2. (Solo la primera vez, o al clonar en otra máquina) instalar librerías
pip install -r requirements.txt

# 3. Ejecutar un script de la carpeta scripts/
python scripts/nombre_del_script.py
```

## ⚙️ Convenciones

- **`data/raw/` es de solo lectura**: nunca se edita a mano. Toda transformación
  se hace por código, para que el proceso sea 100 % reproducible.
- Cada script deja su salida en `data/interim/` o `data/processed/`.
- Antes de cada tag, se anota el cambio en `docs/CHANGELOG.md`.
