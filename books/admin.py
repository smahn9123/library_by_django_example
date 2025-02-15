from django.contrib import admin

# Register your models here.
from .models import Book, Loan, Reservation

admin.site.register(Book)
admin.site.register(Loan)
admin.site.register(Reservation)