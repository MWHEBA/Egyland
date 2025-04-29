from django.contrib import admin
from django.db import models
from django.forms import TextInput
from .models import (
    Product, ProductVariety, Seasonality, ProductSize,
    ProductPackaging, Office, Inquiry, ProductRequest,
    SeasonIcon, CountOption, SizeOption, PackagingOption,
    PackagingType, ProductPackagingType
)

class ProductVarietyInline(admin.TabularInline):
    model = ProductVariety
    extra = 1

class SeasonalityInline(admin.TabularInline):
    model = Seasonality
    extra = 1
    fields = ('type', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec')

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

class ProductPackagingInline(admin.TabularInline):
    model = ProductPackaging
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_type', 'is_featured', 'is_popular', 'is_special', 'created_at')
    list_filter = ('product_type', 'is_featured', 'is_popular', 'is_in_slider', 'is_special')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['button_color'].widget = TextInput(attrs={'type': 'color', 'style': 'width: 5rem;'})
        return form
    
    fieldsets = (
        ("Basic Information", {
            'fields': ('name', 'slug', 'description', 'product_type', 'is_special')
        }),
        ("Product Images", {
            'fields': ('fresh_image', 'iqf_image', 'list_image', 'icon', 'iqf_icon')
        }),
        ("Background Images", {
            'fields': ('background_left', 'background_right', 'bg_image')
        }),
        ("Packaging Images", {
            'fields': ('fresh_packaging_image', 'iqf_packaging_image')
        }),
        ("Product Features", {
            'fields': ('has_varieties', 'has_counts', 'has_size', 'has_packaging')
        }),
        ("Display Options", {
            'fields': ('is_featured', 'is_popular', 'is_in_slider', 'button_color', 'order')
        }),
        ("SEO", {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )
    inlines = [
        ProductVarietyInline, 
        SeasonalityInline,
        ProductSizeInline,
        ProductPackagingInline
    ]

@admin.register(ProductVariety)
class ProductVarietyAdmin(admin.ModelAdmin):
    list_display = ('name', 'product')
    list_filter = ('product',)
    search_fields = ('name', 'description')
    inlines = [SeasonalityInline]

@admin.register(Seasonality)
class SeasonalityAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'type', 'get_months')
    list_filter = ('type', 'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec')
    
    def get_name(self, obj):
        if obj.product:
            return obj.product.name
        return obj.variety.name
    get_name.short_description = 'Product/Variety'
    
    def get_months(self, obj):
        months = []
        if obj.jan: months.append('Jan')
        if obj.feb: months.append('Feb')
        if obj.mar: months.append('Mar')
        if obj.apr: months.append('Apr')
        if obj.may: months.append('May')
        if obj.jun: months.append('Jun')
        if obj.jul: months.append('Jul')
        if obj.aug: months.append('Aug')
        if obj.sep: months.append('Sep')
        if obj.oct: months.append('Oct')
        if obj.nov: months.append('Nov')
        if obj.dec: months.append('Dec')
        return ', '.join(months)
    get_months.short_description = 'Available Months'

@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('product', 'value', 'unit', 'type')
    list_filter = ('type', 'product')

@admin.register(ProductPackaging)
class ProductPackagingAdmin(admin.ModelAdmin):
    list_display = ('product', 'type', 'net_weight', 'weight_unit', 'cartons_per_pallet')
    list_filter = ('type', 'product')

@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ('country', 'email', 'phone')
    search_fields = ('country', 'address', 'email', 'phone')

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'company', 'email', 'type', 'status', 'created_at')
    list_filter = ('type', 'status', 'created_at')
    search_fields = ('name', 'company', 'email', 'message')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('products',)

@admin.register(CountOption)
class CountOptionAdmin(admin.ModelAdmin):
    list_display = ('value',)
    search_fields = ('value',)

@admin.register(SizeOption)
class SizeOptionAdmin(admin.ModelAdmin):
    list_display = ('value',)
    search_fields = ('value',)

@admin.register(PackagingOption)
class PackagingOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'net_weight', 'weight_unit', 'cartons_per_pallet')
    list_filter = ('type', 'weight_unit')
    search_fields = ('name',)

@admin.register(PackagingType)
class PackagingTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'key_word', 'is_fresh', 'is_iqf', 'created_at')
    list_filter = ('is_fresh', 'is_iqf')
    search_fields = ('name', 'description')
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'image', 'key_word')
        }),
        ('Availability', {
            'fields': ('is_fresh', 'is_iqf')
        }),
    )

@admin.register(ProductPackagingType)
class ProductPackagingTypeAdmin(admin.ModelAdmin):
    list_display = ('product', 'packaging_type', 'type', 'order', 'items_per_pallet', 'pallets_per_container')
    list_filter = ('type', 'show_fresh_label')
    search_fields = ('product__name', 'packaging_type__name')
    autocomplete_fields = ['product', 'packaging_type']
    fieldsets = (
        (None, {
            'fields': ('product', 'packaging_type', 'type')
        }),
        ('Details', {
            'fields': ('items_per_pallet', 'pallets_per_container')
        }),
        ('Display Options', {
            'fields': ('show_fresh_label', 'order')
        }),
    )
