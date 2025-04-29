from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from apps.dashboard.mixins import StaffRequiredMixin
from .models import Branch, MainBranch
from .forms import BranchForm, MainBranchForm


class BranchListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    """
    عرض قائمة الفروع
    """
    model = Branch
    template_name = 'dashboard/branches/list.html'
    context_object_name = 'branches'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Branch.objects.all().order_by('display_order')
        
        # Filter by country name
        country_filter = self.request.GET.get('country')
        if country_filter:
            queryset = queryset.filter(country_name__icontains=country_filter)
        
        # Filter by status
        status_filter = self.request.GET.get('status')
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['main_branch'] = MainBranch.get_main_branch()
        return context


class BranchCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """
    إنشاء فرع جديد
    """
    model = Branch
    form_class = BranchForm
    template_name = 'dashboard/branches/form.html'
    success_url = reverse_lazy('dashboard:branches')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Branch'
        context['action'] = 'add'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Branch has been created successfully!')
        return super().form_valid(form)


class BranchUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """
    تحديث معلومات فرع
    """
    model = Branch
    form_class = BranchForm
    template_name = 'dashboard/branches/form.html'
    success_url = reverse_lazy('dashboard:branches')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Branch'
        context['action'] = 'edit'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Branch has been updated successfully!')
        return super().form_valid(form)


class BranchDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """
    حذف فرع
    """
    model = Branch
    template_name = 'dashboard/branches/delete.html'
    success_url = reverse_lazy('dashboard:branches')
    context_object_name = 'branch'
    
    def delete(self, request, *args, **kwargs):
        branch = self.get_object()
        messages.success(request, f'Branch "{branch.country_name}" has been deleted successfully!')
        return super().delete(request, *args, **kwargs)


class BranchDetailAPIView(LoginRequiredMixin, StaffRequiredMixin, View):
    """
    عرض API لجلب بيانات الفرع بتنسيق JSON
    """
    def get(self, request, *args, **kwargs):
        branch_id = kwargs.get('pk')
        branch = get_object_or_404(Branch, id=branch_id)
        
        data = {
            'id': branch.id,
            'country_name': branch.country_name,
            'address': branch.address,
            'phone': branch.phone,
            'email': branch.email,
            'display_order': branch.display_order,
            'is_active': branch.is_active,
            'flag_image': branch.flag_image.url if branch.flag_image else None
        }
        
        return JsonResponse(data)


class MainBranchUpdateView(LoginRequiredMixin, StaffRequiredMixin, View):
    """
    تحديث معلومات الفرع الرئيسي (مكتب مصر)
    """
    template_name = 'dashboard/branches/main_branch_form.html'
    success_url = reverse_lazy('dashboard:branches')
    
    def get(self, request, *args, **kwargs):
        # Find the main branch record or create a new one if it doesn't exist
        main_branch = MainBranch.objects.filter(is_active=True).first()
        if not main_branch:
            main_branch = MainBranch.objects.first()
            
        if not main_branch:
            # Create a new record if none exists
            main_branch = MainBranch(company_name="Egypt (Head Office)")
        
        form = MainBranchForm(instance=main_branch)
        return render(request, self.template_name, {
            'form': form,
            'main_branch': main_branch,
            'title': 'Egypt (Head Office)'
        })
    
    def post(self, request, *args, **kwargs):
        main_branch = MainBranch.objects.filter(is_active=True).first()
        if not main_branch:
            main_branch = MainBranch.objects.first()
            
        if not main_branch:
            main_branch = MainBranch(company_name="Egypt (Head Office)")
        
        form = MainBranchForm(request.POST, request.FILES, instance=main_branch)
        if form.is_valid():
            branch = form.save(commit=False)
            # دائمًا نجعل الفرع الرئيسي نشط
            branch.is_active = True
            branch.save()
            messages.success(request, 'Head office information has been updated successfully!')
            return redirect(self.success_url)
        
        return render(request, self.template_name, {
            'form': form,
            'main_branch': main_branch,
            'title': 'Egypt (Head Office)'
        })
