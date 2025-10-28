from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from decimal import Decimal

# tracker/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


@receiver(post_save, sender=User)
def create_default_categories(sender, instance, created, **kwargs):
    if created:
        # Default Category Groups
        groups_data = [
            {"name": "Bills", "sort": 0},
            {"name": "Needs", "sort": 1},
            {"name": "Wants", "sort": 2},
            {"name": "Future Planning", "sort": 3},
        ]

        for group_data in groups_data:
            group = CategoryGroup.objects.create(
                owner=instance,
                name=group_data["name"],
                sort=group_data["sort"]
            )

            # Default Categories for each group
            if group.name == "Needs":
                categories = [
                    {"name": "Rent/Mortgage", "sort": 0},
                    {"name": "Utilities", "sort": 1},
                    {"name": "Groceries", "sort": 2},
                    {"name": "Transportation", "sort": 3},
                ]
            elif group.name == "Bills":
                categories = [
                    {"name": "Insurance", "sort": 0},
                    {"name": "Healthcare", "sort": 1},
                    {"name": "Household Supplies", "sort": 2},
                ]
            elif group.name == "Wants":
                categories = [
                    {"name": "Dining Out", "sort": 0},
                    {"name": "Entertainment", "sort": 1},
                    {"name": "Personal Care", "sort": 2},
                ]
            else:  # Future Planning
                categories = [
                    {"name": "Emergency Fund", "sort": 0},
                    {"name": "Retirement", "sort": 1},
                    {"name": "Investments", "sort": 2},
                ]

            for cat_data in categories:
                Category.objects.create(
                    owner=instance,
                    group=group,
                    name=cat_data["name"],
                    sort=cat_data["sort"]
                )

class Account(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    on_budget = models.BooleanField(default=True)  # checking, savings, credit card
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class CategoryGroup(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=80)
    sort = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class Category(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(CategoryGroup, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=80)
    sort = models.PositiveIntegerField(default=0)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class BudgetMonth(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField(help_text="Use 1st of month, e.g., 2025-11-01")

    def __str__(self):
        return self.month.strftime("%B")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "month"],
                name="unique_budget_month_per_user",
            )
        ]

class BudgetAllocation(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.ForeignKey(BudgetMonth, on_delete=models.CASCADE, related_name="allocations")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    budgeted = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))



class Payee(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    payee = models.ForeignKey(Payee, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    memo = models.CharField(max_length=200, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)  # expenses negative, income positive
    date = models.DateField(default=now)
    cleared = models.BooleanField(default=False)
    reconciled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.memo