"""Genera el cajón A de Medellín, 2021.

Lee las muestras reales y escribe en salida/, en este orden:
  1. tiempo
  2. cliente
  3. activo
  4. consumo
  5. factura
  6. falla
  7. mantenimiento

La muestra es de 1.000 clientes, con la mezcla de suscriptores del SUI.
No son los 996.993 de Medellín. El consumo de cada hora se suma en la factura.
La lluvia no se copia dentro de la falla.

Uso, desde esta carpeta:
  pip install pyshp
  python generar-cajon-a.py
"""

import csv
import json
import random
import unicodedata
from datetime import datetime, timedelta
from pathlib import Path

try:
    import shapefile
except ImportError:
    raise SystemExit("Falta pyshp. Instala con: pip install pyshp")


N_CLIENTES = 1000
N_ACTIVOS = 200
ANIO = 2021
COD_MEDELLIN = "05001"
SEMILLA = 2021

CARPETA = Path(__file__).resolve().parent
MUESTRAS = CARPETA.parent / "muestras"
SALIDA = CARPETA / "salida"
SUI = MUESTRAS / "sui-epm-antioquia-2021-suscriptores.csv"
CLIMA = MUESTRAS / "open-meteo-medellin-2021.json"
POLIGONO = MUESTRAS / "mgn2025-mpio" / "mgn2025-mpio.shp"
TARIFAS = MUESTRAS / "epm-tarifas-2016-2021-20261007.csv"

MESES = {
    "Enero": 1,
    "Febrero": 2,
    "Marzo": 3,
    "Abril": 4,
    "Mayo": 5,
    "Junio": 6,
    "Julio": 7,
    "Agosto": 8,
    "Septiembre": 9,
    "Octubre": 10,
    "Noviembre": 11,
    "Diciembre": 12,
}
NOMBRE_MES = {numero: nombre for nombre, numero in MESES.items()}

# kWh medio de una hora, antes de la forma del día.
BASE_KWH = {
    ("Residencial", 1): 0.18,
    ("Residencial", 2): 0.25,
    ("Residencial", 3): 0.35,
    ("Residencial", 4): 0.50,
    ("Residencial", 5): 0.70,
    ("Residencial", 6): 0.95,
    ("Industrial", ""): 3.50,
    ("Comercial", ""): 1.20,
    ("Oficial", ""): 0.90,
    ("Otros", ""): 0.60,
}

PERFIL_RESIDENCIAL = [
    0.45, 0.40, 0.38, 0.36, 0.38, 0.55,
    0.90, 1.20, 1.15, 0.95, 0.85, 0.80,
    0.85, 0.82, 0.80, 0.90, 1.10, 1.40,
    1.75, 1.85, 1.55, 1.15, 0.80, 0.55,
]
PERFIL_COMERCIAL = [
    0.25, 0.22, 0.20, 0.20, 0.22, 0.40,
    0.75, 1.15, 1.45, 1.55, 1.60, 1.55,
    1.50, 1.45, 1.50, 1.55, 1.45, 1.20,
    0.85, 0.55, 0.40, 0.35, 0.30, 0.28,
]
PERFIL_INDUSTRIAL = [
    0.75, 0.72, 0.70, 0.70, 0.75, 0.90,
    1.10, 1.20, 1.25, 1.25, 1.25, 1.20,
    1.20, 1.25, 1.25, 1.20, 1.15, 1.05,
    0.95, 0.90, 0.85, 0.82, 0.80, 0.78,
]

AFECTADOS = {
    "poste": (5, 40),
    "proteccion": (10, 80),
    "linea": (20, 250),
    "transformador": (40, 600),
    "subestacion": (200, 2500),
}
COSTO = {
    "poste": (120_000, 350_000),
    "proteccion": (180_000, 600_000),
    "linea": (250_000, 900_000),
    "transformador": (700_000, 2_200_000),
    "subestacion": (1_500_000, 6_000_000),
}


def abrir_csv(nombre):
    SALIDA.mkdir(exist_ok=True)
    ruta = SALIDA / nombre
    archivo = ruta.open("w", newline="", encoding="utf-8-sig")
    return ruta, archivo, csv.writer(archivo)


def leer_csv(ruta):
    ultimo_error = None
    for codec in ("utf-8-sig", "cp1252"):
        try:
            with ruta.open(encoding=codec, newline="") as archivo:
                return list(csv.reader(archivo))
        except UnicodeDecodeError as error:
            ultimo_error = error
    raise SystemExit(f"No pude leer {ruta.name}: {ultimo_error}")


