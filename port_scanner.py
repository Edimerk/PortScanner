import os
import socket
import threading
import time
import subprocess

# Intentar importar tqdm, si no está instalado, instalarlo automáticamente
try:
    import tqdm
except ImportError:
    print("🔄 Instalando la librería 'tqdm' automáticamente...")
    subprocess.run(["pip", "install", "tqdm"], check=True)
    import tqdm  # Importamos nuevamente después de instalar

# Puertos más comunes (modo rápido)
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 8080]

open_ports = []

def scan_port(ip, port, progress_bar=None):
    """Escanea un puerto en una IP dada."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((ip, port))  # 0 = Abierto, Otro = Cerrado
    sock.close()

    if result == 0:
        print(f"[+] Puerto {port} está ABIERTO")
        open_ports.append(port)

    if progress_bar:
        progress_bar.update(1) 

def scan_ports(ip, start_port, end_port, mode):
    """Escanea un rango de puertos en una IP."""
    print(f"\nEscaneando {ip} desde el puerto {start_port} hasta {end_port}...\n")
    
    ports_to_scan = COMMON_PORTS if mode == "rapido" else range(start_port, end_port + 1)

    threads = []
    progress_bar = tqdm.tqdm(total=len(ports_to_scan), desc="Escaneando", unit="puerto")

    for port in ports_to_scan:
        thread = threading.Thread(target=scan_port, args=(ip, port, progress_bar))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    progress_bar.close()
    print("\n✅ Escaneo finalizado.")

    # Guardar resultados en un archivo
    with open("resultados.txt", "w") as file:
        file.write(f"Escaneo de {ip} desde el puerto {start_port} hasta {end_port}\n")
        if open_ports:
            file.write("\nPuertos abiertos:\n")
            file.write("\n".join(map(str, open_ports)))
        else:
            file.write("\nNo se encontraron puertos abiertos.")

    print("\n📂 Resultados guardados en 'resultados.txt'.")

if __name__ == "__main__":
    print("\n🔎 Escáner de Puertos 🔎\n")

    try:
        ip = input("📌 Ingrese la dirección IP a escanear: ")
        socket.inet_aton(ip)  # Verificamos que la IP sea válida

        while True:
            try:
                start_port = int(input("📌 Ingrese el puerto inicial: "))
                end_port = int(input("📌 Ingrese el puerto final: "))
                if start_port > 0 and end_port >= start_port:
                    break
                else:
                    print("⚠️ Los valores de los puertos no son válidos. Inténtelo de nuevo.")
            except ValueError:
                print("⚠️ Entrada no válida. Ingrese números enteros.")

        mode = input("🔄 ¿Modo rápido o completo? (escriba 'rapido' o 'completo'): ").strip().lower()
        if mode not in ["rapido", "completo"]:
            mode = "completo"

        start_time = time.time()  
        scan_ports(ip, start_port, end_port, mode)
        end_time = time.time() 

        print(f"\n⏳ Tiempo total de escaneo: {round(end_time - start_time, 2)} segundos")

    except KeyboardInterrupt:
        print("\n❌ Escaneo cancelado por el usuario.")
    except socket.error:
        print("⚠️ Dirección IP no válida. Inténtelo de nuevo.")
