import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from core.models import Paciente, Especialidad  # Cambia si tu app tiene otro nombre
import os


def parse_date(value):
    try:
        return make_aware(datetime.strptime(value, "%Y-%m-%d %H:%M:%S"))
    except:
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except:
            return None


def parse_value(value):
    if value in ("", "NULL", None):
        return None
    return value.strip()


class Command(BaseCommand):
    help = 'Importa pacientes y especialidades desde archivos CSV'

    def handle(self, *args, **kwargs):
        # File paths
        pacientes_file_path = os.path.join('core', 'management', 'commands', 'adsoperu_dental.csv')
        especialidades_file_path = os.path.join('core', 'management', 'commands', 'especialidad.csv')

        pacientes_count = 0
        especialidades_count = 0

        # ✅ --- IMPORT PACIENTES ---
        try:
            with open(pacientes_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    dni = parse_value(row["dni_pac"])
                    if dni and Paciente.objects.filter(dni_pac=dni).exists():
                        self.stdout.write(self.style.WARNING(f"⚠️ Paciente con DNI {dni} ya existe. Saltando..."))
                        continue
                    paciente = Paciente(
                        nomb_pac=parse_value(row["nomb_pac"]),
                        apel_pac=parse_value(row["apel_pac"]),
                        edad_pac=parse_value(row["edad_pac"]),
                        ocupacion=parse_value(row["ocupacion"]),
                        lugar_nacimiento=parse_value(row["lugar_nacimiento"]),
                        informacion_clinica=parse_value(row["informacion_clinica"]),
                        dire_pac=parse_value(row["dire_pac"]),
                        telf_pac=parse_value(row["telf_pac"]),
                        dni_pac=parse_value(row["dni_pac"]),
                        foto_paciente=parse_value(row["foto_paciente"]),
                        fena_pac=parse_date(row["fena_pac"]),
                        fecha_registro=parse_date(row["fecha_registro"]),
                        civi_pac=parse_value(row["civi_pac"]),
                        afil_pac=parse_value(row["afil_pac"]),
                        aler_pac=parse_value(row["aler_pac"]),
                        emai_pac=parse_value(row["emai_pac"]),
                        titu_pac=parse_value(row["titu_pac"]),
                        pais_id=parse_value(row["pais_id"]),
                        departamento_id=parse_value(row["departamento_id"]),
                        provincia_id=parse_value(row["provincia_id"]),
                        distrito_id=parse_value(row["distrito_id"]),
                        observacion=parse_value(row["observacion"]),
                        registro_pac=parse_date(row["registro_pac"]),
                        detalleodontograma_pac=parse_value(row["detalleodontograma_pac"]),
                        # sexo, esta_pac, estudios_pac → usarán valores por defecto
                    )
                    paciente.save()
                    pacientes_count += 1
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Archivo de pacientes no encontrado: {pacientes_file_path}"))
        except KeyError as e:
            self.stderr.write(self.style.ERROR(f"Columna faltante en pacientes: {e}"))

        # ✅ --- IMPORT ESPECIALIDADES ---
        try:
            with open(especialidades_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    nombre = parse_value(row["nombre_especialidad"])
                    descripcion = parse_value(row["descripcion_especialidad"])

                    # Check if especialidad already exists by name
                    if nombre and Especialidad.objects.filter(nombre=nombre).exists():
                        self.stdout.write(self.style.WARNING(f"⚠️ Especialidad '{nombre}' ya existe. Saltando..."))
                        continue

                    especialidad = Especialidad(
                        nombre=nombre,
                        descripcion=descripcion,
                        honorariosPorcentaje=0.3  # default value
                    )
                    especialidad.save()
                    especialidades_count += 1

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Archivo de especialidades no encontrado: {especialidades_file_path}"))
        except KeyError as e:
            self.stderr.write(self.style.ERROR(f"Columna faltante en especialidades: {e}"))

        # ✅ --- FINAL MESSAGE ---
        self.stdout.write(self.style.SUCCESS(f"✅ {pacientes_count} pacientes importados correctamente"))
        self.stdout.write(self.style.SUCCESS(f"✅ {especialidades_count} especialidades importadas correctamente"))