def sin_tilde(texto):
    base = unicodedata.normalize("NFD", texto.strip())
    return "".join(c for c in base if unicodedata.category(c) != "Mn").upper()


def normalizar(perfil):
    promedio = sum(perfil) / len(perfil)
    return [valor / promedio for valor in perfil]


def peso_entero(texto):
    limpio = texto.replace("$", "").replace(" ", "").strip()
    if limpio in ("", "ND"):
        return 0
    return int(limpio)


def precio_cop(texto):
    limpio = texto.replace("$", "").replace(".", "").replace(",", ".").strip()
    return float(limpio)


def repartir(pesos, total):
    suma = sum(pesos)
    crudos = [peso * total / suma for peso in pesos]
    enteros = [int(valor) for valor in crudos]
    faltan = total - sum(enteros)
    orden = sorted(range(len(pesos)), key=lambda i: crudos[i] - enteros[i], reverse=True)
    for indice in orden[:faltan]:
        enteros[indice] += 1
    return enteros


def dentro_de_anillo(x, y, anillo):
    dentro = False
    j = len(anillo) - 1
    for i, (xi, yi) in enumerate(anillo):
        xj, yj = anillo[j]
        if (yi > y) != (yj > y):
            cruce = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < cruce:
                dentro = not dentro
        j = i
    return dentro


def construir_horas():
    hora = datetime(ANIO, 1, 1)
    fin = datetime(ANIO + 1, 1, 1)
    horas = []
    while hora < fin:
        horas.append(hora)
        hora += timedelta(hours=1)
    return horas


def escribir_calendario(horas):
    ruta, archivo, salida = abrir_csv("01-tiempo.csv")
    salida.writerow(["fecha_hora", "fecha", "hora", "mes", "anio", "periodo"])
    for momento in horas:
        salida.writerow([
            momento.strftime("%Y-%m-%d %H:%M"),
            momento.strftime("%Y-%m-%d"),
            momento.hour,
            momento.month,
            momento.year,
            momento.strftime("%Y-%m"),
        ])
    archivo.close()
    print(f"  {len(horas)} horas -> {ruta.name}")
    return ruta


def leer_sui():
    filas = leer_csv(SUI)
    columnas = filas[0]
    indice = {nombre: i for i, nombre in enumerate(columnas)}
    medellin = None
    for fila in filas[1:]:
        if len(fila) <= indice["Municipio"]:
            continue
        if sin_tilde(fila[indice["Municipio"]]) == "MEDELLIN":
            medellin = fila
            break
    if medellin is None:
        raise SystemExit(f"No está Medellín en {SUI.name}")

    def columna(nombre):
        return peso_entero(medellin[indice[nombre]])

    grupos = [
        ("Residencial", 1, columna("Estrato 1")),
        ("Residencial", 2, columna("Estrato 2")),
        ("Residencial", 3, columna("Estrato 3")),
        ("Residencial", 4, columna("Estrato 4")),
        ("Residencial", 5, columna("Estrato 5")),
        ("Residencial", 6, columna("Estrato 6")),
        ("Industrial", "", columna("Industrial")),
        ("Comercial", "", columna("Comercial")),
        ("Oficial", "", columna("Oficial")),
        ("Otros", "", columna("Otros")),
    ]
    cantidades = repartir([grupo[2] for grupo in grupos], N_CLIENTES)
    return [(tipo, estrato, real, muestra) for (tipo, estrato, real), muestra in zip(grupos, cantidades)]


def escribir_clientes(grupos):
    ruta, archivo, salida = abrir_csv("02-cliente.csv")
    salida.writerow(["cliente_id", "cod_divipola", "tipo_cliente", "estrato", "estado"])
    clientes = []
    numero = 1
    for tipo, estrato, reales, muestra in grupos:
        print(f"  {tipo} {estrato or '-'}: {muestra} de {reales} reales")
        for _ in range(muestra):
            cliente_id = f"C{numero:04d}"
            salida.writerow([cliente_id, COD_MEDELLIN, tipo, estrato, "activo"])
            clientes.append({"cliente_id": cliente_id, "tipo": tipo, "estrato": estrato})
            numero += 1
    archivo.close()
    print(f"  {len(clientes)} clientes -> {ruta.name}")
    return clientes


