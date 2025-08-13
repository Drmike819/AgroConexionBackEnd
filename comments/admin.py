from django.contrib import admin
from .models import Comments, CommentsImage

# Register your models here.

@admin.register(Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ("id", "comment")
    
@admin.register(CommentsImage)
class CommentsImageAdmin(admin.ModelAdmin):
    list_display = ("id","comment", "image")