# Bitácora de versiones (CHANGELOG)

Registro de los puntos clave del proceso ETL. Cada entrada corresponde a un
*tag* de git con el que se puede recuperar ese estado exacto de los datos.

El formato sigue, de forma simplificada, la convención
[Keep a Changelog](https://keepachangelog.com/es/).

---

## [v2-gold] — 2026-07-19 · 🥇 Gold (modelo estrella)

### Añadido
- `scripts/03_silver_a_gold.py`: construye el modelo dimensional en `data/gold/`.
- **Dimensiones**: `dim_customer` (61, con Ciudad/Región), `dim_product` (63),
  `dim_date` (730 días, 2025-2026, meses/días en español).
- **Hechos**: `fact_orders` (80 = ORDERS_2025 + ORDERS_2026 **unidas**),
  `fact_sales` (200 líneas, enriquecidas con `OrderDate` y `CustomerID`).

### Decisiones de modelado
- Unión de órdenes: se conserva el **esquema común**; se descartan las columnas
  solo-2025 de linaje (`LegacyRef`, `SourceFile`). Se añade `OrderYear`.
- Los hechos llevan `CustomerID` como FK (las órdenes venían con nombre).
- 3 productos descontinuados (`Legacy Widget X9`, `Old Model A0`,
  `Retired Cable Z1`) aparecen en ventas pero no en `dim_product` — se
  documentan como huérfanos esperados (productos retirados del catálogo).

---

## [v1-silver] — 2026-07-19 · 🥈 Silver (limpieza)

### Añadido
- `scripts/02_bronze_a_silver.py`: limpia cada tabla de bronze y escribe el
  resultado en `data/silver/` (22 tablas).

### Cambiado / Limpieza
- **Espacios** sobrantes recortados en columnas de texto.
- **Fechas** normalizadas a formato ISO `YYYY-MM-DD`. `OrderDate` (órdenes)
  pierde el componente de hora: se usa grano de día para el análisis.
- **Columnas técnicas** de staging eliminadas: `hash_key`, `source_id`
  (en `CUST_MASTER` y `products`).
- **Columnas 100 % vacías** eliminadas: `GiftMessage` (en ORDERS_2025/2026).

### Eliminado
- Tabla `Sheet1` descartada: era un duplicado exacto de `shipments`.

### Pendiente (se resuelve en capas posteriores)
- Unión de `ORDERS_2025` + `ORDERS_2026` (esquemas distintos) → capa Gold.
- Nulos legítimos conservados a propósito: `products.UnitPrice`,
  `shipments.DeliveryDate` (no se inventan valores).

---

## [Sin tag] — 2026-07-19 · Adopción de arquitectura de medallón

### Cambiado
- Reorganización de `data/` a capas de medallón: `raw/` → `bronze/`;
  `interim/` y `processed/` → `silver/` y `gold/`.
- Documentación (`README.md`) actualizada al modelo Bronze/Silver/Gold.
- Nuevo esquema de tags: `v0-crudo` (bronze) → `v1-silver` → `v2-gold`.

### Añadido
- `scripts/01_ingesta_bronze.py`: extrae las 23 hojas de `raw_tables.xlsx`
  a `data/bronze/*.csv` sin modificar (una tabla por archivo).

> Nota: esto sigue siendo la capa Bronze (datos crudos), por eso no genera un
> tag de milestone nuevo. El próximo tag será `v1-silver` tras la limpieza.

---

## [v0-crudo] — 2026-07-18 · 🥉 Bronze

### Añadido
- Estructura inicial del proyecto (`data/`, `scripts/`, `docs/`).
- Dataset en crudo `raw_tables.xlsx` (23 hojas) — fuente de verdad, no se modifica.
- Entorno de Python (`requirements.txt`: pandas, openpyxl).
- Documentación base (`README.md`, este `CHANGELOG.md`).

---

<!--
Plantilla para las próximas versiones — copia este bloque hacia arriba:

## [vX-nombre] — AAAA-MM-DD

### Añadido
- ...

### Cambiado
- ...

### Corregido / Limpieza
- ...
-->
