# forms.py 
from django import forms 
from .models import ImageClass
  
class ImageClassForm(forms.ModelForm): 
  
    class Meta: 
        model = ImageClass 
        fields = ['Image'] 