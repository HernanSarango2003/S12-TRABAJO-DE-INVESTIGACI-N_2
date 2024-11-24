from django import forms
from aplication.attention.models import Pago

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ['paciente', 'costo_atencion', 'metodo_pago']
        labels = {
            'paciente': 'Paciente',
            'costo_atencion': 'Costo Atención',
            'metodo_pago': 'Método de Pago',
        }
        widgets = {
            'paciente': forms.Select(attrs={'class': 'form-control'}),
            'costo_atencion': forms.Select(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
}