import logging
from django.core.management import BaseCommand

from pilotlog.utils import Importer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Export data to a specified CSV file'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='The path to the CSV file to export')

    def handle(self, *args, **options):
        filename = options['filename']
        try:
            importer = Importer(import_source=None, export_source=filename)
            importer.export_data()
        except Exception as e:
            logger.error(f"Export was unsuccesful: {e}")
