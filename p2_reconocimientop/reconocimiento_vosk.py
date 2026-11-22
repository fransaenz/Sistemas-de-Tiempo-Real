import os
import sys
import queue
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Importamos la función de corrección desde tu archivo utilities.py
from utilities import corregir_por_similitud

q = queue.Queue()

def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

model_path = "vosk-model-small-es-0.42"
if not os.path.exists(model_path):
    print(f"Error: La carpeta '{model_path}' no existe.")
    sys.exit(1)

model = Model(model_path)

# Reconocedor abierto (sin 3er parámetro) para no bloquear la salida de palabras fuera de diccionario
rec = KaldiRecognizer(model, 16000)

# Selección de micrófono
input_device = None
devices = sd.query_devices()
for idx, dev in enumerate(devices):
    if dev['max_input_channels'] > 0:
        if "usb" in dev['name'].lower() or input_device is None:
            input_device = idx

print(f"Usando micrófono ID {input_device}: {devices[input_device]['name']}")
print("Escuchando... Hablá al micrófono (Ctrl+C para salir).")

# Variables para control de duplicados
ultimo_parcial = ""
ultimo_final = ""

try:
    with sd.RawInputStream(samplerate=16000, 
                            blocksize=4000, 
                            device=input_device,
                            dtype='int16',
                            channels=1, 
                            callback=callback):
        while True:
            data = q.get()
            
            if rec.AcceptWaveform(data):
                # Resultado Final de Vosk
                res = json.loads(rec.Result())
                texto_raw = res.get("text", "").strip()
                # Corrección por fuzzy matching/mapeo desde utilities
                texto_final = corregir_por_similitud(texto_raw)
                
                # Filtro: No vacío y No repetido
                if texto_final and texto_final != ultimo_final:
                    print("-> Texto reconocido:", texto_final)
                    ultimo_final = texto_final
                    ultimo_parcial = ""  # Reiniciar el parcial al cerrar frase
            else:
                # Resultado Parcial
                res_p = json.loads(rec.PartialResult())
                texto_p_raw = res_p.get("partial", "").strip()
                
                # Corrección parcial desde utilities
                texto_parcial = corregir_por_similitud(texto_p_raw)
                
                # Filtro: No vacío y No repetido consecutivamente
                if texto_parcial and texto_parcial != ultimo_parcial:
                    print("--> Parcial:", texto_parcial)
                    ultimo_parcial = texto_parcial

except KeyboardInterrupt:
    print("\nPrograma detenido.")
except Exception as e:
    print(f"\nError de audio: {e}")