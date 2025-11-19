from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from slugify import slugify
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name='Слаг', allow_unicode=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, default='avatars/default.png', verbose_name='Аватар')
    bio = models.TextField(max_length=500, blank=True, verbose_name='О себе')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль {self.user.username}'
    

class Story(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Черновик'
        PUBLISHED = 'PB', 'Опубликовано'
    
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name='Слаг', allow_unicode=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories', verbose_name='Автор')
    content = models.TextField(verbose_name='Содержание')
    excerpt = models.TextField(max_length=300, blank=True, verbose_name='Краткое описание')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='stories', verbose_name='Категория')
    cover_image = models.ImageField(upload_to='story_covers/', blank=True, null=True, verbose_name='Обложка')
    cover_image_thumbnail = ImageSpecField(source='cover_image', processors=[ResizeToFill(800, 400)], format='JPEG', options={'quality': 75})
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    published_at = models.DateTimeField(blank=True, null=True, verbose_name='Опубликовано')

    class Meta:
        verbose_name = 'Рассказ'
        verbose_name_plural = 'Рассказы'
        ordering = ['-published_at']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:story_detail', kwargs={"slug": self.slug})
    


class Comment(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='comments', verbose_name='Рассказ')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name='Автор')
    content = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-created_at']

    def __str__(self):
        return f'Комментарий от {self.author.username} к рассказу "{self.story.title}"'


class Like(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='likes', verbose_name='Рассказ')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_stories', verbose_name='Пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        unique_together = ('story', 'user')

    def __str__(self):
        return f'{self.user.username} лайкнул "{self.story.title}"'