from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .constants import ACCOUNT_TYPE, GENDER_TYPE
from .models import UserAddress, UserBankAccount


class UserRegistrationForm(UserCreationForm):
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=50)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
            "account_type",
            "date_of_birth",
            "gender",
            "street_address",
            "city",
            "postal_code",
            "country",
        ]

    def save(self, commit=True):
        new_user = super().save(commit=False)
        if commit == True:
            new_user.save()

            UserBankAccount.objects.create(
                user=new_user,
                account_type=self.cleaned_data.get("account_type"),
                account_number=10000 + new_user.id,
                date_of_birth=self.cleaned_data.get("date_of_birth"),
                gender=self.cleaned_data.get("gender"),
                initial_amount=0,
            )

            UserAddress.objects.create(
                user=new_user,
                postal_code=self.cleaned_data.get("postal_code"),
                city=self.cleaned_data.get("city"),
                street_address=self.cleaned_data.get("street_address"),
                country=self.cleaned_data.get("country"),
            )

        return new_user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # print(self)

        for field in self.fields:
            # print(field)
            self.fields[field].widget.attrs.update(
                {
                    "class": "appearance-none block w-full bg-gray-200 "
                    "text-gray-700 border border-gray-200 rounded "
                    "py-3 px-4 leading-tight focus:outline-none "
                    "focus:bg-white focus:border-gray-500"
                }
            )


class UserUpdateForm(forms.ModelForm):
    account_type = forms.ChoiceField(choices=ACCOUNT_TYPE)
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    gender = forms.ChoiceField(choices=GENDER_TYPE)
    street_address = forms.CharField(max_length=100)
    city = forms.CharField(max_length=50)
    postal_code = forms.IntegerField()
    country = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "account_type",
            "date_of_birth",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields:

            self.fields[field].widget.attrs.update(
                {
                    "class": "appearance-none block w-full bg-gray-200 "
                    "text-gray-700 border border-gray-200 rounded "
                    "py-3 px-4 leading-tight focus:outline-none "
                    "focus:bg-white focus:border-gray-500"
                }
            )
        if self.instance:
            try:
                user_account = self.instance.account
                user_address = self.instance.address
            except UserBankAccount.DoesNotExist:
                user_account = None
                user_address = None
            if user_account:
                self.fields["account_type"].initial = user_account.account_type
                self.fields["date_of_birth"].initial = user_account.date_of_birth
                self.fields["gender"].initial = user_account.gender
                self.fields["city"].initial = user_address.city
                self.fields["street_address"].initial = user_address.street_address
                self.fields["postal_code"].initial = user_address.postal_code
                self.fields["country"].initial = user_address.country

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            user_account, created = UserBankAccount.objects.get_or_create(user=user)
            user_address, created = UserAddress.objects.get_or_create(user=user)

            user_account.account_type = self.cleaned_data.get("account_type")
            user_account.date_of_birth = self.cleaned_data.get("date_of_birth")
            user_account.gender = self.cleaned_data.get("gender")
            user_account.save()

            user_address.city = self.cleaned_data.get("city")
            user_address.country = self.cleaned_data.get("country")
            user_address.postal_code = self.cleaned_data.get("postal_code")
            user_address.street_address = self.cleaned_data.get("street_address")
            user_address.save()

        return user
