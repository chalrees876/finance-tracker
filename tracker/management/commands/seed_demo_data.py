from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date

from tracker.models import (
    Account,
    CategoryGroup,
    Category,
    BudgetMonth,
    BudgetAllocation,
    Payee,
    Transaction,
)

class Command(BaseCommand):
    help = "Seeds demo user, accounts, categories, and example transactions."

    def handle(self, *args, **options):
        username = "demo"
        password = "demo1234"
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Created demo user '{username}' (pw: {password})"))
        else:
            self.stdout.write("ℹ️ Demo user already exists")

        # --- Accounts ---
        checking, _ = Account.objects.get_or_create(
            owner=user,
            name="Checking Account",
            defaults={"on_budget": True, "balance": Decimal("2500.00")},
        )
        savings, _ = Account.objects.get_or_create(
            owner=user,
            name="Savings",
            defaults={"on_budget": True, "balance": Decimal("5000.00")},
        )
        credit_card, _ = Account.objects.get_or_create(
            owner=user,
            name="Credit Card",
            defaults={"on_budget": True, "balance": Decimal("-300.00")},
        )

        # --- Category Groups + Categories ---
        housing_group, _ = CategoryGroup.objects.get_or_create(owner=user, name="Housing")
        fun_group, _ = CategoryGroup.objects.get_or_create(owner=user, name="Fun Money")
        savings_group, _ = CategoryGroup.objects.get_or_create(owner=user, name="Savings Goals")

        rent, _ = Category.objects.get_or_create(owner=user, group=housing_group, name="Rent")
        utilities, _ = Category.objects.get_or_create(owner=user, group=housing_group, name="Utilities")
        dining, _ = Category.objects.get_or_create(owner=user, group=fun_group, name="Dining Out")
        entertainment, _ = Category.objects.get_or_create(owner=user, group=fun_group, name="Entertainment")
        emergency_fund, _ = Category.objects.get_or_create(owner=user, group=savings_group, name="Emergency Fund")

        # --- Budget Month + Allocations ---
        today = date.today().replace(day=1)
        bm, _ = BudgetMonth.objects.get_or_create(owner=user, month=today)

        BudgetAllocation.objects.update_or_create(
            owner=user, month=bm, category=rent, defaults={"budgeted": Decimal("1500.00")}
        )
        BudgetAllocation.objects.update_or_create(
            owner=user, month=bm, category=utilities, defaults={"budgeted": Decimal("200.00")}
        )
        BudgetAllocation.objects.update_or_create(
            owner=user, month=bm, category=dining, defaults={"budgeted": Decimal("300.00")}
        )
        BudgetAllocation.objects.update_or_create(
            owner=user, month=bm, category=entertainment, defaults={"budgeted": Decimal("150.00")}
        )
        BudgetAllocation.objects.update_or_create(
            owner=user, month=bm, category=emergency_fund, defaults={"budgeted": Decimal("250.00")}
        )

        # --- Payees + Transactions ---
        payees = {
            "Landlord": Payee.objects.get_or_create(owner=user, name="Landlord")[0],
            "Utility Co.": Payee.objects.get_or_create(owner=user, name="Utility Co.")[0],
            "Chipotle": Payee.objects.get_or_create(owner=user, name="Chipotle")[0],
            "Netflix": Payee.objects.get_or_create(owner=user, name="Netflix")[0],
            "Employer": Payee.objects.get_or_create(owner=user, name="Employer")[0],
        }

        Transaction.objects.get_or_create(
            owner=user,
            account=checking,
            payee=payees["Employer"],
            category=None,
            amount=Decimal("3500.00"),
            memo="Monthly paycheck",
            date=today,
        )
        Transaction.objects.get_or_create(
            owner=user,
            account=checking,
            payee=payees["Landlord"],
            category=rent,
            amount=Decimal("-1500.00"),
            memo="Rent payment",
            date=today,
        )
        Transaction.objects.get_or_create(
            owner=user,
            account=checking,
            payee=payees["Utility Co."],
            category=utilities,
            amount=Decimal("-180.00"),
            memo="Electric + water",
            date=today,
        )
        Transaction.objects.get_or_create(
            owner=user,
            account=checking,
            payee=payees["Chipotle"],
            category=dining,
            amount=Decimal("-15.25"),
            memo="Burrito bowl",
            date=today,
        )
        Transaction.objects.get_or_create(
            owner=user,
            account=credit_card,
            payee=payees["Netflix"],
            category=entertainment,
            amount=Decimal("-16.99"),
            memo="Monthly subscription",
            date=today,
        )

        self.stdout.write(self.style.SUCCESS("🎉 Demo data created successfully!"))
        self.stdout.write("Login with username: demo / password: demo1234")
        self.stdout.write("Then visit: http://127.0.0.1:8000/dashboard/")
