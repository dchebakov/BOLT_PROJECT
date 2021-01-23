from django.db import models
from django.contrib.auth.models import User
from autoslug import AutoSlugField
from datetime import date
from imagekit.models.fields import ImageSpecField
from imagekit.processors import ResizeToFill, Adjust
from django.urls import reverse

COUNT_BEST_MEMBERS = 3
COUNT_TOP_TAGS = 5

SIGN_CHOICES = (
    (1, 'PLUS'),
    (-1, 'MINUS'),
)


class NewsManager(models.Manager):
    def get_new(self):
        return self.all().order_by('-date_created')


class News(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField()
    date_created = models.DateField(auto_now_add=True)
    slug = AutoSlugField(populate_from='title', unique=True, null=True)

    objects = NewsManager()

    class Meta:
        verbose_name = 'New'


    def get_absolute_url(self):
        return reverse('news', args=[str(self.title)])

    def __str__(self):
        return self.title


def img_url(self, filename):
    return 'users/user_%d/%s%s' % (self.user.id, str(date.today()), filename)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=img_url, blank=True, null=True)
    avatar_small = ImageSpecField([Adjust(contrast=1.2, sharpness=1.1),
                                   ResizeToFill(40, 40)],
                                  format='JPEG', options={'quality': 90})
    avatar_medium = ImageSpecField([Adjust(contrast=1.2, sharpness=1.1),
                                    ResizeToFill(70, 70)],
                                   format='JPEG', options={'quality': 90})

    def __str__(self):
        return self.user.username


class Topic(models.Model):
    title = models.CharField(max_length=30)
    slug = AutoSlugField(populate_from='title', unique=True, null=True)

    def get_task(self):
        return Task.objects.filter(topic=self.title)

    def get_absolute_url(self):
        return reverse('tag', args=[str(self.title)])

    def __str__(self):
        return self.title


class Section(models.Model):
    title = models.CharField(max_length=30, unique=True, null=True)
    slug = models.CharField(max_length=30, unique=True, null=True)

    def get_task(self):
        return Task.objects.filter(tags__in=[self])

    def get_absolute_url(self):
        return reverse('section', args=[str(self.slug)])

    def __str__(self):
        return self.title


class TaskManager(models.Manager):
    def get_new(self):
        return self.all().order_by('-date_created')

    def get_hot(self):
        return self.all().order_by('-rating')


class Task(models.Model):
    title = models.TextField()
    description = models.TextField(blank=True, default='')
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    function_name = models.CharField(max_length=100, null=True)
    objects = TaskManager()

    class Meta:
        verbose_name = 'Task'


    def get_absolute_url(self):
        return reverse('task', args=[str(self.id)])

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    text = models.CharField(max_length=1000)
    date_created = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return self.task.get_absolute_url()

    def __str__(self):
        return self.text


class Thanks(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

    def like(self):
        task = Task.objects.get(id=self.task.id)
        task.rating += 1
        task.save()


def file_url(self, filename):
    return 'tmp/%s%s' % (str(date.today()), filename)
