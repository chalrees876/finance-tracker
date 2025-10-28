from django.contrib import admin
from .models import Account, Category, CategoryGroup, BudgetMonth, BudgetAllocation, Payee, Transaction
admin.site.register([Category, Account, CategoryGroup, BudgetMonth, BudgetAllocation, Payee, Transaction])