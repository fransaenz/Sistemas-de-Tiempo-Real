import unicodedata

# atajo para crear una clase sin constructor (se usa para la clase Resultado)
from dataclasses import dataclass 
# Optional[int] significa 'un int o None' (solo documentación)
from typing import Optional 
# vocabulario de palabras que Vosk reconoce, sacado de la p2
from vocabulario import VOCABULARIO

# Ingredientes / Bebidas que se utilizan en los tragos. Cada uno tiene un ID único (1..N).
# Si el robot suma una bebida nueva, agregarla al final de este bloque.
(VODKA, FERNET, CAMPARI, COCA, SPRITE, NARANJA, CERVEZA, VINO, 
 GANCIA, LIMON, GIN, TONICA, RON, WHISKY, TEQUILA, VERMUT, 
 APEROL, CHAMPAGNE, SIDRA, BAILEYS, LICOR, POMELO,
 AZUCAR, MENTA, SODA, TRIPLE_SEC, ANGOSTURA, CACHACA) = range(1, 29)

# Palabra o frase que dice el usuario -> ID de bebida
SINONIMOS = {
    "vodka": VODKA, "vodca": VODKA, "vodquita": VODKA, "vodkita": VODKA,
    "smirnoff": VODKA, "absolut": VODKA, "skyy": VODKA,

    "fernet": FERNET, "fernecito": FERNET, "ferno": FERNET, "branca": FERNET,
    "fernando": FERNET, "ferne": FERNET, "fernandito": FERNET,
  
    "campari": CAMPARI,  "gancia": GANCIA,
    "tonic": TONICA, "tonica": TONICA, "baileys": BAILEYS,

    "coca": COCA, "coca cola": COCA, "cola": COCA, "coquita": COCA,
    
    "sprite": SPRITE, "spray": SPRITE, "sprayt": SPRITE, "esprai": SPRITE,

    "naranja": NARANJA,  "naranjada": NARANJA, "jugo": NARANJA, "juguito": NARANJA,

    "cerveza": CERVEZA, "birra": CERVEZA, "rabi": CERVEZA, "pinta": CERVEZA, "ipa": CERVEZA,
    "lata": CERVEZA, "porron": CERVEZA, "porroncito": CERVEZA, "quilmes": CERVEZA, 
    "brahma": CERVEZA, "stella": CERVEZA, "artois": CERVEZA, "heineken": CERVEZA, 
    "corona": CERVEZA, "andes": CERVEZA, "cervecita": CERVEZA, "birrin": CERVEZA,

    "vino": VINO, "tinto": VINO, "blanco": VINO, "veneco": VINO, 
    "malbec": VINO, "cabernet": VINO, "merlot": VINO, "totin": VINO, 

    "gin": GIN, "beefeater": GIN, "tanqueray": GIN, "ginebra": GIN, "ginebrita": GIN, "ginebrita": GIN,
    
    "ron": RON, "havana": RON, "bacardi": RON, "club": RON,
    
    "whisky": WHISKY, "tequila": TEQUILA, "quilate": TEQUILA, 
    
    "jagger": LICOR, "jagermeister": LICOR, "licor": LICOR,
    
    "vermut": VERMUT, "vermu": VERMUT, "aperol": APEROL,
    
    "champan": CHAMPAGNE, "champagne": CHAMPAGNE, "sidra": SIDRA,
    
    "pomelo" : POMELO, "limon": LIMON, "lima": LIMON, "soda": SODA,
    
}

# Si dicen SOLO esta bebida, se entiende este trago (lo elegís vos, uno por uno).
# Las bebidas que no figuren acá (ej. vodka) piden aclarar.
ATAJO_SOLO = {
    FERNET: 2,    # "fernet"  -> fernet con coca
    CAMPARI: 4,   # "campari" -> campari naranja
    GIN: 5,       # "gin"     -> gin tonic
}

