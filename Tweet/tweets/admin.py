from django.contrib import admin
from .models import Tweet,Profile,Comment,Reaction
# Register your models here.
admin.site.register(Tweet)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Reaction)

