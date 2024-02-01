from django.contrib import admin
from .models import CustomUser, Comment, Like, Feed
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Comment)
admin.site.register(Feed)
admin.site.register(Like)