#  bebidas -> ID de trago (el que se manda por UART)
TRAGOS = {
    frozenset({VODKA, NARANJA}): 1,                        # Vodka con jugo de naranja
    frozenset({FERNET, COCA}): 2,                          # Fernet con coca
    frozenset({VODKA, SPRITE}): 3,                         # Vodka con sprite
    frozenset({CAMPARI, NARANJA}): 4,                      # Campari
    frozenset({GIN, TONICA}): 5,                           # Gin Tonic
    frozenset({RON, COCA}): 6,                             # Ron Cola (Cuba libre)
    frozenset({VINO, POMELO}): 7,                          # Vino con pomelo
    frozenset({CERVEZA, LIMON}): 8,                        # Cerveza con limón
    # --- tragos clásicos (recetas estándar IBA, simplificadas) ---
    frozenset({GIN, CAMPARI, VERMUT}): 9,                  # negroni
    frozenset({RON, LIMON, AZUCAR, MENTA, SODA}): 10,      # mojito
    frozenset({TEQUILA, TRIPLE_SEC, LIMON}): 11,           # margarita
    frozenset({RON, LIMON, AZUCAR}): 12,                   # daiquiri
    frozenset({CACHACA, LIMON, AZUCAR}): 13,               # caipirinha
    frozenset({VODKA, LIMON, AZUCAR}): 14,                 # caipiroska
    frozenset({GIN, LIMON, AZUCAR, SODA}): 15,             # tom collins
    frozenset({WHISKY, AZUCAR, ANGOSTURA}): 16,            # old fashioned
    frozenset({APEROL, CHAMPAGNE, SODA}): 17,              # aperol spritz
    # --- tragos de una sola bebida ---
    frozenset({CERVEZA}): 18,                              # cerveza
    frozenset({VINO}): 19,                                 # vino
    frozenset({SIDRA}): 20,                                # sidra
    frozenset({CHAMPAGNE}): 21,                            # champagne
    frozenset({BAILEYS}): 22,                              # baileys
    frozenset({TEQUILA}): 23,                              # tequila
    frozenset({WHISKY}): 24,                               # whisky
    frozenset({VERMUT}): 25,                               # vermut
    frozenset({RON}): 26,                                  # ron
    frozenset({LICOR}): 27,                                # licor
    frozenset({GANCIA}): 28,                               # gancia
    # --- tragos sin alcohol ---
    frozenset({POMELO}): 29,                               # jugo de pomelo
    frozenset({COCA}): 30,                                 # coca
    frozenset({SPRITE}): 31,                               # sprite
    frozenset({NARANJA}): 32,                              # jugo de naranja
    frozenset({SODA}): 33,                                 # soda
}

# Bebidas que aparecen en algún trago (se calcula sola)
EN_CARTA = set().union(*TRAGOS)

# Al revés que TRAGOS: ID de trago -> sus bebidas
RECETA = {id_trago: combo for combo, id_trago in TRAGOS.items()}

# Nombre de un trago (una palabra del vocabulario) -> ID de trago
NOMBRES_DE_TRAGO = {
    "cuba": 6, "libre": 6,          # cuba libre = ron + coca
    "negroni": 9,
    "mojito": 10,
    "margarita": 11,
    "daiquiri": 12, "daikiri": 12,
    "caipirinha": 13, "caipiriña": 13,
    "caipiroska": 14, "caipiroshka": 14, "caipirosca": 14,
    "tom": 15, "collins": 15,
    "old": 16, "fashioned": 16,
    "spritz": 17,
}

# Resto de las palabras del vocabulario, por categoría

# Palabras que SÍ cambian el resultado
GENERICOS = {"trago", "chupi", "escabio", "escabiar", "ronda", "fizz"}   # piden algo sin decir qué
HIELO = {"hielo", "hielos"}
NEGACIONES = {"no", "tampoco", "nada", "ninguno", "ninguna", "nunca", "jamas"}
EXCLUSION = {"sin"}
CANCELACIONES = {"cancelar", "cancela", "cancelamelo", "cancelalo", 
                 "detener", "detenete", "detenelo", 
                 "frenar", "frename", "frenalo", "frena",
                 "parar", "paralo", "parate",
                 "espera", "esperame", "esperate", "basta", 
                 "corta", "cortame", "cortalo", "alto"}
CORTESIA = {"muchas", "gracias"}
REPETIR = {"otra", "otro", "repetir", "repeti", "repetilo",
            "repite", "igual", "idem", "lo mismo", "otra vez"}
CANTIDADES = {"un": 1, "una": 1, "dos": 2, "doble": 2, "tres": 3, "triple": 3, "cuatro": 4}

# Palabras que NO cambian el resultado, se ignoran
IGNORADAS = {
    "vaso", "vasos", "jarra", "carton", "tetrabrik", "tetra",   # recipientes
    "mas", "menos", "poco", "mucho",                            # modificadores
    "quiero", "dame", "servime", "traeme", "prepara", "preparame",
    "el", "la", "los", "las", "con", "de", "del", "para", "por",
    "y", "o", "favor", "unos", "unas",
}

DESCONOCIDA = {"[unk]"}
 
CONOCIDAS = (set(SINONIMOS) | set(NOMBRES_DE_TRAGO) | GENERICOS | HIELO
            | NEGACIONES | EXCLUSION | CANCELACIONES | CORTESIA | REPETIR
            | set(CANTIDADES) | IGNORADAS | DESCONOCIDA)

