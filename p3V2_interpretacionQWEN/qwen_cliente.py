import json
import ollama

if __package__:
    from .prompts_qwen import (
        PROMPT,
        FORMATO,
        PROMPT_CONFIRMACION,
        FORMATO_CONFIRMACION
    )
else:
    from prompts_qwen import (
        PROMPT,
        FORMATO,
        PROMPT_CONFIRMACION,
        FORMATO_CONFIRMACION
    )

from utilitiesP3 import PEDIDO, ACLARAR

MODELO = "qwen2.5:3b"


def interpretar(historial):

    respuesta = ollama.chat(
        model=MODELO,
        messages=[
            {"role": "system", "content": PROMPT}
        ] + historial,
        format=FORMATO,
        options={"temperature": 0},
        keep_alive=-1
    )

    resultado = json.loads(respuesta.message.content)

    if resultado["accion"] not in {PEDIDO, ACLARAR}:
        resultado["trago"] = None

    elif resultado["accion"] == PEDIDO:
        if not resultado["trago"]:
            resultado["accion"] = ACLARAR

    return resultado


def confirmar_pedido(texto):

    respuesta = ollama.chat(
        model=MODELO,
        messages=[
            {
                "role": "system",
                "content": PROMPT_CONFIRMACION
            },
            {
                "role": "user",
                "content": texto
            }
        ],
        format=FORMATO_CONFIRMACION,
        options={"temperature": 0},
        keep_alive=-1
    )

    resultado = json.loads(respuesta.message.content)

    return resultado