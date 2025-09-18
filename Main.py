import random
import json
from datetime import date
import pyttsx3
import requests

# archivo donde se guarda el progreso y el nombre
PROGRESO_FILE = "progreso.json"

# lista de retos diarios y cuánto CO2 reducen
retos = [
    {"reto": "Usa la bicicleta en lugar del auto", "co2": 2.1},
    {"reto": "Apaga las luces que no uses", "co2": 0.5},
    {"reto": "Lleva tu propia bolsa reutilizable al super", "co2": 0.3},
    {"reto": "Reduce tu consumo de carne roja hoy", "co2": 1.5},
    {"reto": "Recicla plástico y cartón", "co2": 0.8},
    {"reto": "Toma duchas más cortas (5 min)", "co2": 1.0},
    {"reto": "Planta un árbol o cuida una planta", "co2": 2.5},
    {"reto": "Usa transporte público en lugar del auto", "co2": 1.8},
    {"reto": "Desenchufa cargadores y aparatos que no uses", "co2": 0.4},
    {"reto": "Lleva tu propio termo o botella reutilizable", "co2": 0.2},
    {"reto": "Compra productos locales en lugar de importados", "co2": 1.2},
    {"reto": "Reutiliza frascos y envases de vidrio", "co2": 0.6},
    {"reto": "No uses bolsas plásticas en la verdulería", "co2": 0.3},
    {"reto": "Haz compost con restos de comida", "co2": 1.0},
    {"reto": "Prefiere mandarinas y frutas de estación", "co2": 0.7},
    {"reto": "Comparte auto con alguien (carpool)", "co2": 1.6}
]

# iniciar motor de voz
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[3].id)
engine.setProperty("rate", 150)

# función para hablar y mostrar texto
def hablar(texto):
    print(texto)
    engine.say(texto)
    engine.runAndWait()

# función para obtener el clima de una ciudad
def obtener_clima(city):
    url = f"https://wttr.in/{city}?format=%C+%t"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return "No se pudo obtener la información del clima"
    except Exception:
        return "Error al conectar con el servicio del clima"

# cargar progreso desde archivo
def cargar_progreso():
    try:
        with open(PROGRESO_FILE, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"nombre": None, "puntos": 0, "co2_total": 0, "historial": [], "ciudad": None}

    # asegurar todas las claves
    for key in ["nombre", "puntos", "co2_total", "historial", "ciudad"]:
        if key not in data:
            if key == "historial":
                data[key] = []
            else:
                data[key] = None if key == "nombre" or key == "ciudad" else 0

    return data

# guardar progreso en archivo
def guardar_progreso(data):
    with open(PROGRESO_FILE, "w") as f:
        json.dump(data, f, indent=4)

# mostrar clima de la ciudad principal y permitir consultar otra ciudad
def mostrar_clima(progreso):
    if progreso["ciudad"]:
        clima = obtener_clima(progreso["ciudad"])
        hablar(f"El clima en tu ciudad ({progreso['ciudad']}) es: {clima}")
    else:
        ciudad = input("🌦️ Ingresa tu ciudad para ver el clima: ")
        progreso["ciudad"] = ciudad
        guardar_progreso(progreso)
        clima = obtener_clima(ciudad)
        hablar(f"El clima en {ciudad} es: {clima}")

    otra = input("¿Quieres consultar el clima de otra ciudad? (si/no): ").strip().lower()
    if otra == "si":
        ciudad_extra = input("Ingresa la otra ciudad: ")
        clima_extra = obtener_clima(ciudad_extra)
        hablar(f"El clima en {ciudad_extra} es: {clima_extra}")

# mostrar puntos y CO2 acumulado
def mostrar_puntos(progreso):
    hablar(f"Actualmente tienes {progreso['puntos']} puntos acumulados y has reducido {progreso['co2_total']} kilogramos de CO2.")

# minijuego ecológico
def minijuego(progreso):
    hablar("🎮 Minijuego ecológico: Atrapa la basura antes de que llegue al río!")
    print("Instrucciones: Escribe 'izquierda', 'centro' o 'derecha' para atrapar la basura.")
    posiciones = ["izquierda", "centro", "derecha"]
    basura = random.choice(posiciones)
    intento = input("¿Dónde está la basura?: ").strip().lower()
    if intento == basura:
        puntos_extra = 5
        co2_extra = 0.5
        progreso["puntos"] += puntos_extra
        progreso["co2_total"] += co2_extra
        hablar(f"¡Genial! Atrapaste la basura. Ganaste {puntos_extra} puntos y redujiste {co2_extra} kg de CO2.")
    else:
        hablar(f"Oh no! La basura se fue al río. No ganaste puntos esta vez. 😢")
    guardar_progreso(progreso)

# ejecutar el reto diario
def hacer_reto(progreso):
    nombre = progreso["nombre"]
    hoy = str(date.today())

    if any(entry["fecha"] == hoy for entry in progreso["historial"]):
        hablar(f"{nombre}, ya completaste el reto de hoy.")
        return

    reto = random.choice(retos)
    hablar(f"Reto de hoy para {nombre}: {reto['reto']}. Si lo cumples reduces {reto['co2']} kilogramos de CO2.")

    respuesta = input("¿Lo cumpliste hoy? (si/no): ").strip().lower()

    if respuesta == "si":
        puntos_ganados = int(reto["co2"] * 10)
        progreso["puntos"] += puntos_ganados
        progreso["co2_total"] += reto["co2"]
        hablar(f"Genial {nombre}! Sumaste {puntos_ganados} puntos. Tu CO2 total reducido es {progreso['co2_total']} kilogramos.")
    else:
        hablar(f"No pasa nada {nombre}, mañana tendrás otra oportunidad.")

    progreso["historial"].append({
        "fecha": hoy,
        "reto": reto["reto"],
        "co2": reto["co2"],
        "cumplido": (respuesta == "si")
    })

    guardar_progreso(progreso)
    hablar(f"Total acumulado: {progreso['puntos']} puntos.")

    # ejecutar minijuego después del reto
    minijuego(progreso)

# menú interactivo
def menu():
    progreso = cargar_progreso()

    if not progreso["nombre"]:
        nombre = input("🌱 Bienvenido a MiHuellaEco, ¿cómo te llamas?: ")
        progreso["nombre"] = nombre
        guardar_progreso(progreso)

    mostrar_clima(progreso)

    while True:
        print("\nEscribe un comando: 'reto' para el reto diario, 'puntos' para ver tus puntos, 'clima' para ver el clima, 'salir' para salir.")
        comando = input("Comando: ").strip().lower()

        if comando == "reto":
            hacer_reto(progreso)
        elif comando == "puntos":
            mostrar_puntos(progreso)
        elif comando == "clima":
            mostrar_clima(progreso)
        elif comando == "salir":
            hablar("¡Hasta luego! Sigue cuidando tu huella ecológica 🌱")
            break
        else:
            hablar("Comando no reconocido, intenta de nuevo.")

# Ejecutar
if __name__ == "__main__":
    menu()
