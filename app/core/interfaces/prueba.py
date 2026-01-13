# motor.py — EJEMPLO QUE VIOLA OCP

class MotorAsignacion:

    def procesar(self, postulacion, tipo_estrategia):
        if tipo_estrategia == "art52":
            return "Cupo Aceptado" if postulacion["nota"] >= 80 else "Cupo Rechazado"

        elif tipo_estrategia == "vulnerabilidad":
            return "Cupo Aceptado" if postulacion.get("vulnerable", False) else "Cupo Rechazado"

        elif tipo_estrategia == "merito":
            return "Cupo Aceptado" if postulacion["nota"] > 90 else "Cupo Rechazado"

        # Si luego agregas otra estrategia:
        # elif tipo_estrategia == "otra_nueva":
        #     ... tienes que seguir MODIFICANDO ESTE ARCHIVO

        else:
            return "Estrategia no reconocida"

