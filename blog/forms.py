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


def folder_choices(folders):
    folders = list(folders)
    by_id = {f.id: f for f in folders}

    def path(folder):
        parts, seen = [folder.name], {folder.id}
        while folder.parent_id and folder.parent_id in by_id and folder.parent_id not in seen:
            folder = by_id[folder.parent_id]
            seen.add(folder.id)
            parts.append(folder.name)
        return " / ".join(reversed(parts))

    return sorted(((f.id, path(f)) for f in folders), key=lambda c: c[1].lower())


class MemoryForm(forms.ModelForm):

    FOLDER_MODES = [
        ('existing', 'Existing folder'),
        ('new', 'New folder'),
    ]

    folder_mode = forms.ChoiceField(
        choices=FOLDER_MODES,
        initial='existing',
        required=False,
        widget=forms.RadioSelect,
    )
    folder = forms.ModelChoiceField(
        queryset=Folder.objects.none(),
        required=False,
        empty_label='No folder',
    )
    new_folder_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'e.g. Isfahan'}),
    )
    new_folder_parent = forms.ModelChoiceField(
        queryset=Folder.objects.none(),
        required=False,
        empty_label='No parent (top level)',
    )

    class Meta:
        model = Memory
        fields = [
            'title', 'category', 'story', 'folder',
            'location', 'city', 'country',
            'visibility', 'latitude', 'longitude',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'title-input',
                'placeholder': 'Memory title…',
            }),
            'story': forms.Textarea(attrs={
                'class': 'story-input',
                'rows': 14,
                'placeholder': 'Start with whatever you remember most…',
            }),
            'category': forms.SelectMultiple(),
            'location': forms.TextInput(attrs={'placeholder': 'e.g. Naqsh-e Jahan Square'}),
            'city': forms.TextInput(attrs={'placeholder': 'City'}),
            'country': forms.TextInput(attrs={'placeholder': 'Country'}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        folders = Folder.objects.filter(user=user) if user is not None else Folder.objects.none()
        choices = folder_choices(folders)

        self.fields['folder'].queryset = folders
        self.fields['folder'].choices = [('', 'No folder')] + choices
        self.fields['new_folder_parent'].queryset = folders
        self.fields['new_folder_parent'].choices = [('', 'No parent (top level)')] + choices

        if user is not None and not self.instance.pk:
            self.initial['visibility'] = user.default_visibility

    def clean(self):
        cleaned = super().clean()

        lat = cleaned.get('latitude')
        lng = cleaned.get('longitude')
        if (lat is None) != (lng is None):
            raise ValidationError("Pick a point on the map: both latitude and longitude are required.")

        if cleaned.get('folder_mode') == 'new':
            name = (cleaned.get('new_folder_name') or '').strip()
            if not name:
                self.add_error('new_folder_name', 'Enter a name for the new folder.')
            cleaned['new_folder_name'] = name
            cleaned['folder'] = None

        return cleaned

    def save(self, commit=True):
        memory = super().save(commit=False)

        if self.cleaned_data.get('folder_mode') == 'new' and self.user is not None:
            parent = self.cleaned_data.get('new_folder_parent')
            name = self.cleaned_data['new_folder_name']

            memory.folder = (
                Folder.objects.filter(user=self.user, parent=parent, name=name).first()
                or Folder.objects.create(user=self.user, parent=parent, name=name)
            )

        if commit:
            memory.save()
            self.save_m2m()
        return memory