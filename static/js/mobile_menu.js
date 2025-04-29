document.addEventListener('DOMContentLoaded', function() {
    const menuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    let overlay = document.querySelector('.mobile-menu-overlay');
    
    // إنشاء عنصر الأوفرلاي إذا لم يكن موجوداً
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'mobile-menu-overlay hidden';
        document.body.appendChild(overlay);
    }
    
    // التأكد من أن المنيو مخفي عند بدء التحميل
    if (mobileMenu) {
        mobileMenu.classList.add('hidden');
    }
    
    // التأكد من حالة الزر الأولية
    if (menuButton) {
        menuButton.setAttribute('aria-expanded', 'false');
    }
    
    // إضافة مستمع للزر بطريقة آمنة
    if (menuButton) {
        // إزالة أي مستمعات حدث قديمة لتجنب التكرار
        menuButton.removeEventListener('click', toggleMobileMenu);
        // إضافة مستمع جديد
        menuButton.addEventListener('click', function(event) {
            event.stopPropagation(); // منع انتشار الحدث
            toggleMobileMenu();
        });
    }
    
    // وظيفة فتح وإغلاق القائمة
    function toggleMobileMenu() {
        if (!mobileMenu || !menuButton) return;
        
        const isMenuHidden = mobileMenu.classList.contains('hidden');
        
        // فتح القائمة إذا كانت مخفية
        if (isMenuHidden) {
            mobileMenu.classList.remove('hidden');
            overlay.classList.remove('hidden');
            document.body.style.overflow = 'hidden'; // منع التمرير
            mobileMenu.setAttribute('aria-expanded', 'true');
            menuButton.setAttribute('aria-expanded', 'true');
            document.body.classList.remove('menu-closed');
            
            // إضافة مستمع حدث للنقر على الأوفرلاي
            overlay.addEventListener('click', closeMenu);
        } 
        // إغلاق القائمة إذا كانت مفتوحة
        else {
            closeMenu();
        }
    }
    
    // وظيفة إغلاق القائمة
    function closeMenu() {
        if (!mobileMenu || !menuButton) return;
        
        mobileMenu.classList.add('hidden');
        if (overlay) {
            overlay.classList.add('hidden');
            overlay.removeEventListener('click', closeMenu);
        }
        document.body.style.overflow = ''; // إعادة التمرير
        mobileMenu.setAttribute('aria-expanded', 'false');
        menuButton.setAttribute('aria-expanded', 'false');
        document.body.classList.add('menu-closed');
    }
    
    // إغلاق القائمة عند النقر خارجها
    document.addEventListener('click', function(event) {
        if (mobileMenu && menuButton && 
            !mobileMenu.classList.contains('hidden') && 
            !mobileMenu.contains(event.target) && 
            !menuButton.contains(event.target)) {
            closeMenu();
        }
    });
    
    // إغلاق القائمة عند تغيير حجم النافذة إلى سطح المكتب
    window.addEventListener('resize', function() {
        if (window.innerWidth >= 768) { // الحجم الذي يتحول فيه التصميم إلى سطح المكتب
            closeMenu();
        }
    });
    
    // إضافة مستمعات للروابط في القائمة المتنقلة
    const mobileMenuLinks = document.querySelectorAll('#mobile-menu a');
    mobileMenuLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            closeMenu();
        });
    });
    
    // إضافة فئة menu-closed للجسم عند بدء التحميل
    document.body.classList.add('menu-closed');
}); 