from django.urls import path

from .views import (
    DepositView,
    LoanListView,
    LoanRequestView,
    PayLoanView,
    TransactionReportView,
    WithdrawView,
)

urlpatterns = [
    path("deposit/", DepositView.as_view(), name="deposit"),
    path("report/", TransactionReportView.as_view(), name="transaction_report"),
    path("withdraw/", WithdrawView.as_view(), name="withdraw"),
    path("loan_request/", LoanRequestView.as_view(), name="loan_request"),
    path("loans/", LoanListView.as_view(), name="all_loans"),
    path("loan/<int:loan_id>", PayLoanView.as_view(), name="loan_pay"),
]
