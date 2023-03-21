import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        csv_file = open(
            f'{settings.BASE_DIR}/data/ingredients.csv', encoding="utf8"
        )
        data_reader = csv.reader(csv_file, delimiter=',')
        items = []
        for row in data_reader:
            item = Ingredient(name=row[0], measurement_unit=row[1])
            items.append(item)
        Ingredient.objects.bulk_create(items)
