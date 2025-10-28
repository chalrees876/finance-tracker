# tracker/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Category, CategoryGroup, Transaction, Account, Payee

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ("group", "name")

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop("owner", None)
        super().__init__(*args, **kwargs)
        if owner:
            self.fields["group"].queryset = CategoryGroup.objects.filter(owner=owner).order_by("sort", "name")

class CategoryGroupForm(forms.ModelForm):
    class Meta:
        model = CategoryGroup
        fields = ("name",)


# tracker/forms.py
class TransactionForm(forms.ModelForm):
    payee_name = forms.CharField(
        required=False,
        help_text="Choose from list or type a new payee",
        widget=forms.TextInput(attrs={
            'list': 'payee-suggestions',
            'autocomplete': 'off'
        })
    )
    account_name = forms.CharField(
        required=False,
        help_text="Choose from list or type a new account",
        widget=forms.TextInput(attrs={
            'list': 'account-suggestions',
            'autocomplete': 'off'
        })
    )

    class Meta:
        model = Transaction
        fields = ("account", "account_name", "payee", "payee_name", "category", "memo", "amount", "date", "cleared")

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop("owner", None)
        super().__init__(*args, **kwargs)
        if owner:
            self.fields["account"].queryset = Account.objects.filter(owner=owner)
            self.fields["payee"].queryset = Payee.objects.filter(owner=owner).order_by("name")
            self.fields["category"].queryset = Category.objects.filter(owner=owner, hidden=False).order_by("name")

            # Make account and payee fields not required since we have the name fields
            self.fields["account"].required = False
            self.fields["payee"].required = False

    def clean(self):
        data = super().clean()

        # Validate account
        if not data.get("account") and not data.get("account_name"):
            self.add_error("account_name", "Choose an account or enter a new one.")

        # Validate payee
        if not data.get("payee") and not data.get("payee_name"):
            self.add_error("payee_name", "Choose a payee or enter a new one.")

        return data