def leer_tarifas():
    tarifas = {}
    for fila in leer_csv(TARIFAS):
        if len(fila) < 12:
            continue
        if fila[0] != "Monomia" or fila[4] != "I" or fila[10] != str(ANIO):
            continue
        mes = MESES.get(fila[11])
        if mes is None:
            continue
        precio = precio_cop(fila[5])
        tipo_tarifa, tipo_dato, rango = fila[1], fila[2], fila[3]
        clave = None
        if tipo_tarifa == "Residencial":
            if tipo_dato in ("Estrato 1", "Estrato 2", "Estrato 3") and rango == "Rango > CS":
                clave = tipo_dato
            elif tipo_dato in ("Estrato 4", "Estrato 5 y 6") and rango == "Todo el consumo":
                clave = tipo_dato
        elif tipo_tarifa == "No Residencial" and rango == "N/A":
            if tipo_dato == "Industrial y Comercial":
                clave = "Industrial y Comercial"
            elif tipo_dato.startswith("Oficial"):
                clave = "Oficial"
        if clave:
            tarifas[(mes, clave)] = precio

    faltan = []
    for mes in range(1, 13):
        for clave in ("Estrato 1", "Estrato 2", "Estrato 3", "Estrato 4", "Estrato 5 y 6", "Industrial y Comercial", "Oficial"):
            if (mes, clave) not in tarifas:
                faltan.append(f"{NOMBRE_MES[mes]} {clave}")
    if faltan:
        raise SystemExit("Faltan tarifas de 2021: " + ", ".join(faltan))
    return tarifas


def clave_tarifa(cliente):
    if cliente["tipo"] == "Residencial":
        if cliente["estrato"] <= 4:
            return f"Estrato {cliente['estrato']}"
        return "Estrato 5 y 6"
    if cliente["tipo"] == "Oficial":
        return "Oficial"
    return "Industrial y Comercial"


def leer_clima(horas):
    datos = json.loads(CLIMA.read_text(encoding="utf-8"))
    bloque = datos["hourly"]
    indice = {marca: i for i, marca in enumerate(bloque["time"])}
    temps = []
    lluvias = []
    for momento in horas:
        marca = momento.strftime("%Y-%m-%dT%H:%M")
        i = indice.get(marca)
        if i is None:
            raise SystemExit(f"El clima no trae la hora {marca}")
        temps.append(float(bloque["temperature_2m"][i]))
        lluvias.append(float(bloque["precipitation"][i]))
    print(f"  clima {horas[0]} a {horas[-1]}, {len(horas)} horas")
    return temps, lluvias


def leer_poligono():
    lector = shapefile.Reader(str(POLIGONO), encoding="utf-8")
    encontrado = None
    for i, registro in enumerate(lector.iterRecords()):
        if str(registro["mpio_cdpmp"]).strip() == COD_MEDELLIN:
            encontrado = i
            break
    if encontrado is None:
        raise SystemExit(f"El polígono no trae {COD_MEDELLIN}")
    forma = lector.shape(encontrado)
    puntos = forma.points
    cortes = list(forma.parts) + [len(puntos)]
    anillos = []
    for i in range(len(cortes) - 1):
        anillo = [(p[0], p[1]) for p in puntos[cortes[i]:cortes[i + 1]]]
        if len(anillo) >= 3:
            anillos.append(anillo)
    print(f"  polígono {COD_MEDELLIN}, {sum(len(a) for a in anillos)} vértices")
    return anillos


def punto_dentro(x, y, anillos):
    dentro = False
    for anillo in anillos:
        if dentro_de_anillo(x, y, anillo):
            dentro = not dentro
    return dentro


def escribir_activos(anillos, rng):
    xs = [p[0] for anillo in anillos for p in anillo]
    ys = [p[1] for anillo in anillos for p in anillo]
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    tipos = (
        ["poste"] * 90
        + ["transformador"] * 50
        + ["linea"] * 35
        + ["proteccion"] * 20
        + ["subestacion"] * 5
    )
    rng.shuffle(tipos)
    inicio = datetime(1995, 1, 1)
    fin = datetime(2020, 12, 31)
    dias = (fin - inicio).days

    ruta, archivo, salida = abrir_csv("03-activo.csv")
    salida.writerow([
        "infraestructura_id", "cod_divipola", "tipo",
        "latitud", "longitud", "fecha_instalacion", "estado",
    ])
    activos = []
    intentos = 0
    while len(activos) < N_ACTIVOS:
        intentos += 1
        if intentos > N_ACTIVOS * 20000:
            raise SystemExit("No cupieron los activos dentro del polígono")
        longitud = rng.uniform(minx, maxx)
        latitud = rng.uniform(miny, maxy)
        if not punto_dentro(longitud, latitud, anillos):
            continue
        instalado = inicio + timedelta(days=rng.randrange(dias))
        activo = {
            "infraestructura_id": f"A{len(activos) + 1:04d}",
            "tipo": tipos[len(activos)],
            "latitud": latitud,
            "longitud": longitud,
            "fecha_instalacion": instalado.date(),
        }
        salida.writerow([
            activo["infraestructura_id"],
            COD_MEDELLIN,
            activo["tipo"],
            f"{latitud:.6f}",
            f"{longitud:.6f}",
            instalado.strftime("%Y-%m-%d"),
            "en servicio",
        ])
        activos.append(activo)
    archivo.close()
    print(f"  {len(activos)} activos dentro del polígono -> {ruta.name}")
    return activos


