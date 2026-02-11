# Script de instalacion y configuracion automatica para Raspberry Pi (Rover autonomo)
# Instala las dependencias necesarias y configura el hardware (SPI, camara CSI)

import subprocess

def check_and_install(package):
    """Comprueba si un paquete Python esta instalado. Si no lo esta, lo instala con pip3."""
    try:
        # Intenta importar el paquete para ver si ya existe
        __import__(package)
        return True
    except ImportError:
        # Si no esta instalado, intenta instalarlo con pip3
        install_command = f"sudo pip3 install {package}"
        try:
            subprocess.run(install_command, shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            print(f"Failed to install {package}.")
            return False

def apt_install(package):
    """Instala un paquete del sistema usando apt-get"""
    install_command = f"sudo apt-get install -y {package}"
    try:
        subprocess.run(install_command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to install {package} via apt-get.")
        return False

def custom_install(command):
    """Ejecuta un comando shell personalizado para instalaciones que no usan pip ni apt."""
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to execute custom command: {command}")
        return False

def get_raspberry_pi_version():
    """
    Detecta el modelo de Raspberry Pi leyendo el archivo del sistema.
    Retorna: 3 = Pi 5, 2 = Pi 3, 1 = otro modelo, 0 = no detectado.
    """
    print("Getting Raspberry Pi version...")
    try:
        # Lee el modelo desde el device tree del firmware
        result = subprocess.run(['cat', '/sys/firmware/devicetree/base/model'], capture_output=True, text=True)
        if result.returncode == 0:
            model = result.stdout.strip()
            if "Raspberry Pi 5" in model:
                print("Detected Raspberry Pi 5")
                return 3
            elif "Raspberry Pi 3" in model:
                print("Detected Raspberry Pi 3")
                return 2
            else:
                print(f"Detected Raspberry Pi {model}")
                return 1
        else:
            print("Failed to get Raspberry Pi model information.")
            return 0
    except Exception as e:
        print(f"Error getting Raspberry Pi version: {e}")
        return 0

def update_config_file(file_path, command, value):
    """
    Modifica un parametro en un archivo de configuracion (formato clave=valor).
    Si la linea existe (activa o comentada con #), la reemplaza.
    Si no existe, la anade al final del archivo.
    """
    new_content = []
    command_found = False
    with open(file_path, 'r') as f:
        lines = f.readlines()
    for line in lines:
        stripped_line = line.strip()
        # Busca la linea activa o comentada que coincida con el comando
        if stripped_line.startswith(command) or stripped_line.startswith(f'#{command}'):
            command_found = True
            new_content.append(f'{command}={value}\n')
        else:
            new_content.append(line)
    # Si el comando no existia, lo anade al final
    if not command_found:
        new_content.append(f'\n{command}={value}\n')
    with open(file_path, 'w') as f:
        f.writelines(new_content)
    print(f"Updated {file_path} with '{command}={value}'")

def config_camera_to_config_txt(file_path, command, value=None):
    """
    Configura el dtoverlay de la camara CSI en config.txt.
    Elimina configuraciones previas de camara (ov5647/imx219) y escribe la nueva.
    El parametro 'value' es opcional (ej: cam0/cam1 en Pi 5).
    """
    new_content = []
    command_found = False
    with open(file_path, 'r') as f:
        lines = f.readlines()
    for line in lines:
        stripped_line = line.strip()
        # Elimina cualquier linea con configuracion previa de camara
        if 'ov5647' in stripped_line or 'imx219' in stripped_line:
            continue
        # Busca una linea dtoverlay existente para este modelo de camara
        if stripped_line.startswith(f'dtoverlay={command}') or stripped_line.startswith(f'#dtoverlay={command}'):
            command_found = True
            if value:
                new_content.append(f'dtoverlay={command},{value}\n')
            else:
                new_content.append(f'dtoverlay={command}\n')
        else:
            new_content.append(line)
    # Si no se encontro, anade la configuracion al final
    if not command_found:
        if value:
            new_content.append(f'\ndtoverlay={command},{value}\n')
        else:
            new_content.append(f'\ndtoverlay={command}\n')
    with open(file_path, 'w') as f:
        f.writelines(new_content)
    value_str = f",{value}" if value else ""
    print(f"Updated {file_path} with 'dtoverlay={command}{value_str}'")

def backup_file(file_path):
    """Crea una copia de seguridad del archivo anadiendo la extension .bak."""
    config_path = file_path
    backup_path = config_path + '.bak'
    print("Backing up ", backup_path)
    try:
        # Lee el archivo original en binario y lo copia al backup
        with open(config_path, 'rb') as src_file:
            with open(backup_path, 'wb') as dst_file:
                dst_file.write(src_file.read())
        print(f"Backup of {config_path} created at {backup_path}")
    except Exception as e:
        print(f"Error backing up {config_path}: {e}")

def config_file():
    """
    Configura /boot/firmware/config.txt segun el modelo de Pi y la camara del usuario.
    - Activa SPI (necesario para comunicacion con perifericos)
    - Desactiva la autodeteccion de camara
    - Configura el dtoverlay de la camara segun el modelo (ov5647 o imx219)
    - En Pi 5: pregunta el puerto de camara (cam0/cam1)
    - En Pi 3: desactiva el audio (comparte recursos con la camara)
    """
    pi_version = get_raspberry_pi_version()
    file_path = '/boot/firmware/config.txt'
    # Crear backup antes de modificar
    backup_file(file_path)
    # Activar SPI y desactivar autodeteccion de camara
    update_config_file(file_path, 'dtparam=spi', 'on')
    update_config_file(file_path, 'camera_auto_detect', '0')
    # Preguntar al usuario el modelo de camara (con validacion)
    while True:
        camera_model = input("\nEnter the camera model (e.g., ov5647 or imx219): ").strip().lower()
        if camera_model not in ['ov5647', 'imx219']:
            print("Invalid input. Please enter either ov5647 or imx219.")
        else:
            break
    # Configuracion especifica segun la version de Raspberry Pi
    if pi_version == 3:
        # Pi 5: tiene dos puertos de camara, se debe indicar cual se usa
        print("Setting up for Raspberry Pi 5")
        while True:
            camera_port = input("You have a Raspberry Pi 5. Which camera port is the camera connected to? cam0 or cam1: ").strip().lower()
            if camera_port not in ['cam0', 'cam1']:
                print("Invalid input. Please enter either cam0 or cam1.")
            else:
                break
        config_camera_to_config_txt(file_path, camera_model, camera_port)
    elif pi_version == 2:
        # Pi 3: hay que desactivar el audio porque comparte bus con la camara
        print("Setting up for Raspberry Pi 3")
        update_config_file(file_path, 'dtparam=audio', 'off')
        config_camera_to_config_txt(file_path, camera_model)
    else:
        # Otros modelos: configuracion basica de camara
        config_camera_to_config_txt(file_path, camera_model)

def main():
    """
    Funcion principal: instala todas las dependencias y configura el hardware.
    Dependencias:
      - python3-dev, python3-pyqt5: herramientas de desarrollo y GUI Qt5
      - gpiozero: control de pines GPIO
      - numpy: calculo numerico (usado en procesamiento de imagen)
      - rpi-ws281x-python: control de LEDs NeoPixel (WS281x)
    """
    # Diccionario para rastrear el estado de instalacion de cada dependencia
    install_status = {
        "python3-dev python3-pyqt5": False,
        "gpiozero": False,
        "numpy": False,
        "rpi-ws281x-python (custom install)": False
    }

    # Actualizar la lista de paquetes del sistema
    subprocess.run("sudo apt-get update", shell=True, check=True)
    # Instalar cada dependencia con el metodo adecuado
    install_status["python3-dev python3-pyqt5"] = apt_install("python3-dev python3-pyqt5")
    install_status["gpiozero"] = check_and_install("gpiozero")
    install_status["numpy"] = check_and_install("numpy")
    install_status["rpi-ws281x-python (custom install)"] = custom_install("cd ./Libs/rpi-ws281x-python/library && sudo python3 setup.py install")
    # Verificar si todas las dependencias se instalaron correctamente
    if all(install_status.values()):
        print("\nAll libraries have been installed successfully.")
        # Si todo se instalo bien, proceder a configurar el hardware
        config_file()
        print("Please reboot your Raspberry Pi to complete the installation.")
    else:
        # Mostrar las dependencias que fallaron
        missing_libraries = [lib for lib, status in install_status.items() if not status]
        print(f"\nSome libraries have not been installed yet: {', '.join(missing_libraries)}. Please run the script again.")

# Punto de entrada: solo ejecuta main() si el script se ejecuta directamente
if __name__ == "__main__":
    main()
