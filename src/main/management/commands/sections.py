from django.core.management.base import BaseCommand, CommandError
from main.models import Section
from faker import Factory

fake = Factory.create('en_US')

sections = [('Теория вероятности', 'probabilitytheory'),
            ('ТФКП', 'complexanalysis'),
            ('Дифференциальная геометрия', 'diffgeometry'),
            ('Дифференциальные уравнения', 'diffequation'),
            ('Функциональный анализ', 'functionalanalysis'),
            ('Математический анализ', 'mathanalysis'),
            ('Линейная алгебра', 'linearalgebra'),
            ('Аналитическая геометрия', 'analyticgeometry')]


def create_section():
    for title, slug in sections:
        Section.objects.create(title=title, slug=slug)


class Command(BaseCommand):
    def handle(self, *args, **options):
        create_section()
