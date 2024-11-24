from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from aplication.attention.models import CostosAtencion, CostoAtencionDetalle, Certificado

# Views para CostosAtencion
class CostosAtencionListView(LoginRequiredMixin, ListView):
    model = CostosAtencion
    template_name = 'attention/costos_atencion/list.html'
    context_object_name = 'costos'
    paginate_by = 10

    def get_queryset(self):
        return CostosAtencion.objects.filter(activo=True)

class CostosAtencionCreateView(LoginRequiredMixin, CreateView):
    model = CostosAtencion
    template_name = 'attention/costos_atencion/form.html'
    fields = ['atencion', 'total']
    success_url = reverse_lazy('attention:costos_atencion_list')

    def form_valid(self, form):
        messages.success(self.request, 'Costo de atención creado exitosamente.')
        return super().form_valid(form)

class CostosAtencionUpdateView(LoginRequiredMixin, UpdateView):
    model = CostosAtencion
    template_name = 'attention/costos_atencion/form.html'
    fields = ['atencion', 'total']
    success_url = reverse_lazy('attention:costos_atencion_list')

    def form_valid(self, form):
        messages.success(self.request, 'Costo de atención actualizado exitosamente.')
        return super().form_valid(form)

class CostosAtencionDeleteView(LoginRequiredMixin, DeleteView):
    model = CostosAtencion
    template_name = 'attention/costos_atencion/delete.html'
    success_url = reverse_lazy('attention:costos_atencion_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Costo de atención eliminado exitosamente.')
        return super().delete(request, *args, **kwargs)

class CostosAtencionDetailView(LoginRequiredMixin, DetailView):
    model = CostosAtencion
    template_name = 'attention/costos_atencion/detail.html'
    context_object_name = 'costo'

# Views para CostoAtencionDetalle
class CostoAtencionDetalleListView(LoginRequiredMixin, ListView):
    model = CostoAtencionDetalle
    template_name = 'attention/costos_detalle/list.html'
    context_object_name = 'detalles'
    paginate_by = 10

class CostoAtencionDetalleCreateView(LoginRequiredMixin, CreateView):
    model = CostoAtencionDetalle
    template_name = 'attention/costos_detalle/form.html'
    fields = ['costo_atencion', 'servicios_adicionales', 'costo_servicio']
    success_url = reverse_lazy('attention:costos_detalle_list')

    def form_valid(self, form):
        messages.success(self.request, 'Detalle de costo creado exitosamente.')
        return super().form_valid(form)

class CostoAtencionDetalleUpdateView(LoginRequiredMixin, UpdateView):
    model = CostoAtencionDetalle
    template_name = 'attention/costos_detalle/form.html'
    fields = ['costo_atencion', 'servicios_adicionales', 'costo_servicio']
    success_url = reverse_lazy('attention:costos_detalle_list')

    def form_valid(self, form):
        messages.success(self.request, 'Detalle de costo actualizado exitosamente.')
        return super().form_valid(form)

class CostoAtencionDetalleDeleteView(LoginRequiredMixin, DeleteView):
    model = CostoAtencionDetalle
    template_name = 'attention/costos_detalle/delete.html'
    success_url = reverse_lazy('attention:costos_detalle_list')