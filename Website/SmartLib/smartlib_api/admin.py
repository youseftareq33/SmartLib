from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Reader)
admin.site.register(Book)
admin.site.register(UploadedBook)
