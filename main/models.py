from django.db import models
# from django.contrib.auth import get_user_model

import uuid

class Category(models.Model):
    '''
    Category table
    id
    name - max length 100 chars
    representation of the object - category name
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(verbose_name="Category name", max_length=100, unique=True)

    def __str__(self):
        return self.name

class Post(models.Model):
    '''
    Post table
    id
    name - max length 100 chars
    category - Category model
    image - will upload to media/post_imgs
    representation of the object - name of post

    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(verbose_name="Post name", max_length=100, blank=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="posts", blank=False)
    description = models.TextField(verbose_name="Full description", max_length=300)
    short_description = models.TextField(verbose_name="Short description", max_length=150)
    image = models.ImageField(verbose_name="Image", upload_to="post_imgs")
    created_at = models.DateField(verbose_name="Created at", auto_now_add=True)

    def __str__(self):
        return self.name