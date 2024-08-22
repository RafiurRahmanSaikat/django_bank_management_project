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


class TransferMoneyForm(TransactionForm):
    account_number = forms.IntegerField()
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero")
        return amount


class WithdrawForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        account = self.account
        balance = account.balance

        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        if amount > balance:
            raise forms.ValidationError("Insufficient balance to withdraw this amount.")

        return amount


class LoanRequestForm(TransactionForm):
    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        return amount
