from django import forms

from .models import TransactionModel


class TransactionForm(forms.ModelForm):
    class Meta:
        model = TransactionModel
        fields = ["amount", "transaction_type"]

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop("account")
        super().__init__(*args, **kwargs)
        self.fields["transaction_type"].disabled = True
        self.fields["transaction_type"].widget = forms.HiddenInput()

    def save(self, commit=True):
        self.instance.account = self.account
        self.instance.balance_after_transaction = self.account.balance
        return super().save()


class DepositForm(TransactionForm):
    def clean_amount(self):
        min_deposit_amount = 100
        amount = self.cleaned_data.get("amount")
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        elif amount < min_deposit_amount:
            raise forms.ValidationError(
                "Amount must be greater than {min_deposit_amount}."
            )
        return amount


class WithdrawForm(TransactionForm):
    def clean_amount(self):
        account = self.account
        min_withdrawal_amount = 100
        max_withdrawal_amount = 50000
        balance = account.balance
        amount = self.cleaned_data.get("amount")
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        if amount < min_withdrawal_amount:
            raise forms.ValidationError(
                f"Amount must be greater than {min_withdrawal_amount}."
            )
        if amount > max_withdrawal_amount:
            raise forms.ValidationError(
                f"Amount must be less than or equal to {balance-min_withdrawal_amount}."
            )
        if amount >= balance:
            raise forms.ValidationError("Insufficient balance to withdraw this amount.")
        return amount


class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        return amount
