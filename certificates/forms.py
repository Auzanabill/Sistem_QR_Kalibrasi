from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, Instrument, Certificate


class LoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling."""
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Masukkan password',
        })
    )


class RegisterForm(UserCreationForm):
    """User registration form with profile fields."""
    nama_lengkap = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nama lengkap',
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email',
        })
    )
    instansi = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Instansi/Perusahaan',
        })
    )
    no_telp = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nomor telepon',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password',
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Konfirmasi password',
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            UserProfile.objects.create(
                user=user,
                nama_lengkap=self.cleaned_data['nama_lengkap'],
                instansi=self.cleaned_data.get('instansi', ''),
                no_telp=self.cleaned_data.get('no_telp', ''),
                role='scanner',
            )
        return user


class InstrumentForm(forms.ModelForm):
    """Form for creating/editing instruments."""
    class Meta:
        model = Instrument
        fields = ['nama_alat', 'merk', 'model_tipe', 'nomor_aset', 'nomor_seri', 'pemilik', 'lokasi', 'deskripsi']
        widgets = {
            'nama_alat': forms.TextInput(attrs={'class': 'form-control'}),
            'merk': forms.TextInput(attrs={'class': 'form-control'}),
            'model_tipe': forms.TextInput(attrs={'class': 'form-control'}),
            'nomor_aset': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '001/KAL'}),
            'nomor_seri': forms.TextInput(attrs={'class': 'form-control'}),
            'pemilik': forms.TextInput(attrs={'class': 'form-control'}),
            'lokasi': forms.TextInput(attrs={'class': 'form-control'}),
            'deskripsi': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class CertificateForm(forms.ModelForm):
    """Form for creating/editing certificates."""
    class Meta:
        model = Certificate
        fields = [
            'instrument', 'nomor_sertifikat', 'tanggal_kalibrasi',
            'tanggal_berlaku', 'laboratorium', 'teknisi',
            'penanggung_jawab', 'file_sertifikat', 'is_active',
        ]
        widgets = {
            'instrument': forms.Select(attrs={'class': 'form-select'}),
            'nomor_sertifikat': forms.TextInput(attrs={'class': 'form-control'}),
            'tanggal_kalibrasi': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tanggal_berlaku': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'laboratorium': forms.TextInput(attrs={'class': 'form-control'}),
            'teknisi': forms.TextInput(attrs={'class': 'form-control'}),
            'penanggung_jawab': forms.TextInput(attrs={'class': 'form-control'}),
            'file_sertifikat': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
