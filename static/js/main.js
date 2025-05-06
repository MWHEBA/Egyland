/**
 * Main JavaScript file for Egyland website
 */

document.addEventListener('DOMContentLoaded', function () {
    // إظهار القائمة الرئيسية قبل أي شيء
    const mainNav = document.querySelector('.main-nav');
    if (mainNav) {
        mainNav.style.display = 'flex';
        mainNav.style.visibility = 'visible';
        mainNav.style.opacity = '1';
    }

    // Handle navbar scroll behavior
    initNavbarScrollBehavior();

    // Handle form validation
    initFormValidation();

    // Initialize page transitions
    initPageTransitions();

    // شريط التنقل اللاصق
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 50) {
                navbar.classList.add('sticky');
            } else {
                navbar.classList.remove('sticky');
            }
        });
    }

    // سلايدر الصفحة الرئيسية
    const heroSlider = document.querySelector('.hero-slider');
    if (heroSlider) {
        initSlider(heroSlider);
    }

    // تحقق من النموذج
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', validateForm);
    });
});

// معالجة حدث تحميل الصفحة 
window.addEventListener('load', function() {
    // تأكد من إزالة أي تأثيرات انتقالية متبقية
    document.body.classList.remove('page-exit');
    document.body.style.opacity = '1';
});

/**
 * تهيئة سلوك شريط التنقل عند التمرير
 */
function initNavbarScrollBehavior() {
    const header = document.getElementById('main-header');

    if (header) {
        const mainNav = header.querySelector('.main-nav');
        const headerLinks = header.querySelectorAll('nav a:not(.bg-primary)');
        const mobileMenuIcon = header.querySelector('#mobile-menu-button div');

        // إعادة ظهور القائمة الرئيسية
        if (mainNav) {
            mainNav.style.display = 'flex';
            mainNav.style.visibility = 'visible';
        }

        if (window.location.pathname === '/' || window.location.pathname === '') {
            window.addEventListener('scroll', function () {
                if (window.scrollY > 50) {
                    header.classList.remove('bg-transparent');
                    header.classList.add('bg-white', 'shadow-md');

                    headerLinks.forEach(link => {
                        link.classList.remove('text-white');
                        link.classList.add('text-gray-800');
                    });

                    if (mobileMenuIcon) {
                        // تغيير لون خطوط الأيقونة البرجر إلى الأسود
                        const bars = mobileMenuIcon.querySelectorAll('span');
                        bars.forEach(bar => {
                            bar.classList.remove('bg-white');
                            bar.classList.add('bg-black');
                        });
                    }
                } else {
                    header.classList.add('bg-transparent');
                    header.classList.remove('bg-white', 'shadow-md');

                    headerLinks.forEach(link => {
                        link.classList.add('text-white');
                        link.classList.remove('text-gray-800');
                    });

                    if (mobileMenuIcon) {
                        // تغيير لون خطوط الأيقونة البرجر إلى الأبيض
                        const bars = mobileMenuIcon.querySelectorAll('span');
                        bars.forEach(bar => {
                            bar.classList.add('bg-white');
                            bar.classList.remove('bg-black');
                        });
                    }
                }
            });

            // تشغيل الحدث مباشرة للتحقق من الموضع الحالي
            window.dispatchEvent(new Event('scroll'));
        }
    }
}

/**
 * تهيئة التحقق من صحة النموذج
 */
