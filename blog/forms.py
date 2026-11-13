from django import forms
from django.core.exceptions import ValidationError

from blog.models import Memory, Folder


class MemoryForm(forms.ModelForm):

    class Meta:
        model = Memory
        fields = [
            'title', 'category', 'story', 'folder',
            'location', 'city', 'country',
            'visibility', 'latitude', 'longitude',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'input100',
                'placeholder': 'Post title',
            }),
            'category': forms.SelectMultiple(attrs={'class': 'input100'}),
            'story': forms.Textarea(attrs={
                'class': 'input100',
                'placeholder': 'Write your memory...',
                'rows': 6,
            }),
            'folder': forms.Select(attrs={'class': 'input100'}),
            'location': forms.TextInput(attrs={
                'class': 'input100',
                'placeholder': 'Place name, e.g. Naqsh-e Jahan Square',
            }),
            'city': forms.TextInput(attrs={'class': 'input100', 'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'class': 'input100', 'placeholder': 'Country'}),
            'visibility': forms.Select(attrs={'class': 'input100'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user is not None:
            self.fields['folder'].queryset = Folder.objects.filter(user=user)
            self.fields['folder'].empty_label = 'No folder'

            if not self.instance.pk:
                self.initial['visibility'] = user.default_visibility

    def clean(self):
        cleaned = super().clean()
        lat = cleaned.get('latitude')
        lng = cleaned.get('longitude')

        if (lat is None) != (lng is None):
            raise ValidationError("Pick a point on the map: both latitude and longitude are required.")

        return cleaned