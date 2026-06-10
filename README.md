# 🐾 HoneyDog — SSH Honeypot & Active Defense Tool

<img width="716" height="186" alt="Captura de pantalla 2026-06-10 215421" src="https://github.com/user-attachments/assets/39fd1f4e-87d4-449d-af4d-c494166c7e58" />

`HoneyDog` es una herramienta de ciberseguridad activa y engaño (*deception*) diseñada en Python. Funciona levantando un servidor SSH simulado de alta interacción que acepta cualquier credencial de entrada, confunde a los atacantes con una shell falsa de GNU/Linux y audita en tiempo real cada comando ejecutado, enviando alertas push inmediatas a tu móvil a través de la API de Telegram.

A diferencia de las configuraciones rígidas, `HoneyDog` permite al operador **definir dinámicamente el puerto de escucha** por línea de comandos, facilitando su despliegue en puertos alternativos o suplantando el servicio SSH real mediante privilegios de administrador.

---

## 🧠 El Factor Criptográfico: Simulación Realista vs Mecanismos SSH

Un aspecto avanzado de `HoneyDog` es que genera una clave criptográfica RSA aleatoria de 2048 bits (`paramiko.RSAKey.generate(2048)`) en cada inicialización. 

Esto provoca un comportamiento fascinante durante las fases de pruebas: si detienes el script y lo vuelves a arrancar, la "huella digital" (*fingerprint*) del servidor trampa cambia por completo. Al intentar reconectarte desde la misma máquina, tu cliente SSH de Linux saltará con una alerta de seguridad crítica:

@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@    WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!     @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
IT IS POSSIBLE THAT SOMEONE IS DOING SOMETHING NASTY!
Someone could be eavesdropping on you right now (man-in-the-middle attack)!

## 🛡️ ¿Qué demuestra esto?

Realismo absoluto: El honeypot no es un simple script que escupe texto; implementa el protocolo de cifrado a bajo nivel de tal forma que los clientes SSH legítimos lo tratan como un servidor real, activando sus alertas contra ataques de suplantación de identidad o Man-in-the-Middle (MitM).

Gestión de la persistencia: Para limpiar la caché de claves de tu máquina de pruebas y poder volver a morder el anzuelo, basta con purgar el registro del puerto ejecutando:

ssh-keygen -f '~/.ssh/known_hosts' -R '[127.0.0.1]:2222'

(Sustituye 2222 por el puerto dinámico que hayas levantado).

---

## 🎨 Características Principales

* 🎛️ **Puerto Dinámico:** Flexibilidad total para iniciar el cebo en cualquier puerto válido (1-65535) desde la consola.
* 🧵 **Arquitectura Multihilo:** Capaz de gestionar múltiples conexiones simultáneas de atacantes sin saturar el sistema operativo host.
* 🛡️ **Simulación de Shell:** Emula un prompt realista de Ubuntu/Linux con respuestas controladas a comandos comunes (`whoami`, `ls`, `cat`, etc.).
* 🚨 **Alertas Push en Tiempo Real:** Integración nativa con la API de bots de Telegram para notificar al instante accesos y comandos peligrosos.
* 🔑 **Securización del Entorno:** Gestión de credenciales críticas (Tokens y Chat IDs) mediante variables de entorno aisladas (`.env`).

---

## ⚙️ Interfaz de Consola

       /\_/\  🐾  [ H O N E Y D O G   H O N E Y P O T ]
      ( o.o )     -------------------------------------
       > ^ <      Alineando defensas... ¡Trampa lista!
      /     \     
     (_|_|_|_)    -- by david-rtd | Active Defense Tool --

___

🚀 Instalación y Despliegue
Sigue estos pasos para desplegar el entorno virtual aislado en tu sistema Linux (Kali, Fedora, Ubuntu):

1. Clonar el repositorio y acceder

