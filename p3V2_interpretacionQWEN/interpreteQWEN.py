"""Programa principal: coordina el diálogo y las funciones de los módulos."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from p2_reconocimientop.reconocimiento_vosk import escucharVosk

if __package__:
    from .logica_pedido import (
        resolver_trago, preguntar_aclaracion, nombre_trago,
        obtener_cantidad_hielo, generar_json
    )
    from .qwen_cliente import interpretar, confirmar_pedido
else:
    from logica_pedido import (
        resolver_trago, preguntar_aclaracion, nombre_trago,
        obtener_cantidad_hielo, generar_json
    )
    from qwen_cliente import interpretar, confirmar_pedido

from utilitiesP3 import (
    PEDIDO, ACLARAR, CANCELAR, RECHAZO, CORTESIA_ACC, NO_ENTENDIDO
)


def main():
    try:
        while True:
            texto = escucharVosk()
            historial = [{"role": "user", "content": texto}]
            resultado = interpretar(historial)
            id_trago = None

            # Resolver el pedido y sus posibles aclaraciones.
            while resultado["accion"] in {PEDIDO, ACLARAR}:
                trago = resultado["trago"]
                id_trago, opciones = resolver_trago(trago)

                if resultado["accion"] == PEDIDO and id_trago is not None:
                    break

                if id_trago is not None:
                    opciones = [id_trago]
                resultado["accion"] = ACLARAR

                pregunta = preguntar_aclaracion(trago, opciones)
                print("Robot:", pregunta)
                historial.append({"role": "assistant", "content": pregunta})

                texto = escucharVosk()
                historial.append({"role": "user", "content": texto})

                # Selección numérica directa: no requiere otra llamada a Qwen.
                if texto.strip().isdigit():
                    seleccion = int(texto.strip())
                    if 1 <= seleccion <= len(opciones):
                        id_trago = opciones[seleccion - 1]
                        resultado = {"accion": PEDIDO, "trago": nombre_trago(id_trago)}
                        break

                resultado = interpretar(historial)

            # JSON definitivo y confirmación del usuario.
            if resultado["accion"] == PEDIDO and id_trago is not None:
                cantidad, con_hielo = obtener_cantidad_hielo(historial)
                pedido = generar_json(PEDIDO, id_trago, cantidad, con_hielo)
                print(json.dumps(pedido, ensure_ascii=False))

                nombre = nombre_trago(id_trago)
                hielo = "con hielo" if con_hielo else "sin hielo"

                while True:
                    print(f"¿Confirmas {cantidad} x {nombre} {hielo}? ")
                    texto = escucharVosk()
                    resultado_confirmacion = confirmar_pedido(texto)

                    print(json.dumps(resultado_confirmacion))

                    confirmacion = resultado_confirmacion["accion"]

                    if confirmacion == "CONFIRMADO":
                        # ENVIAR PEDIDO POR UART: utilizar el diccionario pedido.
                        break
                    elif confirmacion == "CANCELADO":
                        break
                    else:
                        print("No entendi la confirmacion.")

            else:
                pedido = generar_json(resultado["accion"])
                print(json.dumps(pedido, ensure_ascii=False))
                if resultado["accion"] == CANCELAR:
                    print("Pedido cancelado.")
                elif resultado["accion"] == RECHAZO:
                    print("De acuerdo, no preparo nada.")
                elif resultado["accion"] == CORTESIA_ACC:
                    print("De nada!")
                elif resultado["accion"] == NO_ENTENDIDO:
                    print("No te entendi. Podes repetirlo?")

    except KeyboardInterrupt:
        print("\nPrograma detenido.")


if __name__ == "__main__":
    main()
