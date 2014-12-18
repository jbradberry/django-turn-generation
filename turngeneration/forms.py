from django.contrib.contenttypes.models import ContentType
from django import forms

from . import models


class PauseForm(forms.ModelForm):
    class Meta:
        model = models.Pause
        fields = ('reason',)

    def clean(self):
        cleaned_data = super(PauseForm, self).clean()

        if not self.instance.generator.allow_pauses:
            raise forms.ValidationError("Pauses are not enabled.")
        if models.Pause.objects.filter(
            generator=self.instance.generator,
            content_type=ContentType.objects.get_for_model(self.instance.agent),
            object_id=self.instance.agent.pk
        ).exists():
            raise forms.ValidationError("You have already paused.")

        return cleaned_data


class ReadyForm(forms.ModelForm):
    class Meta:
        model = models.Ready
        fields = ()

    def clean(self):
        cleaned_data = super(ReadyForm, self).clean()

        if models.Ready.objects.filter(
            generator=self.instance.generator,
            content_type=ContentType.objects.get_for_model(self.instance.agent),
            object_id=self.instance.agent.pk
        ).exists():
            raise forms.ValidationError("You are already marked as ready.")

        return cleaned_data
