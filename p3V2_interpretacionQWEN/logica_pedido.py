"""Consultas deterministas de la carta, preguntas y JSON final."""
import re
import sys
import unicodedata
from pathlib import Path

# utilitiesP3.py está en la carpeta superior (global).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utilitiesP3 import (
    SINONIMOS, TRAGOS, ATAJO_SOLO, RECETA, NOMBRES_DE_TRAGO,
    IGNORADAS, HIELO, CANTIDADES, PEDIDO,
    TONICA, AZUCAR, MENTA, TRIPLE_SEC, ANGOSTURA, CACHACA,
)


def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(
        letra for letra in texto
        if unicodedata.category(letra) != "Mn"
    )
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return texto.strip()


NOMBRES_INGREDIENTES = {}
for palabra, ingrediente in SINONIMOS.items():
    NOMBRES_INGREDIENTES.setdefault(ingrediente, palabra)

NOMBRES_INGREDIENTES.update({
    TONICA: "tonica",
    AZUCAR: "azucar",
    MENTA: "menta",
    TRIPLE_SEC: "triple sec",
    ANGOSTURA: "angostura",
    CACHACA: "cachaca"
})

ALIAS = {
    normalizar(palabra): ingrediente
    for palabra, ingrediente in SINONIMOS.items()
}
ALIAS.update({
    normalizar(nombre): ingrediente
    for ingrediente, nombre in NOMBRES_INGREDIENTES.items()
})

NOMBRES_COMPLETOS = {
    normalizar(nombre): id_trago
    for nombre, id_trago in NOMBRES_DE_TRAGO.items()
}
NOMBRES_COMPLETOS.update({
    "cuba libre": NOMBRES_DE_TRAGO["cuba"],
    "tom collins": NOMBRES_DE_TRAGO["tom"],
    "old fashioned": NOMBRES_DE_TRAGO["old"],
    "aperol spritz": NOMBRES_DE_TRAGO["spritz"]
})

NOMBRES_CLASICOS = {}
for nombre, id_trago in NOMBRES_COMPLETOS.items():
    if id_trago not in NOMBRES_CLASICOS:
        NOMBRES_CLASICOS[id_trago] = nombre
    elif len(nombre.split()) > len(NOMBRES_CLASICOS[id_trago].split()):
        NOMBRES_CLASICOS[id_trago] = nombre


def nombre_trago(id_trago):
    if id_trago in NOMBRES_CLASICOS:
        return NOMBRES_CLASICOS[id_trago]
    return " con ".join(
        NOMBRES_INGREDIENTES[i]
        for i in sorted(RECETA[id_trago])
    )


PALABRAS_BUSQUEDA = sorted(
    set(ALIAS) | set(NOMBRES_COMPLETOS),
    key=len,
    reverse=True
)
PATRON = re.compile(
    r"\b(?:" + "|".join(re.escape(p) for p in PALABRAS_BUSQUEDA) + r")\b"
)
PALABRAS_IGNORADAS = {
    normalizar(p) for p in IGNORADAS | HIELO | set(CANTIDADES)
}
PALABRAS_IGNORADAS.add("unk")


def extraer_componentes(texto):
    ingredientes = set()
    nombres = set()
    texto = normalizar(texto)
    for coincidencia in PATRON.finditer(texto):
        palabra = coincidencia.group()
        if palabra in NOMBRES_COMPLETOS:
            nombres.add(NOMBRES_COMPLETOS[palabra])
        elif palabra in ALIAS:
            ingredientes.add(ALIAS[palabra])
    restante = PATRON.sub(" ", texto)
    desconocidas = set(restante.split()) - PALABRAS_IGNORADAS
    return ingredientes, nombres, desconocidas


def resolver_trago(trago):
    """Devuelve (id_trago, opciones). Si falta aclarar, id_trago es None."""
    if not trago:
        return None, []
    texto = normalizar(trago)

    if " o " in texto:
        opciones = set()
        for alternativa in texto.split(" o "):
            id_trago, disponibles = resolver_trago(alternativa)
            if id_trago is not None:
                opciones.add(id_trago)
            opciones.update(disponibles)
        return None, sorted(opciones)

    partes = texto.split(" sin ")
    ingredientes, nombres, desconocidas = extraer_componentes(partes[0])
    if desconocidas:
        return None, []

    excluidos = set()
    for parte in partes[1:]:
        ing, tragos_excluidos, desconocidas = extraer_componentes(parte)
        if desconocidas or tragos_excluidos:
            return None, []
        excluidos.update(ing)

    if len(nombres) == 1:
        id_trago = next(iter(nombres))
        receta = RECETA[id_trago]
        if ingredientes.issubset(receta) and not receta.intersection(excluidos):
            return id_trago, []
        return None, []

    if len(nombres) > 1:
        return None, sorted(nombres)
    if not ingredientes:
        return None, []

    conjunto = frozenset(ingredientes)
    id_trago = TRAGOS.get(conjunto)
    if id_trago is not None:
        if not RECETA[id_trago].intersection(excluidos):
            return id_trago, []

    if len(conjunto) == 1:
        ingrediente = next(iter(conjunto))
        id_trago = ATAJO_SOLO.get(ingrediente)
        if id_trago is not None:
            if not RECETA[id_trago].intersection(excluidos):
                return id_trago, []

    opciones = [
        id_trago
        for combo, id_trago in TRAGOS.items()
        if ingredientes.issubset(combo)
        and not combo.intersection(excluidos)
    ]
    return None, sorted(opciones)


def preguntar_aclaracion(trago, opciones):
    if opciones:
        if len(opciones) == 1:
            nombre = nombre_trago(opciones[0])
            return f"¿Queres {nombre} o preferis otro trago?"
        nombres = [
            f"{i}. {nombre_trago(id_trago)}"
            for i, id_trago in enumerate(opciones, start=1)
        ]
        return "¿Cual de estas opciones preferis? " + " | ".join(nombres)
    if trago:
        return (
            "Esa combinacion no esta disponible "
            "o esta incompleta. ¿Que otro trago queres?"
        )
    return "¿Que te gustaria tomar?"


def obtener_cantidad_hielo(historial):
    cantidad = 1
    con_hielo = True
    for mensaje in historial:
        if mensaje["role"] != "user":
            continue
        texto = normalizar(mensaje["content"])
        texto = texto.replace("triple sec", "")
        for palabra in texto.split():
            if palabra in CANTIDADES:
                cantidad = CANTIDADES[palabra]
                break
        if re.search(r"\bsin hielos?\b", texto):
            con_hielo = False
        elif re.search(r"\bcon hielos?\b", texto):
            con_hielo = True
    return cantidad, con_hielo


def generar_json(accion, id_trago=None, cantidad=1, con_hielo=True):
    if accion != PEDIDO:
        id_trago = None
        cantidad = 1
        con_hielo = True
    return {
        "accion": accion,
        "trago_id": id_trago,
        "cantidad": cantidad,
        "con_hielo": con_hielo
    }
