from rapidfuzz import process, fuzz
from vocabulario import VOCABULARIO

def corregir_por_similitud(texto_escuchado):
    palabras = texto_escuchado.split()
    resultado = []
    
    for p in palabras:
        # Busca si la palabra se parece en +75% a alguna bebida del bar
        coincidencia = process.extractOne(p, VOCABULARIO, scorer=fuzz.ratio)
        if coincidencia[0] and coincidencia[1] >= 85 :
            resultado.append(coincidencia[0])  # Reemplaza por la bebida corre    
    return " ".join(resultado)
