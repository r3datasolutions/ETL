# Bitácora de versiones (CHANGELOG)

Registro de los puntos clave del proceso ETL. Cada entrada corresponde a un
*tag* de git con el que se puede recuperar ese estado exacto de los datos.

El formato sigue, de forma simplificada, la convención
[Keep a Changelog](https://keepachangelog.com/es/).

---

## [v0-crudo] — 2026-07-18

### Añadido
- Estructura inicial del proyecto (`data/`, `scripts/`, `docs/`).
- Dataset en crudo `data/raw/raw_tables.xlsx` (23 hojas) — fuente de verdad,
  no se modifica.
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
