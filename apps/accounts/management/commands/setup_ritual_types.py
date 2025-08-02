from django.core.management.base import BaseCommand
from apps.accounts.models import RitualType

class Command(BaseCommand):
    help = 'Create test RitualType records for external meditation API'

    def handle(self, *args, **options):
        # Define the ritual types that correspond to external API endpoints
        ritual_types = [
            {
                'name': 'Sleep Manifestation',
                'description': 'External meditation for sleep manifestation'
            },
            {
                'name': 'Morning Spark', 
                'description': 'External meditation for morning spark'
            },
            {
                'name': 'Calming Reset',
                'description': 'External meditation for calming reset'
            },
            {
                'name': 'Dream Visualizer',
                'description': 'External meditation for dream visualization'
            }
        ]
        
        self.stdout.write("Setting up RitualType records for external meditation API...")
        
        created_count = 0
        for ritual_type_data in ritual_types:
            ritual_type, created = RitualType.objects.get_or_create(
                name=ritual_type_data['name'],
                defaults={'description': ritual_type_data['description']}
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Created RitualType: {ritual_type.name} (ID: {ritual_type.id})")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"ℹ️ RitualType already exists: {ritual_type.name} (ID: {ritual_type.id})")
                )
        
        self.stdout.write(f"\nSetup complete! {created_count} new RitualType records created.")
        self.stdout.write("\nAvailable RitualTypes for testing:")
        for rt in RitualType.objects.all():
            self.stdout.write(f"  ID: {rt.id}, Name: {rt.name}") 