from datetime import datetime

from django.core.management.base import BaseCommand

from waitlist.models import Instance


class Command(BaseCommand):
    help = 'Deletes old instances'

    def handle(self, *args, **options):
        instances = list( Instance.objects.all() )
        for instance in instances:
            delta = datetime.utcnow() - instance.last_modified
            if delta.days >= 30:
                instance.delete()
                
