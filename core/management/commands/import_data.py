import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from core.models import Paciente, Especialidad, Clinica,  Consultorio, Enfermedad, Cita, CategoriaTratamiento, Tratamiento, Alergia
import os
from django.contrib.auth import get_user_model

User = get_user_model()

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

        #crear Clinicas

        clinicaIquitos, created = Clinica.objects.update_or_create(
            nomb_clin='Clinica Dental Sede Iquitos', # The field used to find the match
            defaults={
                'direc_clin': 'Calle Callao 176',
                'telf_clin': 917435154,
                'email_clin': 'email 1',
                'telegram_chat_id': '-5055463094', # <--- Replace with your actual Iquitos Chat ID
            }
        )

        # 2. Yurimaguas
        clinicaYurimaguas, created = Clinica.objects.update_or_create(
            nomb_clin='Clinica Dental Filial Yurimaguas', # The field used to find the match
            defaults={
                'direc_clin': 'Calle 15 de agosto 726',
                'telf_clin': 900366452,
                'email_clin': 'email 2',
                'telegram_chat_id': '-5041569133', # <--- Replace with your actual Yurimaguas Chat ID
            }
        )

        alergias = [
            "Ninguna",
            "Látex",
            "Penicilina",
            "Amoxicilina",
            "AINEs (Aspirina, Ibuprofeno, Naproxeno)",
            "Lidocaína (Anestesia local)",
            "Articaína",
            "Metales (Níquel, Cromo, Cobalto)",
            "Resinas acrílicas / Metacrilatos",
            "Sulfitos (preservante en anestesia)",
            "Yodo / Yodopovidona",
            "Clindamicina",
            "Codeína",
            "Eritromicina",
            "Cefalosporinas",
            "Hipoclorito de Sodio"
        ]

        # Tu código para guardar en la BD
        for alergia in alergias:
            # Usamos _ para la variable 'created' ya que no la estamos usando
            obj, created = Alergia.objects.get_or_create(nombre_ale=alergia)
            if created:
                self.stdout.write(f"Alergia creada: {obj.nombre_ale}")
        

        #create consultorios

        for i in range(2):
            consultorio, create = Consultorio.objects.get_or_create(
                nombreConsultorio = f'Iquitos n {i+1}',
                clinica = clinicaIquitos
            )
        for i in range(3):
            consultorio, create = Consultorio.objects.get_or_create(
                nombreConsultorio = f'Yurimaguas n {i+1}',
                clinica = clinicaYurimaguas
            )
        # File paths
        pacientes_iquitos_file_path = os.path.join('core', 'management', 'commands', 'pacientes_iquitos.csv')
        pacientes_yurimaguas_file_path = os.path.join('core', 'management', 'commands', 'pacientes_yurimaguas.csv')
        especialidades_file_path = os.path.join('core', 'management', 'commands', 'especialidad.csv')
        enfermedades_file_path = os.path.join('core', 'management', 'commands', 'enfermedades.csv')

        pacientes_count = 0
        especialidades_count = 0

        # ✅ --- IMPORT PACIENTES ---
        try:
            with open(pacientes_iquitos_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    dni = parse_value(row["dni_pac"])
                    if dni and Paciente.objects.filter(dni_pac=dni).exists():
                        paciente = Paciente.objects.filter(dni_pac=dni).first()
                        if paciente.old_cod_pac != parse_value(row['codi_pac']):
                            paciente.old_cod_pac = parse_value(row['codi_pac'])
                            paciente.save()
                        continue
                    if row['sexo_pac'] == 'M':
                        sexo_pac = 'MASCULINO'
                    else:
                        sexo_pac = 'FEMENINO'
                    paciente = Paciente(
                        old_cod_pac=parse_value(row["codi_pac"]),
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
                        sexo=sexo_pac,
                        clinica = clinicaIquitos
                        #esta_pac, estudios_pac → usarán valores por defecto
                    )
                    paciente.save()
                    pacientes_count += 1
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Archivo de pacientes no encontrado: {pacientes_iquitos_file_path}"))
        except KeyError as e:
            self.stderr.write(self.style.ERROR(f"Columna faltante en pacientes: {e}"))
        #pacientes yurimaguas

        try:
            with open(pacientes_yurimaguas_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    dni = parse_value(row["dni_pac"])
                    if dni and Paciente.objects.filter(dni_pac=dni).exists():
                        paciente = Paciente.objects.filter(dni_pac=dni).first()
                        if paciente.old_cod_pac != parse_value(row['codi_pac']):
                            paciente.old_cod_pac = parse_value(row['codi_pac'])
                            paciente.save()
                        continue
                    if row['sexo_pac'] == 'M':
                        sexo_pac = 'MASCULINO'
                    else:
                        sexo_pac = 'FEMENINO'
                    paciente = Paciente(
                        old_cod_pac=parse_value(row["codi_pac"]),
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
                        sexo=sexo_pac,
                        clinica = clinicaYurimaguas
                        #esta_pac, estudios_pac → usarán valores por defecto
                    )
                    paciente.save()
                    pacientes_count += 1
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Archivo de pacientes no encontrado: {pacientes_yurimaguas_file_path}"))
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

        # ✅ --- IMPORT ENFERMEDADES ---
        enfermedades_count=0
        try:
            with open(enfermedades_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    codigo = parse_value(row.get("codi_enf"))
                    descripcion = parse_value(row.get("desc_enf"))
                    estado = parse_value(row.get("esta_enf")) or 'S'

                    # Check if enfermedad already exists by codigo or descripcion
                    if (codigo and Enfermedad.objects.filter(codigo=codigo).exists()) or \
                    (descripcion and Enfermedad.objects.filter(descripcion=descripcion).exists()):
                        continue

                    enfermedad = Enfermedad(
                        codigo=codigo,
                        descripcion=descripcion,
                        estado=estado,
                    )
                    enfermedad.save()
                    enfermedades_count += 1

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Archivo de enfermedades no encontrado: {enfermedades_file_path}"))
        except KeyError as e:
            self.stderr.write(self.style.ERROR(f"Columna faltante en enfermedades: {e}"))

        # ✅ --- IMPORT CITAS ---
        citas_iquitos_file_path = os.path.join('core', 'management', 'commands', 'citas_iquitos.csv')
        citas_yurimaguas_file_path = os.path.join('core', 'management', 'commands', 'citas_yurimaguas.csv')
        citas_count = 0

        try:
            with open(citas_iquitos_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    old_cod_cit = parse_value(row["codi_cit"])

                    # skip if already exists
                    cita = Cita.objects.filter(old_cod_cit=old_cod_cit).first()
                    if cita:
                        continue

                    # find medico by old_cod_med
                    medico = None
                    if parse_value(row["codi_med"]).isdigit():
                        medico = User.objects.filter(old_cod_med=int(row["codi_med"])).first()

                    # find paciente by old_cod_pac
                    paciente = None
                    if parse_value(row["codi_pac"]).isdigit():
                        paciente = Paciente.objects.filter(old_cod_pac=int(row["codi_pac"])).first()

                    # parse fecha & hora
                    fecha_str = parse_value(row["fech_cit"])
                    fecha = None
                    hora = None
                    if fecha_str:
                        try:
                            dt = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
                            fecha = dt.date()
                            hora = dt.time()
                        except ValueError:
                            self.stdout.write(self.style.ERROR(f"❌ Fecha inválida: {fecha_str}"))
                            continue

                    # estado → cancelado/reprogramado
                    estado = parse_value(row["esta_cit"])
                    cancelado = (estado == "0")  # o depende de tu lógica real
                    reprogramado = (estado == "2")  # ejemplo

                    cita = Cita(
                        old_cod_cit=old_cod_cit,
                        medico=medico,
                        paciente=paciente,
                        fecha=fecha,
                        hora=hora,
                        cancelado=cancelado,
                        reprogramado=reprogramado,
                    )
                    cita._skip_signal = True
                    cita.save()
                    citas_count += 1

            self.stdout.write(self.style.SUCCESS(f"✅ {citas_count} citas insertadas."))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Archivo no encontrado: {citas_iquitos_file_path}"))
        except KeyError as e:
            self.stderr.write(self.style.ERROR(f"Columna faltante en citas: {e}"))

        try:
            with open(citas_yurimaguas_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    old_cod_cit = parse_value(row["codi_cit"])

                    # skip if already exists
                    cita = Cita.objects.filter(old_cod_cit=old_cod_cit).first()
                    if cita:
                        continue

                    # find medico by old_cod_med
                    medico = None
                    if parse_value(row["codi_med"]).isdigit():
                        medico = User.objects.filter(old_cod_med=int(row["codi_med"])).first()

                    # find paciente by old_cod_pac
                    paciente = None
                    if parse_value(row["codi_pac"]).isdigit():
                        paciente = Paciente.objects.filter(old_cod_pac=int(row["codi_pac"])).first()

                    # parse fecha & hora
                    fecha_str = parse_value(row["fech_cit"])
                    fecha = None
                    hora = None
                    if fecha_str:
                        try:
                            dt = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
                            fecha = dt.date()
                            hora = dt.time()
                        except ValueError:
                            self.stdout.write(self.style.ERROR(f"❌ Fecha inválida: {fecha_str}"))
                            continue

                    # estado → cancelado/reprogramado
                    estado = parse_value(row["esta_cit"])
                    cancelado = (estado == "0")  # o depende de tu lógica real
                    reprogramado = (estado == "2")  # ejemplo

                    cita = Cita(
                        old_cod_cit=old_cod_cit,
                        medico=medico,
                        paciente=paciente,
                        fecha=fecha,
                        hora=hora,
                        cancelado=cancelado,
                        reprogramado=reprogramado,
                    )
                    cita._skip_signal = True
                    cita.save()
                    citas_count += 1

            self.stdout.write(self.style.SUCCESS(f"✅ {citas_count} citas insertadas."))

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Archivo no encontrado: {citas_yurimaguas_file_path}"))
        except KeyError as e:
            self.stderr.write(self.style.ERROR(f"Columna faltante en citas: {e}"))

        categorias_file_path = os.path.join('core', 'management', 'commands', 'tratamientoCategoria.csv')
        tratamientos_file_path = os.path.join('core', 'management', 'commands', 'tratamientos.csv')

        categorias_count = 0
        tratamientos_count = 0
        
        # ---- CATEGORIAS ----
        try:
            with open(categorias_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    nombre = parse_value(row.get("nombre"))

                    if not nombre:
                        continue

                    # Check if already exists
                    if CategoriaTratamiento.objects.filter(nombre=nombre).exists():
                        continue

                    categoria = CategoriaTratamiento(nombre=nombre)
                    categoria.save()
                    categorias_count += 1

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Archivo de categorias no encontrado: {categorias_file_path}"))
        except KeyError as e:
            self.stderr.write(self.style.ERROR(f"Columna faltante en categorias: {e}"))

        # ---- TRATAMIENTOS ----
        try:
            with open(tratamientos_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    nombre = parse_value(row.get("nombre"))
                    precio_base = parse_value(row.get("precioBase"))
                    precio_convenio = parse_value(row.get("precioConvenio"))
                    categoria_nombre = parse_value(row.get("categoria"))

                    if not nombre or not precio_base or not categoria_nombre:
                        continue

                    # Buscar categoria por nombre
                    try:
                        categoria = CategoriaTratamiento.objects.get(nombre=categoria_nombre)
                    except CategoriaTratamiento.DoesNotExist:
                        self.stderr.write(self.style.ERROR(f"Categoria no encontrada: {categoria_nombre}"))
                        continue

                    # Evitar duplicados por nombre
                    if Tratamiento.objects.filter(nombre=nombre, categoria=categoria).exists():
                        continue

                    tratamiento = Tratamiento(
                        nombre=nombre,
                        precioBase=float(precio_base),
                        precioConvenio=float(precio_convenio) if precio_convenio and float(precio_convenio) > 0 else None,
                        categoria=categoria
                    )
                    tratamiento.save()
                    tratamientos_count += 1

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"Archivo de tratamientos no encontrado: {tratamientos_file_path}"))
        except KeyError as e:
            self.stderr.write(self.style.ERROR(f"Columna faltante en tratamientos: {e}"))
        

        # ✅ --- FINAL MESSAGE ---
        self.stdout.write(self.style.SUCCESS(f"✅ {pacientes_count} pacientes importados correctamente"))
        self.stdout.write(self.style.SUCCESS(f"✅ {especialidades_count} especialidades importadas correctamente"))
        self.stdout.write(self.style.SUCCESS(f"✅ {enfermedades_count} enfermedades importadas correctamente"))