function initFormValidation() {
    const forms = document.querySelectorAll('form');

    forms.forEach(form => {
        const requiredInputs = form.querySelectorAll('input[required], textarea[required], select[required]');

        form.addEventListener('submit', function (event) {
            let isValid = true;

            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;

                    // إضافة تنسيق خطأ
                    input.classList.add('border-red-500');

                    // إضافة رسالة خطأ إذا لم تكن موجودة
                    const errorElement = input.parentElement.querySelector('.error-message');
                    if (!errorElement) {
                        const errorMessage = document.createElement('p');
                        errorMessage.className = 'text-red-500 text-sm mt-1 error-message';
                        errorMessage.textContent = 'This field is required';
                        input.parentElement.appendChild(errorMessage);
                    }
                } else {
                    // إزالة تنسيق الخطأ
                    input.classList.remove('border-red-500');

                    // إزالة رسالة الخطأ
                    const errorElement = input.parentElement.querySelector('.error-message');
                    if (errorElement) {
                        errorElement.remove();
                    }
                }

                // إضافة مستمع حدث للإدخال لإزالة التنسيق عند اللمس
                input.addEventListener('input', function () {
                    if (input.value.trim()) {
                        input.classList.remove('border-red-500');

                        const errorElement = input.parentElement.querySelector('.error-message');
                        if (errorElement) {
                            errorElement.remove();
                        }
                    }
                });
            });

            if (!isValid) {
                event.preventDefault();
            }
        });
    });
}

/**
 * تهيئة انتقالات الصفحة
 */
function initPageTransitions() {
    // تعديل زر الرجوع والتأكد من عمله بشكل صحيح
    // إزالة كل معالجات الأحداث السابقة التي قد تؤثر على زر الرجوع
    
    const links = document.querySelectorAll('a:not([target="_blank"]):not([href^="#"]):not([href^="mailto:"]):not([href^="tel:"])');

    links.forEach(link => {
        link.addEventListener('click', function (event) {
            const href = this.getAttribute('href');

            // التحقق من أن الرابط يؤدي إلى صفحة داخلية
            if (href && href.indexOf('http') !== 0) {
                event.preventDefault();
                
                // إضافة تأثير خروج بسيط
                document.body.classList.add('page-exit');

                // الانتقال بعد فترة قصيرة للسماح بإكمال التأثير
                setTimeout(function () {
                    window.location.href = href;
                }, 300);
            }
        });
    });
}

// وظيفة تهيئة السلايدر
function initSlider(sliderElement) {
    const slides = sliderElement.querySelectorAll('.slide');
    const totalSlides = slides.length;
    let currentSlide = 0;

    // إخفاء جميع الشرائح ما عدا الأولى
    slides.forEach((slide, index) => {
        if (index !== 0) {
            slide.style.display = 'none';
        }
    });

    // تغيير الشرائح كل 5 ثوانٍ
    setInterval(() => {
        slides[currentSlide].style.display = 'none';
        currentSlide = (currentSlide + 1) % totalSlides;
        slides[currentSlide].style.display = 'block';
        slides[currentSlide].classList.add('fade-in');

        // إزالة تأثير الظهور بعد اكتماله
        setTimeout(() => {
            slides[currentSlide].classList.remove('fade-in');
        }, 1000);
    }, 5000);
}

// التحقق من النموذج
function validateForm(e) {
    const form = e.target;
    const formValid = form.checkValidity();

    if (!formValid) {
        e.preventDefault();

        // إظهار رسائل الخطأ
        const invalidInputs = form.querySelectorAll(':invalid');
        invalidInputs.forEach(input => {
            const errorMessage = input.dataset.errorMessage || 'This field is required';

            // إنشاء عنصر رسالة الخطأ إذا لم يكن موجودًا
            let errorElement = input.nextElementSibling;
            if (!errorElement || !errorElement.classList.contains('error-message')) {
                errorElement = document.createElement('div');
                errorElement.className = 'error-message text-red-500 text-sm mt-1';
                input.parentNode.insertBefore(errorElement, input.nextSibling);
            }

            errorElement.textContent = errorMessage;
        });
    }
}

// تنسيق جدول الموسمية
function setupSeasonalityChart() {
    const charts = document.querySelectorAll('.seasonality-chart');
    charts.forEach(chart => {
        const cells = chart.querySelectorAll('td[data-available]');
        cells.forEach(cell => {
            const available = cell.dataset.available;

            if (available === 'peak') {
                cell.classList.add('month-peak');
            } else if (available === 'yes') {
                cell.classList.add('month-available');
            }
        });
    });
} 