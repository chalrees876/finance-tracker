from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from django.contrib import messages
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import (
    Account,
    CategoryGroup,
    Category,
    BudgetMonth,
    BudgetAllocation,
    Transaction, Payee,
)

from .forms import (
    SignUpForm,
    CategoryForm,
    CategoryGroupForm,
    TransactionForm
)

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    signup_form = SignUpForm()
    login_form = AuthenticationForm()
    signup_success = False

    if request.method == "POST":
        form_type = request.POST.get('form_type')

        if form_type == 'signup':
            signup_form = SignUpForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save()
                # Log the user in after signup
                login(request, user)
                messages.success(request, f"Welcome {user.username}! Your account has been created successfully.")
                return redirect("dashboard")
            else:
                messages.error(request, "Please correct the errors below.")

        elif form_type == 'login':
            login_form = AuthenticationForm(request, data=request.POST)
            if login_form.is_valid():
                username = login_form.cleaned_data.get('username')
                password = login_form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f"Welcome back, {username}!")
                    next_url = request.GET.get('next', 'dashboard')
                    return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")

    return render(request, "tracker/home.html", {
        "signup_form": signup_form,
        "login_form": login_form,
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, "tracker/login.html", {"form": form})

def signup(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome! Your account is ready.")
            return redirect("dashboard")
    else:
        form = SignUpForm()
    return render(request, "tracker/home.html", {"form": form})


@login_required
def categories(request):
    # list groups & categories
    groups = CategoryGroup.objects.filter(owner=request.user).prefetch_related("categories").order_by("sort", "name")

    # forms for quick add
    group_form = CategoryGroupForm()
    cat_form = CategoryForm(owner=request.user)

    return render(request, "tracker/categories.html", {
        "groups": groups,
        "group_form": group_form,
        "cat_form": cat_form,
    })


@login_required
@require_POST
def category_group_create(request):
    form = CategoryGroupForm(request.POST)
    if form.is_valid():
        g = form.save(commit=False)
        g.owner = request.user
        g.save()
        messages.success(request, "Category group created.")
    return redirect("categories")


@login_required
@require_POST
def category_create(request):
    form = CategoryForm(request.POST, owner=request.user)
    if form.is_valid():
        c = form.save(commit=False)
        c.owner = request.user
        c.save()
        messages.success(request, "Category created.")
    else:
        messages.error(request, "Please fix errors in the category form.")
    return redirect("categories")


@login_required
@require_POST
def category_delete(request, category_id):
    c = get_object_or_404(Category, id=category_id, owner=request.user)
    c.delete()
    messages.info(request, "Category deleted.")
    return redirect("categories")


@login_required
def transactions(request):
    tx = Transaction.objects.filter(owner=request.user).select_related("payee", "category", "account") \
        .order_by("-date", "-id")[:200]

    if request.method == "POST":
        form = TransactionForm(request.POST, owner=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user

            # Handle account creation if needed
            account = form.cleaned_data.get("account")
            account_name = form.cleaned_data.get("account_name")
            if not account and account_name:
                account, _ = Account.objects.get_or_create(
                    owner=request.user,
                    name=account_name.strip(),
                    defaults={'on_budget': True, 'balance': 0}
                )
            obj.account = account

            # Handle payee creation if needed
            payee = form.cleaned_data.get("payee")
            payee_name = form.cleaned_data.get("payee_name")
            if not payee and payee_name:
                payee, _ = Payee.objects.get_or_create(
                    owner=request.user,
                    name=payee_name.strip()
                )
            obj.payee = payee

            obj.save()
            messages.success(request, "Transaction added successfully.")
            return redirect("transactions")
    else:
        form = TransactionForm(owner=request.user)

    # Get existing accounts and payees for datalist
    existing_accounts = Account.objects.filter(owner=request.user).values_list('name', flat=True)
    existing_payees = Payee.objects.filter(owner=request.user).values_list('name', flat=True)

    return render(request, "tracker/transactions.html", {
        "transactions": tx,
        "form": form,
        "existing_accounts": existing_accounts,
        "existing_payees": existing_payees
    })

def money(x):
    if x is None:
        return Decimal("0.00")
    return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@require_POST
def logout_view(request):
    logout(request)
    return redirect("home")


# --- helpers ---
def first_of_month(d: date) -> date:
    return d.replace(day=1)


def parse_month_param(request):
    month_str = request.GET.get("month")
    if not month_str:
        return first_of_month(date.today()), first_of_month(date.today()).strftime("%Y-%m")
    try:
        sel = datetime.strptime(month_str, "%Y-%m").date().replace(day=1)
        return sel, month_str
    except ValueError:
        sel = first_of_month(date.today())
        return sel, sel.strftime("%Y-%m")

# --- dashboard (YNAB-style) ---
@login_required
def dashboard(request):
    user = request.user
    sel_month, month_value = parse_month_param(request)
    next_month = (sel_month.replace(day=28) + (date.resolution * 4)).replace(day=1)
    prev_month = (sel_month.replace(day=1) - date.resolution).replace(day=1)

    # Ensure a BudgetMonth exists
    bm, _ = BudgetMonth.objects.get_or_create(owner=user, month=sel_month)

    # Summary cards
    on_budget_balance = Account.objects.filter(owner=user, on_budget=True) \
                            .aggregate(s=Sum("balance"))["s"] or Decimal("0.00")

    activity_this_month = Transaction.objects.filter(
        owner=user, date__gte=sel_month, date__lt=next_month
    ).aggregate(s=Sum("amount"))["s"] or Decimal("0.00")

    budgeted_this_month = BudgetAllocation.objects.filter(owner=user, month=bm) \
                              .aggregate(s=Sum("budgeted"))["s"] or Decimal("0.00")

    total_budgeted_all = BudgetAllocation.objects.filter(owner=user) \
                             .aggregate(s=Sum("budgeted"))["s"] or Decimal("0.00")
    total_income_all = Transaction.objects.filter(owner=user, amount__gt=0) \
                           .aggregate(s=Sum("amount"))["s"] or Decimal("0.00")

    tbb = (on_budget_balance + total_income_all) - total_budgeted_all

    # Build budget table rows by group
    groups_ctx = []
    month_activity_qs = Transaction.objects.filter(
        owner=user, date__gte=sel_month, date__lt=next_month
    )

    for g in CategoryGroup.objects.filter(owner=user).order_by("sort", "name"):
        rows = []
        for c in g.categories.filter(hidden=False).order_by("sort", "name"):
            # budgeted for selected month
            alloc = BudgetAllocation.objects.filter(owner=user, month=bm, category=c).first()
            budgeted = alloc.budgeted if alloc else Decimal("0.00")

            # activity for selected month (expenses negative, income positive)
            cat_act = month_activity_qs.filter(category=c).aggregate(s=Sum("amount"))["s"] or Decimal("0.00")

            # FIXED: Correct available calculation - only include transactions up to selected month
            prior_budgeted = BudgetAllocation.objects.filter(
                owner=user,
                category=c,
                month__month__lt=sel_month
            ).aggregate(s=Sum("budgeted"))["s"] or Decimal("0.00")

            prior_activity = Transaction.objects.filter(
                owner=user,
                category=c,
                date__lt=sel_month
            ).aggregate(s=Sum("amount"))["s"] or Decimal("0.00")

            available = (prior_budgeted + prior_activity) + budgeted + cat_act

            rows.append({
                "category": c,
                "budgeted": money(budgeted),
                "activity": money(cat_act),
                "available": money(available),
                "allocation_id": alloc.id if alloc else None,
            })
        groups_ctx.append({"name": g.name, "rows": rows})

    ctx = {
        "month_value": month_value,
        "sel_month": sel_month,
        "prev_month": prev_month.strftime("%Y-%m"),
        "next_month": next_month.strftime("%Y-%m"),
        "tbb": money(tbb),
        "budgeted_this_month": money(budgeted_this_month),
        "activity_this_month": money(activity_this_month),
        "on_budget_balance": money(on_budget_balance),
        "groups": groups_ctx,
    }
    return render(request, "tracker/dashboard.html", ctx)

@login_required
@require_POST
def budget_allocate(request):
    category_id = request.POST.get("category_id")
    month_str = request.POST.get("month")
    raw = (request.POST.get("budgeted") or "0").replace(",", "").strip()
    try:
        amount = Decimal(raw)
    except Exception:
        amount = Decimal("0.00")

    # Parse month and ensure BudgetMonth
    sel_month = datetime.strptime(month_str, "%Y-%m").date().replace(day=1)
    bm, _ = BudgetMonth.objects.get_or_create(owner=request.user, month=sel_month)

    c = Category.objects.get(id=category_id, owner=request.user)
    alloc, _ = BudgetAllocation.objects.get_or_create(owner=request.user, month=bm, category=c)
    alloc.budgeted = amount
    alloc.save()

    return redirect(f"/dashboard/?month={month_str}")