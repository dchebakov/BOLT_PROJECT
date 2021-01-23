from django.core.management.base import BaseCommand, CommandError
from main.models import Section, Task
from faker import Factory

fake = Factory.create('en_US')

tasks = [(
    'В лифт К-этажного дома сели N пассажиров (N<K). Каждый независимо от других с одинаковой вероятностью может выйти на любом (начиная со второго) этаже. Определить вероятность, что: а) все вышли на разных этажах; б) по крайней мере двое сошли на одном этаже.',
    'probabilitytheory', 'probabilitytheoryEx1')]


def create_section():
    for title, slug, function_name in tasks:
        Task.objects.create(
            title=title,
            section=Section.objects.get(slug=slug),
            function_name=function_name
        )


class Command(BaseCommand):
    def handle(self, *args, **options):
        create_section()