PEDIDO = "PEDIDO"
CANCELAR = "CANCELAR"
RECHAZO = "RECHAZO"
REPETIR_ULTIMO = "REPETIR"
FUERA_DE_CARTA = "FUERA_DE_CARTA"
ACLARAR = "ACLARAR"
CORTESIA_ACC = "CORTESIA"
NO_ENTENDIDO = "NO_ENTENDIDO"
 
ACCIONES = {PEDIDO, CANCELAR, RECHAZO, REPETIR_ULTIMO, FUERA_DE_CARTA,
            ACLARAR, CORTESIA_ACC, NO_ENTENDIDO}

#Clase Resultado, es el tipo de objeto que devuelve la función interpretar(). 
# Contiene la acción (PEDIDO, CANCELAR, etc.) y los parámetros del pedido si corresponde.
@dataclass
class Resultado:
    accion: str
    trago_id: Optional[int] = None   # solo si accion == PEDIDO
    cantidad: int = 1                # por defecto 1
    con_hielo: bool = True           # por defecto con hielo
    desconocidas: int = 0     

# Funcion Normalizar: convierte el texto a minúsculas, elimina tildes y 
# signos de puntuación, y reemplaza el comodín [unk] por un espacio. 
# Esto facilita la interpretación del texto por parte del sistema.
def normalizar(texto):
    """Minúsculas, sin tildes ni signos, sin el comodín [unk]."""
    texto = texto.lower().replace("[unk]", " ")
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    texto = "".join(c if c.isalnum() or c == " " else " " for c in texto)
    return " ".join(texto.split())

#Funcion interpretar: toma un texto de entrada y devuelve un objeto Resultado.
# La función analiza el texto palabra por palabra, identificando bebidas, cantidades, negaciones y otros comandos.
def interpretar(texto):
    """Texto -> Resultado. Siempre devuelve una acción válida."""

    desconocidas = texto.lower().count("[unk]")
    ps = normalizar(texto).split()
    pw = set(ps)
    def res(accion, **kw):
        return Resultado(accion, desconocidas=desconocidas, **kw)
 
    # 1) Cancelar tiene prioridad sobre todo
    if pw & CANCELACIONES:
        return res(CANCELAR)
 
    # 2) Recorrer las palabras EN ORDEN
    afirmadas, negadas = set(), set()
    negando = excluir = False
    con_hielo = True
    cantidad = None
    for p in ps:
        if p in NEGACIONES:
            negando = True
        elif p in EXCLUSION:
            excluir = True
        elif p in HIELO:
            if excluir:
                con_hielo = False
            excluir = False
        elif p in SINONIMOS:
            (negadas if (negando or excluir) else afirmadas).add(SINONIMOS[p])
            excluir = False
        elif p in NOMBRES_DE_TRAGO:
            if negando or excluir:
                negadas.add(p)
            else:
                afirmadas |= RECETA[NOMBRES_DE_TRAGO[p]]   # el nombre aporta sus bebidas
            excluir = False
        elif p in CANTIDADES and cantidad is None:
            cantidad = CANTIDADES[p]
 
    # 3) Negaciones: ante la duda, no servir
    if negadas or (pw & NEGACIONES):
        if afirmadas:
            return res(ACLARAR)
        return res(RECHAZO)
 
    # 4) Sin bebidas nombradas
    if not afirmadas:
        if pw & REPETIR:
            return res(REPETIR_ULTIMO)
        if pw & GENERICOS:
            return res(ACLARAR)
        if pw & CORTESIA:
            return res(CORTESIA_ACC)
        return res(NO_ENTENDIDO)
 
    # 5) Algo que no figura en ningún trago de la carta
    bebidas = frozenset(afirmadas)
    if bebidas - EN_CARTA:
        return res(FUERA_DE_CARTA)
 
    # 6) Todo está en la carta: ¿forma un trago?
    if bebidas in TRAGOS:                                   # combinación exacta
        trago = TRAGOS[bebidas]
    elif len(bebidas) == 1 and next(iter(bebidas)) in ATAJO_SOLO:
        trago = ATAJO_SOLO[next(iter(bebidas))]             # una bebida sola con atajo
    else:
        return res(ACLARAR)

    return res(PEDIDO, trago_id=trago, cantidad=cantidad or 1,
               con_hielo=con_hielo)
 
 
def interpretar_id(texto):
    """Versión simple: ID de trago si es un pedido, None en cualquier otro caso."""
    r = interpretar(texto)
    return r.trago_id if r.accion == PEDIDO else None
 
 