git clone [https://github.com/david-rtd/honeydog.git](https://github.com/david-rtd/honeydog.git)

cd honeydog

2. Crear y activar el entorno virtual (venv)

Para cumplir con la especificación PEP 668 y evitar conflictos con paquetes del sistema:

python3 -m venv .venv

source .venv/bin/activate

3. Instalar dependencias requeridas

pip install -r requirements.txt

4. Configuración del Entorno (.env)

## IMPORTANTE: https://t.me/botfather
Este es el enlace oficial de BotFather, cualquier otro enlace puede ser una estafa

___


Por motivos de seguridad, nunca subas tus credenciales al repositorio. Crea un archivo .env en la raíz del proyecto:

nano .env 

Añade tus credenciales con el siguiente formato (sin espacios):

Fragmento de código:

TELEGRAM_TOKEN=tu_token_de_botfather_aqui 

TELEGRAM_CHAT_ID=tu_id_numérico_aquí

(Nota: Asegúrate de que tu .gitignore incluye el archivo .env antes de hacer el push).

___

### Conseguir el id numerico
Abre el bot que creaste en el BotFather real y asegúrate de haberle dado al botón Iniciar / Start (si ya lo hiciste antes, dale otra vez por si acaso).

Abre una pestaña en tu navegador web.

Copia la siguiente dirección en la barra de URL, pero cambiando la palabra TU_TOKEN_AQUÍ por el token largo que te dio BotFather (el que empieza por números y tiene dos puntos):

https://api.telegram.org/botTELEGRAM_TOKEN/getUpdates Dale a Enter

Te saldra este contenido:

"message": { "from": { "id": 123456789, "is_bot": false, "first_name": "Usuario", "username": "tu_usuario" } }

Donde "id", copialo y agregalo en TELEGRAM_CHAT_ID

___

🕹️ Modo de Uso (Control del Puerto)

<img width="642" height="178" alt="Captura de pantalla 2026-06-10 215517" src="https://github.com/user-attachments/assets/3fb773db-a943-471b-a328-7139195a1f5b" />

HoneyDog gestiona los puertos de manera inteligente. Puedes lanzarlo de las siguientes formas:

Puerto por defecto (2222): Ideal para pruebas rápidas sin interferir con tu SSH legítimo.

python honeydog.py
Puerto personalizado (Ej. 4444):

python honeydog.py 4444
Puerto SSH real (22): Reemplaza el servicio real para interceptar ataques directos. Nota: Los puertos inferiores al 1024 requieren privilegios de sudo en Linux.

sudo python honeydog.py 22

Para apagar el cebo de forma segura, usa Ctrl + C. El script interceptará la señal limpiando los sockets y despidiéndose con un toque de personalidad:

🐾 [HoneyDog] Queria mas galletas :( Guau, Guau

___

🧪 Pruebas de Concepto (Auditoría Local)

Para verificar el comportamiento del honeypot en el puerto personalizado 4444, abre una terminal secundaria y simula el ataque:

ssh cualquier_usuario@127.0.0.1 -p 4444

Introduce cualquier credencial. El sistema concederá acceso inmediato.

Inyecta comandos en la shell simulada (whoami, ls, o lee el archivo trampa con cat flag.txt).

Comprueba tu Telegram: el bot te enviará reportes formateados con la IP origen, contraseñas capturadas y los payloads en tiempo real.

<img width="502" height="393" alt="Captura de pantalla 2026-06-10 215531" src="https://github.com/user-attachments/assets/b5383005-e697-48cc-bee5-c5c813d5470c" />


___

📁 Estructura del Repositorio
honeydog.py: Lógica principal del honeypot, gestión de hilos y parsing de argumentos.

requirements.txt: Dependencias del entorno (paramiko, requests, python-dotenv).

honeydog_access.log: Historial local de IPs y contraseñas recolectadas.

honeydog_commands.log: Registro secuencial de la telemetría y comandos del atacante.

___

📄 Licencia y Descargo de Responsabilidad

Este proyecto ha sido desarrollado con fines exclusivamente educativos, de investigación y auditoría de sistemas (Blue Teaming). El autor no se responsabiliza del uso indebido de esta herramienta en redes no autorizadas.

Developed by david-rtd | Blue Team & Systems Automation
