import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
# CHANGE 'core.models' to your actual app name
from odontograma.models import Diente

class Command(BaseCommand):
    help = 'Seeds the Diente table with coordinates from the JSON fixture'

    def add_arguments(self, parser):
        # Optional: Allow passing a different filename
        parser.add_argument(
            '--file', 
            type=str, 
            default='diente_fixtures.json',
            help='Path to the JSON file containing tooth coordinates'
        )

    def handle(self, *args, **options):
        file_path = 'diente_fixtures.json'

        # Construct full path (assuming file is in root or same dir)
        # You might need to adjust this base path depending on where you run the script
        if not os.path.exists(file_path):
             self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
             return

        self.stdout.write(f"Reading from {file_path}...")

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            count_created = 0
            count_updated = 0

            for entry in data:
                # The script from the previous step outputs Django fixture format:
                # {"model": "...", "pk": 18, "fields": {...}}
                fields = entry.get('fields', {})
                pk = entry.get('pk')
                
                if not pk or not fields:
                    continue

                numero = fields.get('numero')
                raw_hitbox = fields.get('hitbox_json')

                # CLEANUP: The fixture might have saved the JSON as a string.
                # We convert it back to a Dict so Django saves it as a proper JSON Object.
                if isinstance(raw_hitbox, str):
                    try:
                        hitbox_data = json.loads(raw_hitbox)
                    except json.JSONDecodeError:
                        self.stdout.write(self.style.WARNING(f"Invalid JSON in hitbox for tooth {numero}"))
                        hitbox_data = {}
                else:
                    hitbox_data = raw_hitbox

                # Update or Create logic
                obj, created = Diente.objects.update_or_create(
                    numero=numero,
                    defaults={
                        'hitbox_json': hitbox_data
                    }
                )

                if created:
                    count_created += 1
                else:
                    count_updated += 1

            self.stdout.write(self.style.SUCCESS(
                f'Successfully seeded Dientes. Created: {count_created}, Updated: {count_updated}'
            ))

        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Failed to decode JSON file.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))