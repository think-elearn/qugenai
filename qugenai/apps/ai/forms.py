from django import forms


class QGenForm(forms.Form):
    subject = forms.CharField(label="Subject", max_length=64)
