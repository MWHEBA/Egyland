from django.db import migrations
from django.utils.text import slugify
import uuid

def update_empty_slugs(apps, schema_editor):
    """
    تحديث جميع المنتجات التي ليس لها slug أو التي لها slug فارغ
    """
    Product = apps.get_model('products', 'Product')
    
    # الحصول على جميع المنتجات التي ليس لها slug
    products_without_slug = Product.objects.filter(slug__exact='')
    
    for product in products_without_slug:
        # محاولة إنشاء slug من الاسم
        base_slug = slugify(product.name)
        
        # إذا كان الاسم بالعربية أو لم ينتج عنه slug صالح
        if not base_slug:
            # استخدام معرف فريد
            base_slug = str(uuid.uuid4())[:8]
        
        # التحقق من أن الـ slug فريد
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        product.slug = slug
        product.save(update_fields=['slug'])
        
    print(f"Updated {products_without_slug.count()} products with empty slugs.")

class Migration(migrations.Migration):
    
    dependencies = [
        ('products', '0025_alter_product_button_color'),
    ]
    
    operations = [
        migrations.RunPython(update_empty_slugs, reverse_code=migrations.RunPython.noop),
    ] 