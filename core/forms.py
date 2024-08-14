from django import forms

from .models import Process,Task


class ProcessForm(forms.ModelForm):
    class Meta:
        model = Process
        fields = ('name','description','bpmn')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bpmn'].widget = forms.HiddenInput()

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('name','description','process',)