def factor_calor(temperatura, residencial):
    if not residencial or temperatura < 24:
        return 1.0
    return 1 + min(0.25, 0.015 * (temperatura - 24))


def escribir_consumo(clientes, horas, temps, rng):
    perfiles = {
        "Residencial": normalizar(PERFIL_RESIDENCIAL),
        "Industrial": normalizar(PERFIL_INDUSTRIAL),
        "Comercial": normalizar(PERFIL_COMERCIAL),
        "Oficial": normalizar(PERFIL_COMERCIAL),
        "Otros": normalizar(PERFIL_COMERCIAL),
    }
    hora_del_dia = [momento.hour for momento in horas]
    mes_de_hora = [momento.month - 1 for momento in horas]
    marca = [momento.strftime("%Y-%m-%d %H:%M") for momento in horas]

    ruta, archivo, salida = abrir_csv("04-consumo.csv")
    salida.writerow(["cliente_id", "fecha_hora", "consumo_kwh"])
    sumas = []
    for n, cliente in enumerate(clientes, start=1):
        perfil = perfiles[cliente["tipo"]]
        base = BASE_KWH[(cliente["tipo"], cliente["estrato"])]
        factor_cliente = 0.80 + rng.random() * 0.40
        residencial = cliente["tipo"] == "Residencial"
        acumulado = [0] * 12
        for i, momento in enumerate(marca):
            bruto = base * perfil[hora_del_dia[i]] * factor_cliente
            bruto *= factor_calor(temps[i], residencial)
            bruto *= 0.85 + rng.random() * 0.30
            milesimas = int(round(bruto * 10000))
            acumulado[mes_de_hora[i]] += milesimas
            salida.writerow([cliente["cliente_id"], momento, f"{milesimas / 10000:.4f}"])
        sumas.append(acumulado)
        if n % 100 == 0:
            print(f"  {n} clientes")
    archivo.close()
    print(f"  {len(clientes) * len(horas)} filas -> {ruta.name}")
    return sumas


def escribir_facturas(clientes, sumas, tarifas, rng):
    ruta, archivo, salida = abrir_csv("05-factura.csv")
    salida.writerow([
        "cliente_id", "periodo", "consumo_kwh_mes",
        "valor_facturado", "tarifa", "estado_pago",
    ])
    estados = ["pagada", "pendiente", "en mora"]
    for cliente, acumulado in zip(clientes, sumas):
        clave = clave_tarifa(cliente)
        for mes in range(1, 13):
            kwh = acumulado[mes - 1] / 10000
            tarifa = tarifas[(mes, clave)]
            valor = round(kwh * tarifa, 2)
            estado = rng.choices(estados, weights=[82, 11, 7])[0]
            salida.writerow([
                cliente["cliente_id"],
                f"{ANIO}-{mes:02d}",
                f"{kwh:.4f}",
                f"{valor:.2f}",
                f"{tarifa:.2f}",
                estado,
            ])
    archivo.close()
    print(f"  {len(clientes) * 12} facturas -> {ruta.name}")


def factor_clima(lluvia, temperatura):
    factor = 1.0
    if lluvia >= 5:
        factor *= 3.5
    elif lluvia >= 1:
        factor *= 2.2
    elif lluvia > 0:
        factor *= 1.3
    if temperatura >= 28:
        factor *= 1.8
    elif temperatura >= 25:
        factor *= 1.3
    return factor


