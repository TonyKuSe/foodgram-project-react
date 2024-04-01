import json
from django.conf import settings
from django.core.management import BaseCommand

from reviews.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка из json файла'

    def handle(self, *args, **kwargs):
        data_path = settings.BASE_DIR
        json_file_path = f'{data_path}/data/ingredients.json'
        with open(
            json_file_path,
            'r',
            encoding='utf-8'
        ) as json_file:
            reader = json.load(json_file)
            ingredients = []
            for data in reader:
                ingredient = Ingredient.objects.create(
                    name=data['name'],
                    measurement_unit=data['measurement_unit']
                )
                ingredients.append(ingredient)
        self.stdout.write(self.style.SUCCESS('Все ингридиенты загружены!'))
