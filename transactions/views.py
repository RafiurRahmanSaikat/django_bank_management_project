from datetime import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMultiAlternatives
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView

from .constants import DEPOSIT, LOAN, LOAN_PAID, TRANSACTION_TYPE, WITHDRAW
from .forms import DepositForm, LoanRequestForm, WithdrawForm
from .models import TransactionModel

# Create your views here.from django.views import generic


class TransactionCreateMixin(LoginRequiredMixin, CreateView):
    template_name = "transactions/transaction.html"
    model = TransactionModel
    title = ""
    success_url = reverse_lazy("transaction_report")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"account": self.request.user.account})
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.title
        context.update({"title": self.title})
        return context


class DepositView(TransactionCreateMixin):
    title = "Deposit"
    form_class = DepositForm

    def get_initial(self):
        initial = {"transaction_type": DEPOSIT}
        return initial

    def form_valid(self, form):
        account = self.request.user.account
        amount = form.cleaned_data["amount"]
        account.balance += amount
        account.save(update_fields=["balance"])
        messages.success(self.request, "f{amount} Tk Succesfully Deposited")
        mail_subject = "Deposit"
        message = render_to_string(
            "transactions/deposite_mail.html",
            {
                "user": self.request.user,
                "amount": amount,
                "transaction_type": "Deposit",
                "transaction_date": datetime.now(),
            },
        )
        mail_to = self.request.user.email
        # send_email = EmailMessage(mail_subject, message, to=[mail_to])
        send_email = EmailMultiAlternatives(mail_subject, "", to=[mail_to])
        send_email.attach_alternative(message, "text/html")
        send_email.send()

        return super().form_valid(form)


class WithdrawView(TransactionCreateMixin):
    title = "Withdraw"
    form_class = WithdrawForm

    def get_initial(self):
        initial = {"transaction_type": WITHDRAW}
        return initial

    def form_valid(self, form):
        account = self.request.user.account
        amount = form.cleaned_data["amount"]
        account.balance -= amount
        account.save(update_fields=["balance"])
        messages.success(self.request, "f{amount} Tk Succesfully Withdrawed")
        return super().form_valid(form)


class LoanRequestView(TransactionCreateMixin):
    title = "Request For Loan"
    form_class = LoanRequestForm

    def get_initial(self):
        initial = {"transaction_type": LOAN}
        return initial

    def form_valid(self, form):
        current_loan_count = TransactionModel.objects.filter(
            account=self.request.user.account,
            transaction_type=LOAN,
            loan_approve=True,
        ).count()
        if current_loan_count >= 3:
            return HttpResponse("You have already requested 3 loans.")

        messages.success(
            self.request, "f{amount} Tk Loan Requested to Administrator Approval"
        )
        return super().form_valid(form)


class TransactionReportView(LoginRequiredMixin, ListView):
    template_name = "transactions/transaction_report.html"
    model = TransactionModel
    balance = 0

    def get_queryset(self):
        queryset = super().get_queryset().filter(account=self.request.user.account)
        start_date_str = self.request.GET.get("start_date")
        end_date_str = self.request.GET.get("end_date")

        if start_date_str and end_date_str:

            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            # queryset = queryset.filter(transaction_date__range=(start_date, end_date))

            queryset = queryset.filter(
                timeStamp__date__gte=start_date,
                timeStamp__date__lte=end_date,
            )
            self.balance = (
                TransactionModel.objects.filter(
                    timeStamp__date__gte=start_date, timeStamp__date__lte=end_date
                ).aggregate(Sum("amount"))["amount__sum"]
                or 0
            )

        else:
            self.balance = self.request.user.account.balance

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({"account": self.request.user.account})
        return context


class PayLoanView(LoginRequiredMixin, View):

    def get(self, request, loan_id):
        loan = get_object_or_404(TransactionModel, id=loan_id)

        if loan.loan_approve:
            user_account = loan.account
            if user_account.balance > loan.amount:
                user_account.balance -= loan.amount
                loan.balance_after_transaction = user_account.balance
                user_account.save()
                loan.transaction_type = LOAN_PAID
                loan.save()
                return redirect("all_loans")
            else:
                messages.error(self.request, "Insufficient balance to pay loan.")
                return redirect("all_loans")


class LoanListView(LoginRequiredMixin, ListView):
    model = TransactionModel
    template_name = "transactions/loan_request.html"
    context_object_name = "loans"

    def get_queryset(self):
        user_account = self.request.user.account
        queryset = TransactionModel.objects.filter(
            account=user_account,
            transaction_type=LOAN,
        )
        return queryset
