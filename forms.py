from django import forms
from django.core.validators import RegexValidator, FileExtensionValidator

#create forms here
YES_NO_CHOICES = (
    (0, 'No'),
    (1, 'Yes')
)
class SqlServerLogInForm(forms.Form):
    ip_address = forms.GenericIPAddressField()
    username = forms.CharField()
    password = forms.CharField(
        widget=forms.widgets.PasswordInput()
    )

class CreateSqlTableForm(forms.Form):
    table_name = forms.CharField(
        validators=[RegexValidator(regex="^[a-zA-Z_][a-zA-Z0-9_\s]+$", message='Invalid table name. Table name must start with upper or lowwer letter (a-z) or underscore. Table name can contain only upper or lower letters (a-z), digits (0-9), underscores or spaces.')]
    )
    excel_file = forms.FileField(
        widget = forms.widgets.FileInput(),
        validators=[FileExtensionValidator(allowed_extensions=['xls', 'xlsx'])]
    )

class UpdateSqlTableForm(forms.Form):
    table_name_u = forms.CharField(
        validators=[RegexValidator(regex="^[a-zA-Z_][a-zA-Z0-9_\s]+$", message='Invalid table name. Table name must start with upper or lowwer letter (a-z) or underscore. Table name can contain only upper or lower letters (a-z), digits (0-9), underscores or spaces.')]
    )
    excel_file_u = forms.FileField(
        widget = forms.widgets.FileInput(),
        validators=[FileExtensionValidator(allowed_extensions=['xls', 'xlsx'])]
    )
    drop_table = forms.ChoiceField(
        choices=YES_NO_CHOICES,
        widget=forms.widgets.Select()
    )

    def __init__(self, *args, **kwargs):
        table_list = kwargs.pop('table_list', None)
        super().__init__(*args, *kwargs)
        self.fields['table_name_u'].widget = forms.widgets.Select(choices=tuple([(table, table) for table in table_list]))

    