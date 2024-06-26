from django.contrib import admin

from sde import models

admin.site.register(models.Hash)
admin.site.register(models.Category)
admin.site.register(models.Group)
admin.site.register(models.MarketGroup)
admin.site.register(models.Type)
admin.site.register(models.MetaGroup)
admin.site.register(models.MetaType)
