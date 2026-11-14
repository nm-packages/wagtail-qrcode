from django import forms
from wagtail.admin.forms import WagtailAdminPageForm

from wagtail_qrcode.email import get_email_defaults


class QrCodeEmailFieldsForm(forms.Form):
    email_address = forms.EmailField(
        label="Recipient Email",
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "Email address"}),
        help_text="The email address will not be saved to the database and is used only once to send the EPS file.",
    )
    email_subject = forms.CharField(
        label="Subject",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Subject if email is sent"}),
    )
    email_body = forms.CharField(
        label="Body",
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Body of the email if sent"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, value in get_email_defaults().items():
            self.initial.setdefault(name, value)

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("email_address"):
            if not cleaned_data["email_subject"]:
                self.add_error(
                    "email_subject",
                    "The email subject is required if an email address is provided.",
                )
            if not cleaned_data["email_body"]:
                self.add_error(
                    "email_body",
                    "The email body is required if an email address is provided.",
                )

        return cleaned_data


class QrCodeEmailForm(QrCodeEmailFieldsForm, WagtailAdminPageForm):
    """Collect a one-time email request; the editor hooks send it after saving."""
