from django.core.mail import EmailMessage
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, DetailView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_GET
# Asegúrate de que WeasyPrint esté importado correctamente
from aplication.attention.models import Pago, CostosAtencion, ServiciosAdicionales
from aplication.attention.forms.pago import PagoForm
import paypalrestsdk
from django.http import HttpResponse, JsonResponse
from django.template.loader import get_template, render_to_string
from weasyprint import HTML
from django.conf import settings

# Configurar PayPal SDK
paypalrestsdk.configure({
    "mode": "sandbox",  # Cambia a "live" para producción
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})

class PagoListView(LoginRequiredMixin, ListView):
    template_name = "attention/pago/list.html"
    model = Pago
    context_object_name = 'pagos'

    pagos = Pago.objects.all()
    print(pagos)

class PagoCreateView(LoginRequiredMixin, CreateView):
    model = Pago
    template_name = 'attention/pago/form.html'
    form_class = PagoForm
    success_url = reverse_lazy('attention:pago_list')

    def get_initial(self):
        initial = super().get_initial()
        paciente_id = self.request.GET.get('paciente_id')
        if paciente_id:
            initial['paciente'] = paciente_id
        return initial

    def form_valid(self, form):
        try:
            metodo_pago = form.cleaned_data.get('metodo_pago')
            if metodo_pago == 'PayPal':
                return self.process_paypal_payment(form)
            else:
                return self.process_cash_payment(form)
        except Exception as e:
            form.add_error(None, f"Error procesando el pago: {str(e)}")
            return self.form_invalid(form)

    def process_cash_payment(self, form):
        pago = form.save(commit=False)
        pago.pagado = True
        # Asignar el paciente basado en el costo de atención
        pago.paciente = pago.costo_atencion.atencion.paciente
        pago.save()

        # Actualizar el estado del costo de atención
        costo_atencion = pago.costo_atencion
        costo_atencion.pagado = True
        costo_atencion.save()

        return redirect(self.success_url)

    def process_paypal_payment(self, form):
        costo_atencion = form.cleaned_data.get('costo_atencion')
        total = costo_atencion.total

        # Crear el pago en PayPal
        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": self.request.build_absolute_uri(
                    reverse_lazy('attention:paypal_execute')
                ) + f"?costo_atencion_id={costo_atencion.id}",
                "cancel_url": self.request.build_absolute_uri(
                    reverse_lazy('attention:pago_list')
                )
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "Costo Atención Médica",
                        "sku": f"atencion_{costo_atencion.id}",
                        "price": str(total),
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": str(total),
                    "currency": "USD"
                },
                "description": f"Atención médica para {costo_atencion.atencion.paciente.nombre_completo}"
            }]
        })

        if payment.create():
            # Guardar el costo_atencion_id en la sesión
            self.request.session['costo_atencion_id'] = costo_atencion.id
            
            # Obtener la URL de aprobación
            approval_url = next(
                (link.href for link in payment.links if link.rel == "approval_url"),
                None
            )
            if approval_url:
                return redirect(approval_url)
        
        form.add_error(None, "Error al crear el pago en PayPal")
        return self.form_invalid(form)

def paypal_execute(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    costo_atencion_id = request.GET.get('costo_atencion_id')

    if not all([payment_id, payer_id, costo_atencion_id]):
        return redirect('attention:pago_list')

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        costo_atencion = get_object_or_404(CostosAtencion, pk=costo_atencion_id)
        
        # Crear el objeto Pago
        pago = Pago.objects.create(
            paciente=costo_atencion.atencion.paciente,
            costo_atencion=costo_atencion,
            metodo_pago='PayPal',
            pagado=True
        )
        
        # Marcar el costo de atención como pagado
        costo_atencion.pagado = True
        costo_atencion.save()
        
        return redirect('attention:pago_list')
    else:
        print(payment.error)
        return redirect('attention:pago_list')

class PagoDetailView(LoginRequiredMixin, DetailView):
    model = Pago
    template_name = 'attention/pago/detail.html'
    context_object_name = 'pago'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pago = self.object
        context['total_pagado'] = pago.costo_atencion.total
        return context