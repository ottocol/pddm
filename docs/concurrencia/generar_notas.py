#!/usr/bin/env python3
"""Genera notas.json para el ejercicio de concurrencia.

Uso: python3 generar_notas.py [numero_de_notas] [archivo_salida]
     (por defecto 10000 notas en notas.json)

Copia el archivo resultante en docs/datos/notas.json del sitio MkDocs.
"""
import json
import random
import sys
from datetime import datetime, timedelta, timezone

random.seed(2026)  # siempre genera el mismo archivo

acciones = ["Llamar a", "Escribir a", "Recordar a", "Quedar con", "Enviar el informe a",
            "Preguntar a", "Revisar con", "Comprar un regalo para", "Devolver el libro a",
            "Pedir cita para"]
personas = ["Ana", "Luis", "María José", "Íñigo", "Pilar", "Àlex", "Begoña", "Raúl",
            "Nuria", "el equipo de diseño", "la profesora", "el fontanero"]
cosas = ["comprar pan", "revisar el presupuesto", "preparar la presentación del lunes",
         "reservar mesa para el sábado", "llevar el coche al taller", "pagar la factura de la luz",
         "renovar el pasaporte", "estudiar Core Data", "terminar la práctica de iOS",
         "regar las plantas", "hacer la compra", "contestar los correos pendientes",
         "ir a l'Alcúdia", "llamar al médico", "actualizar el currículum"]
detalles = ["Antes del viernes.", "Sin falta.", "Si da tiempo.", "Importante.",
            "Mirar precios antes.", "Llevar la documentación.", "Preguntar por el descuento.",
            "Ojo con el horario de verano.", "Apuntar el resultado aquí."]

def texto_aleatorio():
    r = random.random()
    if r < 0.40:
        texto = f"{random.choice(acciones)} {random.choice(personas)}"
    elif r < 0.75:
        texto = random.choice(cosas).capitalize()
    else:
        # nota de varias líneas
        lineas = [random.choice(cosas).capitalize()]
        for _ in range(random.randint(1, 3)):
            lineas.append(random.choice(detalles))
        texto = "\n".join(lineas)
    if random.random() < 0.15:
        texto += " " + random.choice(detalles)
    return texto

def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    salida = sys.argv[2] if len(sys.argv) > 2 else "notas.json"
    ahora = datetime(2026, 10, 1, tzinfo=timezone.utc)
    notas = []
    for _ in range(n):
        fecha = ahora - timedelta(seconds=random.randint(0, 2 * 365 * 24 * 3600))
        notas.append({
            "texto": texto_aleatorio(),
            "fecha": fecha.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })
    # unas pocas notas vacías, para el ejercicio de migraciones
    for i in random.sample(range(n), max(1, n // 1000)):
        notas[i]["texto"] = ""
    with open(salida, "w", encoding="utf-8") as f:
        json.dump(notas, f, ensure_ascii=False, indent=1)
    print(f"Generadas {n} notas en {salida}")

if __name__ == "__main__":
    main()
