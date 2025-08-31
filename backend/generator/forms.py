# backend/generator/forms.py
from django import forms

ALLOWED_NICHES = {"general", "freelance", "consulting", "events", "coaching", "design"}
TONES = {"professional", "friendly", "urgent", "casual"}
LANGS = {"en", "pt"}
PAYMENT_METHODS = {"none", "mbway", "iban", "stripe"}

class GenerateForm(forms.Form):
    prompt = forms.CharField(min_length=3, max_length=2000)
    niche = forms.CharField(initial="general")
    tone = forms.CharField(initial="professional")
    language = forms.CharField(initial="en")
    payment_method = forms.CharField(initial="none")
    payment_value = forms.CharField(required=False)
    add_to_calendar = forms.BooleanField(required=False)
    audience = forms.CharField(required=False)
    brand_voice = forms.CharField(required=False)
    include_signature = forms.BooleanField(required=False)

    def clean_niche(self):
        n = (self.cleaned_data["niche"] or "").lower()
        if n not in ALLOWED_NICHES:
            raise forms.ValidationError("Invalid niche.")
        return n

    def clean_tone(self):
        t = (self.cleaned_data["tone"] or "").lower()
        return t if t in TONES else "professional"

    def clean_language(self):
        l = (self.cleaned_data["language"] or "").lower()
        return l if l in LANGS else "en"

    def clean(self):
        data = super().clean()
        pm = (data.get("payment_method") or "").lower()
        pv = (data.get("payment_value") or "").strip()
        if pm not in PAYMENT_METHODS:
            self.add_error("payment_method", "Invalid payment method.")
        if pm in {"mbway", "iban", "stripe"} and not pv:
            self.add_error("payment_value", "Please provide the payment value for the selected method.")
        data["payment_method"] = pm
        data["payment_value"] = pv
        return data

    def constraints(self) -> dict:
        return {
            "niche": self.cleaned_data["niche"],
            "tone": self.cleaned_data["tone"],
            "payment": {
                "method": self.cleaned_data["payment_method"],
                "value": self.cleaned_data["payment_value"],
            },
            "calendar_hint": "Only extract date/time if explicitly and unambiguously stated.",
            "enable_calendar": bool(self.cleaned_data["add_to_calendar"]),
        }
