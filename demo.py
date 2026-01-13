class LectorMock:
    """MALA PRÁCTICA: nombre de método incompatible con la interfaz esperada."""
    def load_data(self):
        # NOTA: usar 'load_data' en vez de 'cargar_datos' rompe la sustitución (LSP).
        print("LectorMock (malo) leyendo en memoria")
        aspirantes = [{"id": "1", "nombre": "Ana", "preferencias": "101|102"}]
        carreras = [{"id": "101", "nombre": "Ingeniería"}]
        return aspirantes, carreras


class LectorCSV:
    """MALA PRÁCTICA: rutas fijas, manejo silencioso de errores."""
    def __init__(self):
        self.path_aspirantes = "data/aspirantes.csv"
        self.path_carreras = "data/carreras.csv"

    def cargar_datos(self):
        aspirantes = []
        carreras = []

        try:
            with open(self.path_carreras, encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(",")
                    carreras.append({
                        "id": int(parts[0]),
                        "nombre": parts[1]
                    })
        except Exception:
            # SILENCIA errores
            pass

        print("LectorCSV (malo): cargar_datos terminó (o no).")
        return aspirantes, carreras