# ============================================================
# 7) Controles de compatibilidad con P2
# ============================================================
def verificar_compatibilidad():
    """1) Palabras de P2 que P3 no clasificó. 2) Palabras de P3 que Vosk nunca diría."""
    vocab = set(VOCABULARIO)
    sin_tratar = sorted(vocab - CONOCIDAS)
    if sin_tratar:
        print(f"AVISO: palabras de VOCABULARIO sin tratamiento en P3: {sin_tratar}")
    else:
        print("OK  cobertura: todas las palabras de VOCABULARIO están clasificadas")
    for alias in sorted(set(SINONIMOS) | set(NOMBRES_DE_TRAGO)):
        if alias not in vocab:
            print(f"AVISO: '{alias}' está en P3 pero no en VOCABULARIO (Vosk nunca lo diría)")
 
 
def probar_cada_palabra():
    """Cada palabra de VOCABULARIO, dicha sola, debe dar una acción válida."""
    malas = [p for p in VOCABULARIO if interpretar(p).accion not in ACCIONES]
    print("OK  todas las palabras sueltas dan una acción válida" if not malas
          else f"MAL palabras sin acción válida: {malas}")


   

if __name__ == "__main__":
    verificar_compatibilidad()
    probar_cada_palabra()
    print()

    # (frase, acción esperada, trago esperado, [extras opcionales])
    pruebas = [
        ("quiero un fernet con coca", PEDIDO, 2),
        ("dame una coca con ferne", PEDIDO, 2),
        ("un fernet", PEDIDO, 2),
        ("un campari", PEDIDO, 4),
        ("campari con naranja", PEDIDO, 4),
        ("vodka con naranja", PEDIDO, 1),
        ("vodka sprite por favor", PEDIDO, 3),
        ("gin tonic", PEDIDO, 5),
        ("un gin", PEDIDO, 5),
        ("ron con coca", PEDIDO, 6),
        ("un ron", PEDIDO, 26),
        ("cuba libre", PEDIDO, 6),
        ("vino con pomelo", PEDIDO, 7),
        ("una cerveza", PEDIDO, 18),
        ("cerveza con limon", PEDIDO, 8),
        ("un negroni", PEDIDO, 9),
        ("un mojito", PEDIDO, 10),
        ("margarita", PEDIDO, 11),
        ("daikiri", PEDIDO, 12),
        ("caipirinha", PEDIDO, 13),
        ("caipiroska", PEDIDO, 14),
        ("tom collins", PEDIDO, 15),
        ("old fashioned", PEDIDO, 16),
        ("aperol spritz", PEDIDO, 17),
        ("spritz", PEDIDO, 17),
        ("[unk] fernet [unk]", PEDIDO, 2, {"desconocidas": 2}),
        ("fernet con coca", PEDIDO, 2, {"cantidad": 1, "con_hielo": True}),
        ("dos fernet con coca", PEDIDO, 2, {"cantidad": 2}),
        ("dos mojito", PEDIDO, 10, {"cantidad": 2}),
        ("fernet con coca sin hielo", PEDIDO, 2, {"con_hielo": False}),
        ("fernet con coca doble", PEDIDO, 2, {"cantidad": 2}),
        # --- Ambiguos ---
        ("un vodka", ACLARAR, None),
        ("un vino", PEDIDO, 19),
        ("un whisky", PEDIDO, 24),
        ("una coca", PEDIDO, 30),
        ("naranja", PEDIDO, 32),
        ("vodka con fernet", ACLARAR, None),
        ("mojito con coca", ACLARAR, None),
        ("un trago", ACLARAR, None),
        ("un fizz", ACLARAR, None),
        # --- Fuera de la carta ---
        ("baileys", PEDIDO, 22),
        ("una sidra", PEDIDO, 20),
        ("fernet con coca y baileys", ACLARAR, None),
        # --- Negaciones, cancelar, etc. ---
        ("no quiero fernet con coca", RECHAZO, None),
        ("no quiero un mojito", RECHAZO, None),
        ("nada gracias", RECHAZO, None),
        ("fernet sin coca", ACLARAR, None),
        ("basta", CANCELAR, None),
        ("otra", REPETIR_ULTIMO, None),
        ("gracias", CORTESIA_ACC, None),
        ("[unk]", NO_ENTENDIDO, None),
        ("", NO_ENTENDIDO, None),
        ("quiero un fernet para mi", PEDIDO, 2),
        ("una gancia", PEDIDO, 28),
    ]
    fallos = 0
    for frase, accion, trago, *extra in pruebas:
        extras = extra[0] if extra else {}
        r = interpretar(frase)
        ok = (r.accion == accion and r.trago_id == trago
              and all(getattr(r, k) == v for k, v in extras.items()))
        fallos += not ok
        print(f"{'OK ' if ok else 'MAL'} {frase!r} -> {r.accion} {r.trago_id}"
              + ("" if ok else f"   (esperado {accion} {trago})"))
    print(f"\n{len(pruebas) - fallos}/{len(pruebas)} pruebas OK")