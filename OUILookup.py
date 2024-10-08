#!/usr/bin/env python3

#Librerias 
import sys
import subprocess
import re
import requests
import getopt
import time

HELP = """Use: ./OUILookup --mac <mac> | --arp | [--help]
--mac: MAC a consultar. P.e. aa:bb:cc:00:00:00.
--arp: muestra los fabricantes de los host
disponibles en la tabla arp.
--help: muestra este mensaje y termina."""


# Función para obtener los datos de fabricación de una tarjeta de red por MAC
def obtener_fabricante (mac_address):  
    """
    Obtiene los datos de fabricación de una tarjeta de red por MAC.
    
    Parámetros:
        mac : MAC del host a consultar.
    
    Retorna:
        Datos de fabricación de la tarjeta de red o "Not found" si no se encuentra.
    """
    api_url                = f"https://api.maclookup.app/v2/macs/{mac_address}"  ##construye la URL de la API publica a usar
    tiempo_inicial         = time.time()
    respuesta              = requests.get(api_url)  #solicitud HTTP GET a la URL de la API (obtener fabricante)
    tiempo_final           = time.time()
    tiempo_de_respuesta_ms = (tiempo_final-tiempo_inicial) *1000  #convertir a milisegundos

    #manejo de respuesta desde la API
    if respuesta.status_code==200:
        datos=respuesta.json()
        return datos['company'],tiempo_de_respuesta_ms
    else:
        return "Fabricante no encontrado",tiempo_de_respuesta_ms
    
# Función para obtener la tabla ARP
def obtener_tabla_arp():
    """
    Obtiene la tabla ARP.
    
    Retorna:
        Texto con la tabla ARP.
    """
    tabla_arp={}
    try:
        salida = subprocess.check_output("arp -a", shell = True, stderr = subprocess.STDOUT).decode('cp850',errors = 'replace') #ejecutar el comando 'arp -a' para obtener la tabla arp
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar el comando: {e.salida.decode('cp850', errors='replace')}")
        return tabla_arp
    
    # Procesar la salida para extraer direcciones IP y MAC
    for line in salida.split("\n"):
        match =re.match(r'^\s*(\d+\.\d+\.\d+\.\d+)\s+([a-fA-F0-9-:]+)\s+', line)
        if match:
            ip             = match.group(1)
            mac            = match.group(2).replace('-', ':')  # Reemplazar '-' por ':' en la MAC
            tabla_arp[mac] = ip
    return tabla_arp


def main(argv):
    direccion_mac =''
    mostrar_arp =False

    #analizar argumentos de la linea de comandos y posterior manejo
    try:
        opts, args = getopt.getopt(argv, "ham:", ["help", "arp", "mac="]) 
    except getopt.GetoptError:
        print("Uso: OUILookup.py --mac <mac> | --arp | [--help]")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):     
            print(HELP)
            sys.exit()
        elif opt in ('-m', '--mac'):
            direccion_mac = arg
        elif opt in ('-a', '--arp'):
            mostrar_arp = True


    if mostrar_arp:
        tabla_arp = obtener_tabla_arp()       
        for mac, ip in tabla_arp.items():
            vendor = obtener_fabricante(mac)
            print(f"IP: {ip} / MAC: {mac} / Fabricante: {vendor}")

    elif direccion_mac:
        vendor, tiempo_de_respuesta_ms = obtener_fabricante(direccion_mac)
        print(f"MAC address: {direccion_mac}")    
        print(f"Fabricante: {vendor}")
        print(f"Tiempo de respuesta: {tiempo_de_respuesta_ms:.2f} ms")
    else:
        print(HELP)

if __name__ == "__main__":
    main(sys.argv[1:])

#Lucas Rojas 21.270.496-2 lucas.rojas@alumnos.uv.cl
#Christopher O'Kinggton 21.565.973-9 christopher.okinggton@alumnos.uv.cl