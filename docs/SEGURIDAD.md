# Seguridad del pipeline — marco de referencia

Convenciones de seguridad aplicadas a este pipeline ETL, y el criterio para
decidir **qué datos pueden versionarse en git y cuáles no**.

---

## 1. La regla de oro

> Todo lo que entra a un repositorio es **legible para siempre**: aunque borres
> el archivo después, sigue en el **historial de git**. Eliminarlo en un commit
> nuevo NO lo quita del pasado — habría que reescribir el historial
> (`git filter-repo`) y, aun así, el dato ya se considera comprometido.

Por eso se **clasifica antes de commitear**, no se limpia después.

## 2. Clasificación de datos (criterio de decisión)

| Nivel | Ejemplos en este proyecto | ¿Va a git? |
|-------|---------------------------|------------|
| 🟢 **Público** | `products`, `regions`, `exchange_rates` | Sí |
| 🟡 **Interno** | `sales_targets`, métricas agregadas | Sí, si el repo es privado |
| 🔴 **PII / confidencial** | `Email`, `Phone`, `ContactName`, `AccountManager`, `UserEmail` | **Nunca en claro** |

Dos preguntas definen todo:
1. **¿El repositorio es público o privado?**
2. **¿El dato identifica a una persona?**

> ℹ️ **Nota sobre este repositorio:** es público, pero los datos son
> **sintéticos** (material de un curso). No hay ninguna persona real expuesta.
> Las medidas de abajo se aplican igual, para entrenar el hábito con datos
> falsos antes de trabajar con datos reales.

## 3. Dónde se aplica en el pipeline

```
🥉 Bronze          🥈 Silver              🥇 Gold
(PII en claro) --> (PII anonimizada) --> (sin PII)
                        ▲
                        └── scripts/anonimizar.py
```

La anonimización ocurre en el paso **Bronze → Silver**. A partir de Silver,
ninguna tabla contiene datos personales en claro.

### ⚠️ Excepción consciente: Bronze sí se versiona en este proyecto

**Bronze contiene PII en claro** (`raw_tables.xlsx` y `bronze/customer_contacts.csv`)
y aun así está versionado en git. Es una decisión deliberada:

- El **objetivo didáctico** del repositorio es versionar los datos en *cada*
  etapa del medallón, y los datos son **sintéticos** (no hay persona real).
- **Con datos reales esto NO se haría.** La regla correcta sería:

  | | Datos de práctica (aquí) | Datos reales (producción) |
  |---|---|---|
  | Bronze con PII | Versionado en git | **Fuera de git** — vive en almacenamiento seguro (BD, S3, data lake) |
  | Silver / Gold | Versionados (anonimizados) | Versionados (anonimizados) |
  | Reproducibilidad | `git clone` basta | El pipeline reingesta desde la fuente segura |

Para migrar a la regla de producción bastaría con añadir al `.gitignore`:

```gitignore
data/bronze/          # PII en crudo: nunca en git
```

y documentar de dónde se obtiene la fuente.

### Técnica 1 — Enmascarar (conserva lo útil para el análisis)

| Columna | Antes | Después |
|---------|-------|---------|
| `Email` | `emma.adel@example.com` | `e***@example.com` (conserva el dominio) |
| `Phone` | `+77-140-8078` | `***-***-8078` (conserva los últimos 4) |

### Técnica 2 — Seudonimizar (hash estable)

| Columna | Antes | Después |
|---------|-------|---------|
| `ContactName` | `Emma Adel` | `Contacto_3f9a1c` |
| `AccountManager` | `Sarah Lin` | `Gestor_a1b2c3` |

Es **determinista**: el mismo valor produce siempre el mismo seudónimo, así que
agrupar por gestor o unir tablas **sigue funcionando igual**.

El hash usa una **sal secreta** (`ANONIM_SALT`). En producción debe venir de una
variable de entorno o gestor de secretos, **nunca del código**.

### Técnica 3 — Excluir de git (cuando el dato real es imprescindible)

Algunos datos **no se pueden anonimizar** porque el sistema necesita el valor real:

| Tabla | Por qué | Tratamiento |
|-------|---------|-------------|
| `security` (`UserEmail`) | Power BI necesita el email **real** para el Row-Level Security (RLS) | Excluida en `.gitignore`; se regenera localmente desde la fuente |

Este es el patrón general del mundo real: **git versiona el código; los datos
sensibles viven en almacenamiento seguro** (base de datos, S3, data lake) y el
pipeline los regenera.

## 4. Gestión de secretos

- Credenciales **nunca** en el código. Se leen de variables de entorno.
- El archivo `.env` está en `.gitignore`. Para compartir la *forma* de la
  configuración (sin valores) se usa un `.env.example`.

## 5. Otras medidas recomendadas (aún no implementadas)

| Mecanismo | Para qué |
|-----------|----------|
| **Puertas de validación** (Pandera / Great Expectations) | Que datos corruptos no avancen entre capas: tipos, rangos, claves únicas, integridad referencial |
| **Pre-commit + Gitleaks** | Impedir que se *commitee* un secreto por accidente |
| **`pip-audit` / Dependabot** | Detectar vulnerabilidades en las dependencias |
| **Hashes SHA-256 de Bronze** | Detectar alteraciones de los datos de origen |
| **Logging estructurado** | Auditoría de cada corrida del pipeline |
| **Power BI RLS** | Que cada usuario vea solo los datos de su región (tabla `security`) |
