from app.core.container import Container
import sys
import json

def main():
    """
    Punto de entrada principal de la aplicación.
    Inicializa el contenedor y ejecuta el motor.
    """
    print("==============================================")
    print("==       Motor de Asignación de Cupos       ==")
    print("==============================================")
    
    container = Container()
    
    # Validar la existencia y formato del config.json
    try:
        container.config()
    except FileNotFoundError:
        print("Error fatal: No se encontró el archivo 'config.json'.")
        print("Asegúrese de que el archivo exista en la raíz del proyecto.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("Error fatal: El archivo 'config.json' tiene un formato JSON inválido.")
        sys.exit(1)
        
    motor = container.motor()
    motor.ejecutar_proceso()

if __name__ == "__main__":
    main()
