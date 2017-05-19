from django.core.management.base import BaseCommand, CommandError
from BOLT.models import News
from faker import Factory

fake = Factory.create('en_US')
news = [('Добавлены новые задания',
         'На нашем сайте появились новые задания в категории "Теория вероятностей". Это номера из наших студенческих домашних заданий, спешим поделиться ими с вами. Напоминаем, что все возникшие вопросы можете задавать в комментариях, или можно связаться с нами напрямую, все контакты размещены в разделе "О нас". Успехов!'),
        ('Обратная связь',
         'Для того, чтобы связаться с нами по какому-либо вопросу, перейдите в раздел "О нас", в нем указаны все доступные способы. Так же, зарегистрированные на нашем сайте пользователи могут оставлять комментарии под каждой задачей. В них вы можете задавать свои вопросы по ходу решения и указывать, с чем вы не согласны. Нашли ошибку? Считаете предложенное решение неверным? Пишите об этом в комментариях!'),
        ('Наш сайт начал свою работу',
         'Всем доброго времени суток! Сегодня наш сайт начал свою работу. Здесь будут выкладываться подробные решения задач по основным студенческим дисциплинам. Слева представлен список разделов, выберите нужный предмет, и вы сразу попадете в архив имеющихся на данный момент задач. Кроме того, вы можете вбить в поисковую строку условие задания, а затем просто выбрать из списка предложенных. После этого вставьте свои исходные данные, и вы получите подробно расписанное решение именно вашей задачи. Успехов!')]


def create_news():
    for title, text in news:
        News.objects.create(
            title=title,
            text=text,
        )


class Command(BaseCommand):
    #     def add_arguments(self, parser):
    #         parser.add_argument('count')

    def handle(self, *args, **options):
        create_news()