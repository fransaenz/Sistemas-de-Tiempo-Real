(VODKA, FERNET, CAMPARI, COCA, SPRITE, NARANJA, CERVEZA, VINO, 
 GANCIA, LIMON, GIN, TONICA, RON, WHISKY, TEQUILA, VERMUT, 
 APEROL, CHAMPAGNE, SIDRA, BAILEYS, LICOR, POMELO,
 AZUCAR, MENTA, SODA, TRIPLE_SEC, ANGOSTURA, CACHACA) = range(1, 29)

SINONIMOS = {
    "vodka": VODKA, "vodca": VODKA, "vodquita": VODKA, "vodkita": VODKA,
    "smirnoff": VODKA, "absolut": VODKA, "skyy": VODKA,

    "fernet": FERNET, "fernecito": FERNET, "ferno": FERNET, "branca": FERNET,
    "fernando": FERNET, "ferne": FERNET, "fernandito": FERNET,
  
    "campari": CAMPARI,  "gancia": GANCIA,
    "tonic": TONICA, "tonica": TONICA, "baileys": BAILEYS,

    "coca": COCA, "cola": COCA, "coquita": COCA, "cocucha": COCA, 
    "cocacola": COCA, "caco": COCA, "cocarda": COCA,
    
    "sprite": SPRITE, "spray": SPRITE, "sprayt": SPRITE, "esprai": SPRITE,

    "naranja": NARANJA,  "naranjada": NARANJA, "jugo": NARANJA, "juguito": NARANJA,

    "cerveza": CERVEZA, "birra": CERVEZA, "rabi": CERVEZA, "pinta": CERVEZA, "ipa": CERVEZA,
    "lata": CERVEZA, "porron": CERVEZA, "porroncito": CERVEZA, "quilmes": CERVEZA, 
    "brahma": CERVEZA, "stella": CERVEZA, "artois": CERVEZA, "heineken": CERVEZA, 
    "corona": CERVEZA, "andes": CERVEZA, "cervecita": CERVEZA, "birrin": CERVEZA,

    "vino": VINO, "tinto": VINO, "blanco": VINO, "veneco": VINO, 
    "malbec": VINO, "cabernet": VINO, "merlot": VINO, "totin": VINO, 

    "gin": GIN, "beefeater": GIN, "tanqueray": GIN, "ginebra": GIN, "ginebrita": GIN, 
    
    "ron": RON, "havana": RON, "bacardi": RON, "club": RON, 
    "roncito": RON, "ronsito": RON, "ronaldo": RON, "ronaldinho": RON,
    
    "whisky": WHISKY, "tequila": TEQUILA, "quilate": TEQUILA, "quila": TEQUILA,
    
    "jager": LICOR,"jagger": LICOR, "jagermeister": LICOR, "licor": LICOR,
    "yaguer": LICOR, "yager": LICOR, "yagermeister": LICOR, "yaguermaster": LICOR,
    
    "vermut": VERMUT, "vermu": VERMUT, "aperol": APEROL,
    
    "champan": CHAMPAGNE, "champagne": CHAMPAGNE, "sidra": SIDRA,
    "yampan": CHAMPAGNE, "yampagne": CHAMPAGNE,
    
    "limon": LIMON, "lima": LIMON, "limonada": LIMON, "limoncito": LIMON, 
    "pomelo" : POMELO, "soda": SODA, "sodita": SODA
    
}


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
    "y", "o", "favor", "unos", "unas", "anana"
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

