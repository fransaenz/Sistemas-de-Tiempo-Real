from rapidfuzz import process, fuzz
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from vocabulario import VOCABULARIO


def corregir_por_similitud(texto_escuchado):
    palabras = texto_escuchado.split()
    resultado = []

    for p in palabras:

        if p in VOCABULARIO:
            resultado.append(p)
            continue

        coincidencia = process.extractOne(
            p, VOCABULARIO, scorer=fuzz.ratio
        )

        if coincidencia and coincidencia[1] >= 65:
            resultado.append(coincidencia[0])
        else: continue

    return " ".join(resultado)