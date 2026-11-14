from django.db import models
from django.conf import settings
from account.models import User
from decimal import Decimal
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Folder(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='folders')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.parent:
            if self.parent.user_id != self.user_id:
                raise ValidationError("You cannot create a subfolder inside another user's folder.")

    def __str__(self):
        return self.name


class Memory(models.Model):
    class Visibility(models.TextChoices):
        PUBLIC = 'public', 'Public'
        PRIVATE = 'private', 'Private'

    title = models.CharField(max_length=100)
    story = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memories')
    folder = models.ForeignKey(Folder, on_delete=models.SET_NULL, null=True, blank=True, related_name='memories')
    location = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    category = models.ManyToManyField(Category, null=True, blank=True, related_name='posts')
    visibility = models.CharField( max_length=10,choices=Visibility.choices,default=Visibility.PRIVATE,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                                   validators=[MinValueValidator(Decimal('-90')), MaxValueValidator(Decimal('90'))],
                                   )
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True,
                                    validators=[MinValueValidator(Decimal('-180')), MaxValueValidator(Decimal('180'))],
                                    )

    @property
    def has_location(self):
        return self.latitude is not None and self.longitude is not None

    @property
    def geo_uri(self):
        return f"geo:{self.latitude},{self.longitude}?q={self.latitude},{self.longitude}"

    def __str__(self):
        return self.title


class MemoryMedia(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = 'image', 'Image'
        VIDEO = 'video', 'Video'

    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='memories/media/')
    media_type = models.CharField(max_length=10, choices=MediaType.choices)
    caption = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_cover = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.memory.title} - {self.media_type}'


class Comment(models.Model):
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    context = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name='replies')


class Question(models.Model):
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='questions')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='questions')
    context = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.context[:50]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='answers')
    context = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.author_id != self.question.memory.author_id:
            raise ValidationError("Only the memory's author can answer questions.")


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    memory = models.ForeignKey(Memory, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['memory', 'user'], name='unique_like_per_memory')
        ]
