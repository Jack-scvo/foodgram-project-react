import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_file = open(
            f'{settings.BASE_DIR}/data/ingredients.csv', encoding="utf8"
        )
        data_reader = csv.DictReader(csv_file, delimiter=',')
        items = []
        for row in data_reader:
            item = model(**row)
            items.append(item)
        Ingredient.objects.bulk_create(items)
