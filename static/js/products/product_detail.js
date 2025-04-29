// تفعيل التمرير في الصفحة
document.addEventListener("DOMContentLoaded", function () {
    // إلغاء تأثير منع التمرير
    document.documentElement.style.overflow = "auto";
    document.body.style.overflow = "auto";
    document.body.style.height = "auto";
    document.querySelector("main").style.overflow = "visible";

    // إلغاء تثبيت الهيدر والفوتر
    document.querySelector("#main-header").style.position = "relative";
    document.querySelector("footer").style.position = "relative";
    document.querySelector("footer").style.bottom = "auto";

    // تعيين أيقونة المنتج الصحيحة للشهور النشطة
    const productIcon = document.querySelector('meta[name="product-icon"]');
    if (productIcon && productIcon.content) {
        const activeMonths = document.querySelectorAll('.month-active-fresh, .month-active-iqf');
        activeMonths.forEach(month => {
            month.style.backgroundImage = `url('${productIcon.content}')`;
        });
    }

    // ترتيب عناصر العد وفقًا للقيم الرقمية (من الأصغر للأكبر)
    const countsContainers = document.querySelectorAll('.counts-container');

    countsContainers.forEach(container => {
        // الحصول على جميع عناصر العد
        const countItems = Array.from(container.querySelectorAll('.count-item'));

        // ترتيب العناصر حسب القيم الرقمية
        countItems.sort((a, b) => {
            const aValue = parseFloat(a.querySelector('.count-value').textContent.replace(/[^\d.-]/g, '')) || 0;
            const bValue = parseFloat(b.querySelector('.count-value').textContent.replace(/[^\d.-]/g, '')) || 0;
            return aValue - bValue;
        });

        // إعادة ترتيب العناصر في DOM
        countItems.forEach(item => {
            container.appendChild(item);
        });
    });

    // إضافة كلاسات للعناصر في وصف المنتج
    const productDescriptions = document.querySelectorAll('.product-description');
    
    productDescriptions.forEach(function(description) {
        // إضافة كلاس للعنوان "Among the finest varieties are:"
        const varietyTitles = description.querySelectorAll('h2');
        varietyTitles.forEach(function(title) {
            if (title.textContent.includes('Among the finest varieties')) {
                title.classList.add('product-varieties-title');
            }
        });
        
        // إضافة كلاس للفقرات التي تصف الأنواع
        const varietyDivs = description.querySelectorAll('div');
        varietyDivs.forEach(function(div) {
            if (div.querySelector('b') || div.querySelector('strong')) {
                div.classList.add('variety-description');
            }
        });
        
        // إضافة كلاس للكلمات ذات اللون الأرجواني
        const allSpans = description.querySelectorAll('span');
        allSpans.forEach(function(span) {
            if (span.textContent.includes('purple') || (span.getAttribute('style') && span.getAttribute('style').includes('purple'))) {
                span.classList.add('purple');
            }
        });
    });
}); 