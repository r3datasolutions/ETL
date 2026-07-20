"""
anonimizar.py
-------------
Módulo de anonimización de datos personales (PII).

Se aplica en el paso Bronze -> Silver, de modo que a partir de la capa Silver
NINGUNA tabla contenga datos personales en claro. Así Silver y Gold pueden
versionarse en git sin exponer PII.

Dos técnicas, según lo que necesite el análisis:

  • ENMASCARAR: oculta parte del valor pero conserva lo útil.
      emma.adel@example.com -> e***@example.com   (conserva el dominio)
      +77-140-8078          -> ***-***-8078       (conserva los últimos 4)

  • SEUDONIMIZAR: sustituye por un código estable derivado de un hash.
      'Sarah Lin' -> 'Gestor_a1b2c3'
    Es DETERMINISTA: el mismo nombre da siempre el mismo seudónimo, así que
    los agrupamientos y las uniones siguen funcionando igual.

SAL (salt): el hash se calcula con una sal secreta. En producción debe venir
de una variable de entorno (fichero .env, NUNCA en git); aquí hay un valor por
defecto solo para que el proyecto de práctica sea reproducible.
"""

import hashlib
import os

import pandas as pd

# En producción: definir ANONIM_SALT en el entorno (.env, gestor de secretos).
SAL = os.environ.get("ANONIM_SALT", "etl-practica-sal-por-defecto")


def seudonimo(valor, prefijo: str = "ID") -> str:
    """Devuelve un código estable (mismo valor -> mismo seudónimo)."""
    if pd.isna(valor):
        return valor
    digest = hashlib.sha256(f"{SAL}{valor}".encode()).hexdigest()[:6]
    return f"{prefijo}_{digest}"


def enmascarar_email(valor) -> str:
    """emma.adel@example.com -> e***@example.com (conserva el dominio)."""
    if pd.isna(valor) or "@" not in str(valor):
        return valor
    local, _, dominio = str(valor).partition("@")
    return f"{local[:1]}***@{dominio}"


def enmascarar_telefono(valor) -> str:
    """+77-140-8078 -> ***-***-8078 (conserva los últimos 4 dígitos)."""
    if pd.isna(valor):
        return valor
    texto = str(valor)
    return f"***-***-{texto[-4:]}" if len(texto) >= 4 else "***"


# Registro de columnas con PII -> cómo tratarlas.
# La clave es el NOMBRE DE COLUMNA: se aplica en cualquier tabla donde aparezca.
COLUMNAS_PII = {
    "Email": enmascarar_email,
    "Phone": enmascarar_telefono,
    "ContactName": lambda v: seudonimo(v, "Contacto"),
    "AccountManager": lambda v: seudonimo(v, "Gestor"),
}

# Tablas que NO se anonimizan porque necesitan el dato real, y que por tanto
# quedan EXCLUIDAS de git (ver .gitignore y docs/SEGURIDAD.md).
#   - 'security': Power BI necesita el UserEmail real para el Row-Level Security.
TABLAS_EXCLUIDAS_DE_GIT = {"security"}


def anonimizar(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Aplica las reglas de PII. Devuelve (df, columnas_anonimizadas)."""
    aplicadas = []
    for columna, funcion in COLUMNAS_PII.items():
        if columna in df.columns:
            df[columna] = df[columna].map(funcion)
            aplicadas.append(columna)
    return df, aplicadas
