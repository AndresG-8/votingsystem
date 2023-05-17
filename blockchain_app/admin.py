from django.contrib import admin
from .models import Block, Transaction, Chain
# Register your models here.

admin.site.register(Block)
admin.site.register(Transaction)
admin.site.register(Chain)