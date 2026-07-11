from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.template.defaultfilters import date as date_filter, floatformat
from .models import Transaction


@login_required(login_url="/users/login/")
def finance_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by(
        "-date", "-id"
    )

    # Get filter parameters
    search_query = request.GET.get("search", "").strip()
    type_filter = request.GET.get("type", "all")
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")
    page_number = request.GET.get("page", 1)

    # Apply filters
    if search_query:
        transactions = transactions.filter(
            Q(description__icontains=search_query) | Q(category__icontains=search_query)
        )

    if type_filter != "all":
        transactions = transactions.filter(type=type_filter)

    if start_date:
        transactions = transactions.filter(date__gte=start_date)

    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    # Pagination (10 items per page)
    paginator = Paginator(transactions, 10)
    page_obj = paginator.get_page(page_number)

    # Handle AJAX request
    if (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or request.GET.get("ajax") == "true"
    ):
        data = {
            "transactions": [
                {
                    "id": tx.id,
                    "date": date_filter(tx.date, "d M Y"),
                    "description": tx.description,
                    "category": tx.category,
                    "type": tx.type,
                    "amount_formatted": f"R$ {floatformat(tx.amount, 2)}",
                }
                for tx in page_obj
            ],
            "pagination": {
                "has_next": page_obj.has_next(),
                "has_previous": page_obj.has_previous(),
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_items": paginator.count,
                "start_index": page_obj.start_index() if paginator.count > 0 else 0,
                "end_index": page_obj.end_index() if paginator.count > 0 else 0,
            },
        }
        return JsonResponse(data)

    return render(request, "finance_list.html", {"transactions": page_obj})


@login_required(login_url="/users/login/")
def finance_add(request):
    if request.method == "POST":
        Transaction.objects.create(
            user=request.user,
            description=request.POST.get("description"),
            amount=request.POST.get("amount"),
            date=request.POST.get("date"),
            category=request.POST.get("category"),
            type=request.POST.get("type"),
        )
        return redirect("dashboard:home")

    return render(request, "finance_add.html")