def escribir_fallas(activos, horas, temps, lluvias, rng):
    ruta, archivo, salida = abrir_csv("06-falla.csv")
    salida.writerow([
        "incidente_id", "infraestructura_id", "fecha_hora",
        "clientes_afectados", "duracion_minutos",
    ])
    fallas = []
    numero = 1
    for activo in activos:
        edad = ANIO - activo["fecha_instalacion"].year
        factor_edad = 1 + max(0, edad - 10) * 0.08
        bajo, alto = AFECTADOS[activo["tipo"]]
        for i, momento in enumerate(horas):
            probabilidad = min(0.05, 0.00018 * factor_edad * factor_clima(lluvias[i], temps[i]))
            if rng.random() >= probabilidad:
                continue
            minutos = rng.randint(20, 180)
            if lluvias[i] >= 5:
                minutos += rng.randint(30, 120)
            falla = {
                "incidente_id": f"F{numero:05d}",
                "infraestructura_id": activo["infraestructura_id"],
                "cuando": momento,
                "indice": i,
                "afectados": rng.randint(bajo, alto),
                "minutos": minutos,
            }
            salida.writerow([
                falla["incidente_id"],
                falla["infraestructura_id"],
                momento.strftime("%Y-%m-%d %H:%M"),
                falla["afectados"],
                falla["minutos"],
            ])
            fallas.append(falla)
            numero += 1
    archivo.close()
    print(f"  {len(fallas)} fallas -> {ruta.name}")
    return fallas


def costo_aleatorio(tipo, rng, correctivo):
    bajo, alto = COSTO[tipo]
    valor = rng.randint(bajo, alto)
    if correctivo:
        valor = int(valor * (1.4 + rng.random() * 0.8))
    return valor


def escribir_mantenimientos(activos, fallas, rng):
    ruta, archivo, salida = abrir_csv("07-mantenimiento.csv")
    salida.writerow(["mantenimiento_id", "infraestructura_id", "fecha", "tipo", "costo"])
    tipo_de = {activo["infraestructura_id"]: activo["tipo"] for activo in activos}
    filas = []
    inicio = datetime(ANIO, 1, 1)
    for activo in activos:
        dia = inicio + timedelta(days=rng.randrange(365))
        filas.append((
            activo["infraestructura_id"],
            dia.strftime("%Y-%m-%d"),
            "preventivo",
            costo_aleatorio(activo["tipo"], rng, False),
        ))
    limite = datetime(ANIO, 12, 31)
    for falla in fallas:
        if rng.random() >= 0.45:
            continue
        dia = falla["cuando"] + timedelta(days=rng.randint(1, 5))
        if dia > limite:
            dia = limite
        filas.append((
            falla["infraestructura_id"],
            dia.strftime("%Y-%m-%d"),
            "correctivo",
            costo_aleatorio(tipo_de[falla["infraestructura_id"]], rng, True),
        ))
    for i, (activo_id, fecha, tipo, costo) in enumerate(filas, start=1):
        salida.writerow([f"M{i:05d}", activo_id, fecha, tipo, costo])
    archivo.close()
    print(f"  {len(filas)} mantenimientos -> {ruta.name}")


def main():
    rng = random.Random(SEMILLA)
    print("Paso 1. Calendario")
    horas = construir_horas()
    escribir_calendario(horas)

    print("Paso 2. Clientes, con la mezcla del SUI")
    grupos = leer_sui()
    clientes = escribir_clientes(grupos)

    print("Clima y tarifa, para consumo, factura y fallas")
    temps, lluvias = leer_clima(horas)
    tarifas = leer_tarifas()

    print("Paso 3. Activos dentro del polígono")
    anillos = leer_poligono()
    activos = escribir_activos(anillos, rng)

    print("Paso 4. Consumo de cada cliente, cada hora")
    sumas = escribir_consumo(clientes, horas, temps, rng)

    print("Paso 5. Factura = suma del mes, por la tarifa EPM")
    escribir_facturas(clientes, sumas, tarifas, rng)

    print("Paso 6. Fallas sobre activos")
    fallas = escribir_fallas(activos, horas, temps, lluvias, rng)

    print("Paso 7. Mantenimientos sobre activos")
    escribir_mantenimientos(activos, fallas, rng)

    kwh_enero = sumas[0][0] / 10000
    print("Comprobación, cliente C0001, 2021-01")
    print(f"  suma de las horas = {kwh_enero:.4f} kWh")
    print("  ese mismo número queda en consumo_kwh_mes de su factura")
    if fallas:
        falla = fallas[0]
        print(
            f"  falla {falla['incidente_id']} a las {falla['cuando']}: "
            f"{falla['afectados']} clientes, {falla['minutos']} minutos"
        )
        print(f"  lluvia de esa hora: {lluvias[falla['indice']]} mm. No va en la fila de la falla.")
    print("Listo.")


if __name__ == "__main__":
    main()
