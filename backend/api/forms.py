from django import forms
#from .models import Document

"""class DocumentForm(forms.ModelForm):
    
    class Meta:
        model = Document
        #fields = ('document', )
        fields = ('description', 'document',)"""

class DocumentForm(forms.Form):
    document = forms.FileField()
    description = forms.CharField(max_length=255)
