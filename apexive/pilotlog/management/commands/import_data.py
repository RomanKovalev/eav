import logging

from django.core.management import BaseCommand

from pilotlog.utils import Importer


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Import data from a specified JSON file'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str, help='The path to the JSON file to import')

    def handle(self, *args, **options):
        filename = options['filename']
        try:
            importer = Importer(import_source=filename, export_source=None)
            importer.import_data()
        except Exception as e:
            logger.error(f"Export was unsuccesful: {e}")
