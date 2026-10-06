from django import forms

from .models import FeeInstallment


class FeeInstallmentAdminForm(forms.ModelForm):

    class Meta:
        model = FeeInstallment
        fields = '__all__'

    def clean(self):

        cleaned_data = super().clean()

        payment_plan = cleaned_data.get('payment_plan')
        expected_date = cleaned_data.get('expected_date')
        expected_month = cleaned_data.get('expected_month')

        if payment_plan == 'EXACT_DATE':

            if not expected_date:
                self.add_error(
                    'expected_date',
                    'Please enter the expected payment date.'
                )

            if expected_month:
                self.add_error(
                    'expected_month',
                    'Leave expected month blank when using Exact Date.'
                )

        elif payment_plan == 'MONTH':

            if not expected_month:
                self.add_error(
                    'expected_month',
                    'Please enter the expected payment month.'
                )

            if expected_date:
                self.add_error(
                    'expected_date',
                    'Leave expected date blank when using Month.'
                )

        return cleaned_data