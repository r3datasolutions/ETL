# Bitácora de versiones (CHANGELOG)

Registro de los puntos clave del proceso ETL. Cada entrada corresponde a un
*tag* de git con el que se puede recuperar ese estado exacto de los datos.

El formato sigue, de forma simplificada, la convención
[Keep a Changelog](https://keepachangelog.com/es/).

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
