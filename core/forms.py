from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User 
from .models import Item, Profile

# ----------------------------------------
# NEO-BRUTALIST WIDGET ATTRIBUTES
# ----------------------------------------
NEO_INPUT_CLASS = (
    "w-full p-4 border-4 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] "
    "focus:outline-none focus:shadow-[6px_6px_0px_0px_rgba(79,70,229,1)] "
    "focus:translate-x-[-2px] focus:translate-y-[-2px] "
    "font-black uppercase italic transition-all bg-white text-black placeholder:text-slate-400"
)

NEO_SELECT_CLASS = NEO_INPUT_CLASS

NEO_FILE_CLASS = (
    "w-full p-4 border-4 border-dashed border-black bg-slate-50 "
    "font-black uppercase cursor-pointer hover:bg-indigo-50 transition-colors "
    "file:mr-4 file:py-2 file:px-4 file:border-2 file:border-black "
    "file:text-[10px] file:font-black file:bg-black file:text-white"
)

# ----------------------------------------
# PASSWORD RESET: RESTRICTED ACCESS
# ----------------------------------------

class MySpecificResetForm(PasswordResetForm):
    """
    Ensures password recovery is directed to the verified Gmail node.
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': NEO_INPUT_CLASS, 
            'placeholder': 'SYSTEM_ADMIN_EMAIL'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Restriction logic: Only gerald exists in this terminal's override
        if email != "geraldcudia19@gmail.com":
            raise forms.ValidationError("UNAUTHORIZED ACCESS: RECOVERY RESTRICTED.")
        
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("NODE NOT FOUND: NO ACCOUNT LINKED.")
        return email

    def get_users(self, email):
        return User.objects.filter(email__iexact=email, is_active=True)

# ----------------------------------------
# SIGNUP FORM
# ----------------------------------------

class SignupForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': NEO_INPUT_CLASS, 'placeholder': 'USER_ID'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': NEO_INPUT_CLASS, 'placeholder': 'EMAIL_NODE'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': NEO_INPUT_CLASS, 'placeholder': 'SECURE_KEY'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("IDENTIFIER TAKEN. SELECT ALTERNATE ID.")
        return username

    def clean_email(self):
        """Prevents duplicate email registration in the mainframe."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("GMAIL_NODE_OCCUPIED: ALREADY IN SYSTEM.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit: user.save()
        return user

# ----------------------------------------
# PROFILE FORM (IDENTITY OVERRIDE)
# ----------------------------------------

class UserProfileForm(forms.ModelForm):
    """
    Updates both User (Gmail Node) and Profile (Bio-Data) parameters.
    Includes conflict detection for existing emails and identifiers.
    """
    email = forms.EmailField(
        required=True, 
        widget=forms.EmailInput(attrs={
            'class': NEO_INPUT_CLASS, 
            'placeholder': 'PRIMARY_GMAIL_NODE'
        })
    )
    username = forms.CharField(
        required=True, 
        widget=forms.TextInput(attrs={'class': NEO_INPUT_CLASS, 'placeholder': 'UPDATE_USER_ID'})
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': NEO_INPUT_CLASS, 'placeholder': 'PHONE_BROADCASTER'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': NEO_INPUT_CLASS, 
            'placeholder': 'IDENTITY_BRIEF (BIO)', 
            'rows': 3
        })
    )
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': NEO_FILE_CLASS})
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['phone'].initial = self.instance.profile.phone
            self.fields['bio'].initial = self.instance.profile.bio
            self.fields['image'].initial = self.instance.profile.image

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Exclude self to allow saving if the username wasn't changed
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("IDENTIFIER IN USE.")
        return username

    def clean_email(self):
        """
        Validates that the new Gmail Node is not already claimed by 
        another entity in the mainframe.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("GMAIL_NODE_CONFLICT: ALREADY ASSIGNED TO ANOTHER ID.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get('phone')
            profile.bio = self.cleaned_data.get('bio')
            if self.cleaned_data.get('image'):
                profile.image = self.cleaned_data.get('image')
            profile.save()
        return user

# ----------------------------------------
# REPORTING & ITEM FORMS
# ----------------------------------------

class ReportItemStep1Form(forms.ModelForm):
    item_type = forms.ChoiceField(
        choices=Item.TYPE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'hidden'}), 
        label="Select Broadcast Type",
        initial=Item.LOST
    )
    
    class Meta:
        model = Item
        fields = ['item_type']

class ReportItemStep2Form(forms.ModelForm):
    date_happened = forms.DateField(
        widget=forms.DateInput(attrs={'class': NEO_INPUT_CLASS, 'type': 'date'}),
        label="Event Date"
    )

    class Meta:
        model = Item
        fields = ['title', 'description', 'location', 'date_happened', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': NEO_INPUT_CLASS, 'placeholder': 'OBJECT_NAME'}),
            'description': forms.Textarea(attrs={'class': NEO_INPUT_CLASS, 'rows': 4, 'placeholder': 'DATA_LOG_DETAILS'}),
            'location': forms.TextInput(attrs={'class': NEO_INPUT_CLASS, 'placeholder': 'COORDINATES'}),
            'image': forms.ClearableFileInput(attrs={'class': NEO_FILE_CLASS}),
        }

class ItemForm(forms.ModelForm):
    date_happened = forms.DateField(widget=forms.DateInput(attrs={'class': NEO_INPUT_CLASS, 'type': 'date'}))
    
    class Meta:
        model = Item
        fields = ['title', 'description', 'item_type', 'location', 'date_happened', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': NEO_INPUT_CLASS}),
            'description': forms.Textarea(attrs={'class': NEO_INPUT_CLASS, 'rows': 4}),
            'item_type': forms.Select(attrs={'class': NEO_SELECT_CLASS}),
            'location': forms.TextInput(attrs={'class': NEO_INPUT_CLASS}),
            'image': forms.ClearableFileInput(attrs={'class': NEO_FILE_CLASS}),
        }