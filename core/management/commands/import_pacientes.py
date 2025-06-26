import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from core.models import Paciente  # Cambia si tu app tiene otro nombre


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
    help = 'Importa pacientes desde un archivo CSV'

    def handle(self, *args, **kwargs):
        file_path = './adsoperu_dental.csv'
        count = 0

        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    dni = parse_value(row["dni_pac"])
                    if dni and Paciente.objects.filter(dni_pac=dni).exists():
                        self.stdout.write(self.style.WARNING(f"⚠️  Paciente con DNI {dni} ya existe. Saltando..."))
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
                    count += 1
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Archivo no encontrado: {file_path}"))
            return
        except KeyError as e:
            self.stderr.write(self.style.ERROR(f"Columna faltante: {e}"))
            return

        self.stdout.write(self.style.SUCCESS(f"✅ {count} pacientes importados correctamente"))
