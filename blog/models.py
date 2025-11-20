import re
from django.utils.safestring import mark_safe
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from slugify import slugify
from django.utils import timezone
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from django.utils.html import strip_tags
from django.utils.text import Truncator


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
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    bio = models.TextField(max_length=500, blank=True, verbose_name='О себе')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль {self.user.username}'
    
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'
    

class Story(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Черновик'
        PUBLISHED = 'PB', 'Опубликовано'
    
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(max_length=200, unique=True, blank=True, verbose_name='Слаг', allow_unicode=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories', verbose_name='Автор')
    content = MarkdownxField(verbose_name='Содержание')
    excerpt = models.TextField(max_length=300, blank=True, verbose_name='Краткое описание')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='stories', verbose_name='Категория')
    cover_image = models.ImageField(upload_to='story_covers/', blank=True, null=True, verbose_name='Обложка')
    cover_image_thumbnail = ImageSpecField(source='cover_image', processors=[ResizeToFill(800, 400)], format='JPEG', options={'quality': 75})
    status = models.CharField(max_length=2, choices=Status.choices, default=Status.DRAFT, verbose_name='Статус', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')
    published_at = models.DateTimeField(blank=True, null=True, verbose_name='Опубликовано', db_index=True)

    class Meta:
        verbose_name = 'Рассказ'
        verbose_name_plural = 'Рассказы'
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['-published_at', 'status']),
            models.Index(fields=['author', 'status']),
        ]

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if self.status == self.Status.PUBLISHED:
            if not self.published_at:
                self.published_at = timezone.now()
        else:
            if self.pk:
                old_story =Story.objects.filter(pk=self.pk).first()
                if old_story and old_story.status == self.Status.PUBLISHED:
                    self.published_at = None
        super().save(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('blog:story_detail', kwargs={"slug": self.slug})
    
    def get_cover_image_url(self):
        if self.cover_image:
            return self.cover_image.url
        return '/static/images/default-cover.jpg'
    
    def get_cover_thumbnail_url(self):
        if self.cover_image:
            return self.cover_image_thumbnail.url
        return '/static/images/default-cover.jpg'
    
    def get_markdown_content(self):
        if not self.content:
            return ''
        
        html_pattern = re.compile(r'<[^>]+>')
        is_html = bool(html_pattern.search(self.content))

        if is_html:
            return mark_safe(self.content)
        html = markdownify(self.content)
        return mark_safe(html)
        
    def get_plain_excerpt(self, words=25):
        if self.excerpt:
            text_source = self.excerpt
        else:
            text_source = self.content
        
        if not text_source:
            return ''
        
        html_pattern = re.compile(r'<[^>]+>')
        is_html = bool(html_pattern.search(text_source))

        if is_html:
            text = strip_tags(text_source)
        else:
            html_content = markdownify(text_source)
            text = strip_tags(html_content)
        
        text = ' '.join(text.split())
        return Truncator(text).words(words, truncate='...')


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