import socket
import sys
import threading
import os
import paramiko
import requests
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Generamos una clave RSA falsa para el servidor del Honeypot
HOST_KEY = paramiko.RSAKey.generate(2048)

def send_telegram_alert(message):
    """Envía una alerta push al bot de Telegram de forma segura"""
    if not TOKEN or not CHAT_ID:
        return # Si no hay credenciales, no hace nada
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"[-] Error al enviar alerta a Telegram: {e}")

class HoneyDogServer(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip = client_ip
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        log_msg = f"[🐾 HoneyDog] ¡Intento de acceso! IP: {self.client_ip} | Usuario: {username} | Clave: {password}"
        print(log_msg)
        
        # Guardar en log local
        with open("honeydog_access.log", "a") as log:
            log.write(f"IP: {self.client_ip} | User: {username} | Pass: {password}\n")
            
        # 🚨 ALERTA DE TELEGRAM: Intento de intrusión
        tg_msg = (
            f"🐾 *[HoneyDog ALERT]*\n"
            f"⚠️ *Intento de acceso SSH detectado*\n"
            f"🌐 *IP Atacante:* `{self.client_ip}`\n"
            f"👤 *Usuario usado:* `{username}`\n"
            f"🔑 *Contraseña usada:* `{password}`"
        )
        send_telegram_alert(tg_msg)
            
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

def handle_connection(client_socket, client_ip):
    try:
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(HOST_KEY)
        
        server = HoneyDogServer(client_ip)
        transport.start_server(server=server)
        
        channel = transport.accept(20)
        if channel is None:
            return

        server.event.wait()
        
        # Bienvenida falsa al servidor simulado
        channel.send("\r\nWelcome to Ubuntu 24.04.1 LTS (GNU/Linux 6.8.0-generic x86_64)\r\n\r\n")
        
        buffer = ""
        channel.send("kali@ubuntu:~$ ")
        
        while True:
            char = channel.recv(1)
            if not char:
                break
                
            if char == b'\r' or char == b'\n':
                channel.send("\r\n")
                command = buffer.strip()
                
                if command:
                    print(f"[🔥 COMANDO EJECUTADO] IP {client_ip}: {command}")
                    with open("honeydog_commands.log", "a") as log:
                        log.write(f"IP: {client_ip} | Cmd: {command}\n")
                    
                    # 🚨 ALERTA DE TELEGRAM: Comando ejecutado en la trampa
                    tg_cmd_msg = (
                        f"🔥 *[HoneyDog COMPROMISE]*\n"
                        f"💻 *Comando ejecutado en la shell falsa*\n"
                        f"🌐 *IP:* `{client_ip}`\n"
                        f"🐚 *Comando:* `{command}`"
                    )
                    send_telegram_alert(tg_cmd_msg)
                
                # Respuestas simuladas básicas
                if command == "whoami":
                    channel.send("root\r\n")
                elif command == "ls":
                    channel.send("Desktop  Documents  Downloads  flag.txt  shadow_backup.bak\r\n")
                elif command == "cat flag.txt":
                    channel.send("¡Buen intento! Pero has caído en las garras de HoneyDog 🐾\r\n")
                elif command == "exit":
                    channel.send("Connection closed.\r\n")
                    break
                else:
                    channel.send(f"bash: {command}: command not found\r\n")
                    
                buffer = ""
                channel.send("kali@ubuntu:~$ ")
            else:
                channel.send(char)
                buffer += char.decode('utf-8', errors='ignore')

    except Exception as e:
        print(f"[-] Error con la conexión de {client_ip}: {e}")
    finally:
        client_socket.close()

def start_honeypot(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(100)
        print(f"🐾 [HoneyDog] El cebo está listo. Escuchando intrusos en el puerto {port}...")
    except Exception as e:
        print(f"[-] Error al levantar el socket en el puerto {port}: {e}")
        print("💡 Consejo: Puertos menores al 1024 requieren permisos de administrador (sudo).")
        sys.exit(1)

    while True:
        client_socket, client_addr = server_socket.accept()
        client_ip = client_addr[0]
        
        t = threading.Thread(target=handle_connection, args=(client_socket, client_ip))
        t.start()

if __name__ == "__main__":
    BANNER = r"""
       /\_/\  🐾  [ H O N E Y D O G   H O N E Y P O T ]
      ( o.o )     -------------------------------------
       > ^ <      Alineando defensas... ¡Trampa lista!
      /     \     
     (_|_|_|_)    -- by david-rtd | Active Defense Tool --
    """
    print(BANNER)
    
    # Manejo dinámico del puerto
    target_port = 2222 # Puerto por defecto
    
    if len(sys.argv) > 1:
        try:
            target_port = int(sys.argv[1])
            if target_port < 1 or target_port > 65535:
                raise ValueError
        except ValueError:
            print("[-] Error: El puerto debe ser un número entero válido entre 1 y 65535.")
            sys.exit(1)
            
    try:
        start_honeypot(target_port)
    except KeyboardInterrupt:
        print("\n\n🐾 [HoneyDog] Queria mas galletas :( Guau, Guau")
        sys.exit(0)
