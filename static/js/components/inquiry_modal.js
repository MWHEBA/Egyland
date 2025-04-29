/**
 * ملف JavaScript لإدارة مودال الاستفسارات
 */

// تفعيل التصريح الصارم
'use strict';

// العناصر الأساسية - نستخدم var لنمنع الخطأ عند إعادة التحميل
var inquiryModal, modalOverlay, closeButton, inquiryButtons, inquiryForm, productIdInput;
var generalInquiryOption, productSpecificOption, generalInquiryInput, productSpecificInput, productsSection, productsSelect;
var phoneInput, countrySelect, phoneError, countryCodeInput;

// كائن intlTelInput
var iti;

// قائمة المنتجات - سيتم ملؤها لاحقًا
var productsList = [];

// القائمة الثابتة للمنتجات (للاستخدام في حالة فشل API)
var hardcodedProducts = [
    { id: 1, name: 'Oranges', slug: 'oranges' },
    { id: 2, name: 'Strawberry', slug: 'strawberry' },
    { id: 3, name: 'Mango', slug: 'mango' },
    { id: 4, name: 'Pomegranate', slug: 'pomegranate' },
    { id: 5, name: 'Guava', slug: 'guava' },
    { id: 6, name: 'Lemon', slug: 'lemon' },
    { id: 7, name: 'Grapes', slug: 'grapes' },
    { id: 8, name: 'Apple', slug: 'apple' },
    { id: 9, name: 'Banana', slug: 'banana' },
    { id: 10, name: 'Pineapple', slug: 'pineapple' },
    { id: 11, name: 'Kiwi', slug: 'kiwi' }
];

// تحميل مسبق للمنتجات دون عرض المودال
function preloadProducts() {
    // محاولة استخدام API أولاً
    loadProductsFromAPI().catch(() => {
        // ثم استخدام API بديل إذا لم ينجح الأول
        loadProductsFromSecondaryAPI().catch(() => {
            // في النهاية استخدام القائمة الثابتة
            useHardcodedProducts();
        });
    });
}

// دالة لتحميل المنتجات من API
function loadProductsFromAPI() {
    // استخدام المسار الكامل للـ API
    // المسار الصحيح هو /inquiries/api/products/
    return fetch('/inquiries/api/products/')
        .then(response => {
            if (!response.ok) throw new Error(`API returned status ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (Array.isArray(data) && data.length > 0) {
                productsList = data;
                return productsList;
            } else {
                throw new Error('API returned empty or invalid data');
            }
        });
}

// دالة لتحميل المنتجات من API ثانوي
function loadProductsFromSecondaryAPI() {
    // محاولة استخدام المسار الثانوي
    return fetch('/admin/products/product/?format=json')
        .then(response => {
            if (!response.ok) throw new Error(`Secondary API returned status ${response.status}`);
            return response.json();
        })
        .then(data => {
            if (Array.isArray(data) && data.length > 0) {
                // تنسيق البيانات ليتوافق مع التنسيق المتوقع
                productsList = data.map(item => ({
                    id: item.id,
                    name: item.name || item.fields?.name,
                    slug: item.slug || item.fields?.slug
                }));
                return productsList;
            } else {
                throw new Error('Secondary API returned empty or invalid data');
            }
        });
}

// استخدام القائمة الثابتة للمنتجات
function useHardcodedProducts() {
    productsList = hardcodedProducts;
    return productsList;
}

// جلب قائمة المنتجات من الخادم أو من القائمة المخزنة
function fetchProducts() {
    // التحقق إذا كانت قائمة المنتجات محملة بالفعل
    if (productsList.length > 0) {
        populateProductsSelect(productsList);
        return;
    }
    
    // إذا لم تكن القائمة محملة، محاولة جلبها من الخادم
    loadProductsFromAPI()
        .then(products => {
            populateProductsSelect(products);
        })
        .catch(error => {
            console.error('Error fetching products:', error);
            useHardcodedProducts();
            populateProductsSelect(productsList);
        });
}

// ملء قائمة المنتجات في المودال
function populateProductsSelect(products) {
    // مسح الخيارات الحالية
    productsSelect.innerHTML = '';
    
    // إذا كان لدينا قائمة منتجات، نستخدمها
    if (products && products.length > 0) {
        // المنتج الحالي من URL الصفحة
        const currentProductSlug = getCurrentProductSlugFromURL();
        
        // إضافة كل المنتجات من قائمة API
        products.forEach(product => {
            const option = document.createElement('option');
            option.value = product.id;
            option.text = product.name; // استخدام اسم المنتج بدون إيموجي
            
            // تحديد المنتج الحالي بناءً على معرف المنتج أو slug
            let shouldSelect = false;
            
            // التحقق من المعرف أولاً
            if (productIdInput.value && parseInt(product.id) === parseInt(productIdInput.value)) {
                shouldSelect = true;
            } 
            // ثم التحقق من اسم المسار إذا كان متاحًا
            else if (currentProductSlug && product.slug && product.slug === currentProductSlug) {
                shouldSelect = true;
                // تحديث معرف المنتج
                productIdInput.value = product.id;
            }
            
            if (shouldSelect) {
                option.selected = true;
            }
            
            productsSelect.appendChild(option);
        });
    } 
    // إذا لم يكن لدينا قائمة منتجات صالحة، نستخدم الاحتياطية
    else {
        console.warn('No product list from API available, using fallback');
        addCurrentProductToSelect();
    }
    
    // التحقق من عدم وجود منتجات وإظهار رسالة للمستخدم
    if (productsSelect.options.length === 0) {
        const option = document.createElement('option');
        option.text = 'No products available';
        option.disabled = true;
        productsSelect.appendChild(option);
        console.warn('No products available to display');
    }
}

// الحصول على slug المنتج الحالي من URL
function getCurrentProductSlugFromURL() {
    // تحليل URL الحالي
    const url = window.location.pathname;
    
    // التحقق مما إذا كنا في صفحة منتج
    // الشكل الشائع: /products/{slug}/
    if (url.startsWith('/products/')) {
        // استخراج slug المنتج (الجزء الأخير من URL)
        const parts = url.split('/').filter(part => part.length > 0);
        if (parts.length >= 2 && parts[0] === 'products') {
            return parts[1];
        }
    }
    
    return null;
}

// إضافة المنتج الحالي فقط للاختيار
function addCurrentProductToSelect() {
    // مسح الاختيارات الحالية
    productsSelect.innerHTML = '';
    
    // استخراج المنتج الحالي من URL
    const currentProductSlug = getCurrentProductSlugFromURL();
    
    // استخدام القائمة الثابتة
    hardcodedProducts.forEach(product => {
        const option = document.createElement('option');
        option.value = product.id;
        option.text = product.name;
        
        // تحديد المنتج الحالي إذا كان متطابقًا بالمعرف أو الاسم
        const productNameFromPage = getProductNameFromPage();
        
        if ((productIdInput.value && product.id == productIdInput.value) || 
            (product.slug && currentProductSlug && product.slug === currentProductSlug) ||
            (productNameFromPage && product.name === productNameFromPage)) {
            option.selected = true;
        }
        
        productsSelect.appendChild(option);
    });
    
    // إذا كان هناك معرف منتج حالي وليس موجود في القائمة الثابتة، نضيفه
    if (productIdInput.value || currentProductSlug) {
        const productId = productIdInput.value ? parseInt(productIdInput.value) : null;
        const productName = getProductNameFromPage() || 'Current Product';
        
        // التحقق من أن المنتج ليس موجودًا بالفعل في القائمة
        const exists = hardcodedProducts.some(p => {
            return (productId && p.id === productId) || 
                   (currentProductSlug && p.slug === currentProductSlug) ||
                   (p.name === productName);
        });
        
        if (!exists) {
            const option = document.createElement('option');
            option.value = productId || '0'; // استخدام معرف افتراضي إذا لم يكن متاحًا
            option.text = productName;
            option.selected = true;
            productsSelect.appendChild(option);
        }
    }
}

// الحصول على اسم المنتج من الصفحة الحالية
function getProductNameFromPage() {
    // محاولة العثور على عنوان المنتج في الصفحة
    const productTitle = document.querySelector('.product-type-title');
    if (productTitle) {
        return productTitle.textContent.trim();
    }
    
    // محاولة العثور على عنوان المنتج بديل
    const pageTitle = document.querySelector('.page-title h1');
    if (pageTitle) {
        return pageTitle.textContent.trim();
    }
    
    return null;
}

// فتح المودال
function openModal(productId = null) {
    // تعيين معرف المنتج إذا تم تمريره
    if (productId) {
        productIdInput.value = productId;
        productSpecificInput.checked = true;
        generalInquiryInput.checked = false;
        
        // تفعيل خيار "Product Specific"
        generalInquiryOption.classList.remove('active');
        productSpecificOption.classList.add('active');
        
        // إظهار قسم المنتجات
        productsSection.classList.remove('hidden');
    } else {
        productIdInput.value = '';
    }
    
    // مسح أي اختيارات سابقة وجلب قائمة منتجات جديدة
    productsSelect.innerHTML = '';
    fetchProducts();
    
    // فتح المودال
    inquiryModal.classList.add('active');
    document.body.style.overflow = 'hidden'; // منع التمرير في الصفحة الرئيسية
    
    // تفعيل البحث في حقل اختيار الدولة في كل مرة يتم فتح المودال
    // (لضمان أن الحقل سيكون جاهزًا للبحث)
    try {
        // تحقق من وجود jQuery وmكتبة select2
        if (typeof $ !== 'undefined' && $.fn && $.fn.select2) {
            const $countrySelect = $('select[name="country"]');
            // تحقق من وجود العنصر أولا
            if ($countrySelect.length > 0) {
                $countrySelect.select2({
                    placeholder: 'Select Country',
                    allowClear: true,
                    width: '100%'
                });
            }
        } else {
            console.warn('Select2 library not loaded. Country search disabled.');
        }
    } catch (error) {
        console.error('Error initializing Select2:', error);
    }
    
    // مسح حقل الهاتف إذا كان موجوداً
    if (phoneInput) {
        phoneInput.value = '';
        phoneError.style.display = 'none';
    }
}

// إغلاق المودال
function closeModal() {
    inquiryModal.classList.remove('active');
    document.body.style.overflow = ''; // استعادة التمرير في الصفحة الرئيسية
    
    // إزالة تهيئة Select2 عند إغلاق المودال - مع تحقق أفضل
    try {
        // تحقق من وجود jQuery أولا
        if (typeof $ !== 'undefined' && $.fn && $.fn.select2) {
            // تحقق من وجود العنصر وإذا كان مهيئا فعلا بواسطة select2
            const $countrySelect = $('select[name="country"]');
            if ($countrySelect.length > 0 && $countrySelect.data('select2')) {
                $countrySelect.select2('destroy');
            }
        }
    } catch (error) {
        console.error('Error destroying Select2:', error);
    }
}

// تهيئة حقل الهاتف باستخدام intl-tel-input
function initializePhoneInput() {
    try {
        iti = window.intlTelInput(phoneInput, {
            utilsScript: 'https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/utils.js',
            separateDialCode: true,
            preferredCountries: ['eg', 'sa', 'ae', 'us', 'gb'],
            initialCountry: 'auto',
            geoIpLookup: function(callback) {
                // استخدام proxy محلي للتحقق من IP وتجنب مشاكل CORS
                fetch('/api/ip-lookup/')
                .then(res => {
                    if (!res.ok) throw new Error('IP lookup failed');
                    return res.json();
                })
                .then(data => {
                    if (data && data.country_code) {
                        callback(data.country_code);
                    } else {
                        throw new Error('No country code found');
                    }
                })
                .catch((error) => {
                    console.log('Could not determine user country, using default:', error);
                    callback('eg'); // مصر كاحتياطي
                });
            },
            customPlaceholder: function(selectedCountryPlaceholder, selectedCountryData) {
                // تخصيص النص المرجعي للهاتف
                return "e.g. " + selectedCountryPlaceholder;
            }
        });
        
        // الاستماع لتغييرات حقل الهاتف للتحقق
        phoneInput.addEventListener('input', validatePhoneNumber);
        
        // الاستماع لتغيير البلد في iti لتحديث حقل البلد
        phoneInput.addEventListener('countrychange', function() {
            if (iti) {
                // الحصول على رمز الدولة وتحديث الحقل المخفي
                const countryData = iti.getSelectedCountryData();
                if (countryData && countryData.dialCode) {
                    countryCodeInput.value = '+' + countryData.dialCode;
                    
                    // تحديث اختيار الدولة في select إذا كان مختلفًا
                    updateCountrySelect(countryData.iso2);
                }
            }
        });
        
        // ربط حقل البلد بمكتبة الهاتف
        countrySelect.addEventListener('change', function() {
            const selectedOption = countrySelect.options[countrySelect.selectedIndex];
            const countryName = selectedOption.text;
            let countryCode = getCountryCodeByName(countryName);
            
            if (countryCode && iti) {
                iti.setCountry(countryCode.toLowerCase());
            }
        });
    } catch (error) {
        console.error('Error initializing phone input:', error);
    }
}

// تحديث اختيار الدولة في القائمة المنسدلة عند تغيير الدولة في حقل الهاتف
function updateCountrySelect(countryCode) {
    if (!countrySelect || !countryCode) return;
    
    // تحويل رمز الدولة إلى اسم الدولة
    const countryName = getCountryNameByCode(countryCode);
    if (!countryName) return;
    
    // البحث عن الخيار المناسب في القائمة المنسدلة
    let found = false;
    
    // تنظيف اسم الدولة من الأقواس والنصوص الإضافية
    // مثال: "Egypt (‫مصر‬‎)" سيتم تحويله إلى "egypt"
    const cleanCountryName = countryName.toLowerCase()
                                       .replace(/\(.*?\)/g, '') // إزالة أي نص بين قوسين وقوسين
                                       .trim();
    
    for (let i = 0; i < countrySelect.options.length; i++) {
        // تنظيف اسم الدولة في القائمة المنسدلة أيضًا
        const optionText = countrySelect.options[i].text;
        const cleanOptionText = optionText.toLowerCase()
                                        .replace(/\(.*?\)/g, '')
                                        .trim();
        
        // المقارنة مع التركيز على الجزء الأساسي من اسم الدولة
        // نقارن الاسم المنظف فقط، أو نتحقق إذا كان أحدهما يحتوي الآخر
        if (cleanOptionText === cleanCountryName || 
            cleanOptionText.includes(cleanCountryName) || 
            cleanCountryName.includes(cleanOptionText)) {
            
            // تحديث اختيار الدولة في الـ Select2
            if ($.fn.select2) {
                $(countrySelect).val(countrySelect.options[i].value).trigger('change');
            } else {
                countrySelect.selectedIndex = i;
            }
            
            found = true;
            break;
        }
    }
    
    // نحاول البحث بالاعتماد على رمز الدولة إذا لم ينجح البحث بالاسم
    if (!found) {
        const codeMap = {
            'eg': 'Egypt',
            'dz': 'Algeria',
            'sa': 'Saudi Arabia',
            'ae': 'United Arab Emirates',
            'us': 'United States',
            'gb': 'United Kingdom',
            'az': 'Azerbaijan',
            'io': 'British Indian Ocean Territory'
            // يمكن إضافة المزيد من رموز الدول هنا
        };
        
        if (codeMap[countryCode.toLowerCase()]) {
            const simpleCountryName = codeMap[countryCode.toLowerCase()];
            
            for (let i = 0; i < countrySelect.options.length; i++) {
                if (countrySelect.options[i].text === simpleCountryName) {
                    // تحديث اختيار الدولة
                    if ($.fn.select2) {
                        $(countrySelect).val(countrySelect.options[i].value).trigger('change');
                    } else {
                        countrySelect.selectedIndex = i;
                    }
                    
                    found = true;
                    break;
                }
            }
        }
    }
    
    if (!found) {
        console.warn(`Country not found in the dropdown: ${countryName} (${countryCode})`);
    }
}

// الحصول على اسم الدولة من رمز الدولة - طريقة محسنة
function getCountryNameByCode(countryCode) {
    // استخدام البيانات من مكتبة intlTelInput إذا كانت متاحة
    if (window.intlTelInputGlobals && window.intlTelInputGlobals.getCountryData) {
        const countryData = window.intlTelInputGlobals.getCountryData();
        const country = countryData.find(c => c.iso2.toLowerCase() === countryCode.toLowerCase());
        if (country) {
            // استخراج الجزء الإنجليزي فقط من اسم الدولة إذا أمكن
            // مثال: لاستخراج "Egypt" من "Egypt (‫مصر‬‎)"
            const simplifiedName = country.name.split('(')[0].trim();
            return simplifiedName || country.name;
        }
    }
    
    // الطريقة الاحتياطية - استخدام قائمة ثابتة
    const countryCodeMap = {
        'eg': 'Egypt',
        'sa': 'Saudi Arabia',
        'ae': 'United Arab Emirates',
        'us': 'United States',
        'gb': 'United Kingdom',
        'ca': 'Canada',
        'fr': 'France',
        'de': 'Germany',
        'it': 'Italy',
        'es': 'Spain',
        'au': 'Australia',
        'nz': 'New Zealand',
        'dz': 'Algeria',
        'ar': 'Argentina',
        'at': 'Austria',
        'bh': 'Bahrain',
        'bd': 'Bangladesh',
        'be': 'Belgium',
        'br': 'Brazil',
        'kh': 'Cambodia',
        'cl': 'Chile',
        'cn': 'China',
        'co': 'Colombia',
        'cz': 'Czech Republic',
        'dk': 'Denmark',
        'fi': 'Finland',
        'gr': 'Greece',
        'hk': 'Hong Kong',
        'hu': 'Hungary',
        'in': 'India',
        'id': 'Indonesia',
        'ir': 'Iran',
        'iq': 'Iraq',
        'ie': 'Ireland',
        'il': 'Israel',
        'jp': 'Japan',
        'jo': 'Jordan',
        'kw': 'Kuwait',
        'lb': 'Lebanon',
        'ly': 'Libya',
        'my': 'Malaysia',
        'mx': 'Mexico',
        'ma': 'Morocco',
        'nl': 'Netherlands',
        'ng': 'Nigeria',
        'no': 'Norway',
        'om': 'Oman',
        'pk': 'Pakistan',
        'pa': 'Panama',
        'pe': 'Peru',
        'ph': 'Philippines',
        'pl': 'Poland',
        'pt': 'Portugal',
        'qa': 'Qatar',
        'ro': 'Romania',
        'ru': 'Russia',
        'sg': 'Singapore',
        'za': 'South Africa',
        'kr': 'Korea, South',
        'lk': 'Sri Lanka',
        'se': 'Sweden',
        'ch': 'Switzerland',
        'sy': 'Syria',
        'tw': 'Taiwan',
        'th': 'Thailand',
        'tn': 'Tunisia',
        'tr': 'Turkey',
        'ua': 'Ukraine',
        'ye': 'Yemen',
        'az': 'Azerbaijan',
        'io': 'British Indian Ocean Territory',
    };
    
    return countryCodeMap[countryCode.toLowerCase()] || null;
}

// الحصول على رمز الدولة من اسم الدولة - طريقة محسنة
function getCountryCodeByName(countryName) {
    // تنظيف اسم الدولة قبل البحث
    const cleanCountryName = countryName.toLowerCase().replace(/\(.*?\)/g, '').trim();
    
    // استخدام البيانات من مكتبة intlTelInput إذا كانت متاحة
    if (window.intlTelInputGlobals && window.intlTelInputGlobals.getCountryData) {
        const countryData = window.intlTelInputGlobals.getCountryData();
        
        // البحث عن الدولة باسمها (بحث غير حساس لحالة الأحرف ومع تنظيف الاسم)
        for (const country of countryData) {
            const cleanCurrentName = country.name.toLowerCase().replace(/\(.*?\)/g, '').trim();
            
            if (cleanCurrentName === cleanCountryName || 
                cleanCurrentName.includes(cleanCountryName) || 
                cleanCountryName.includes(cleanCurrentName)) {
                
                return country.iso2;
            }
        }
    }
    
    // الطريقة الاحتياطية - استخدام قائمة ثابتة
    const countryNameMap = {
        'Egypt': 'eg',
        'Saudi Arabia': 'sa',
        'United Arab Emirates': 'ae',
        'United States': 'us',
        'United Kingdom': 'gb',
        'Canada': 'ca',
        'France': 'fr',
        'Germany': 'de',
        'Italy': 'it',
        'Spain': 'es',
        'Australia': 'au',
        'New Zealand': 'nz',
        'Algeria': 'dz',
        'Argentina': 'ar',
        'Austria': 'at',
        'Bahrain': 'bh',
        'Bangladesh': 'bd',
        'Belgium': 'be',
        'Brazil': 'br',
        'Cambodia': 'kh',
        'Chile': 'cl',
        'China': 'cn',
        'Colombia': 'co',
        'Czech Republic': 'cz',
        'Denmark': 'dk',
        'Finland': 'fi',
        'Greece': 'gr',
        'Hong Kong': 'hk',
        'Hungary': 'hu',
        'India': 'in',
        'Indonesia': 'id',
        'Iran': 'ir',
        'Iraq': 'iq',
        'Ireland': 'ie',
        'Israel': 'il',
        'Japan': 'jp',
        'Jordan': 'jo',
        'Kuwait': 'kw',
        'Lebanon': 'lb',
        'Libya': 'ly',
        'Malaysia': 'my',
        'Mexico': 'mx',
        'Morocco': 'ma',
        'Netherlands': 'nl',
        'Nigeria': 'ng',
        'Norway': 'no',
        'Oman': 'om',
        'Pakistan': 'pk',
        'Panama': 'pa',
        'Peru': 'pe',
        'Philippines': 'ph',
        'Poland': 'pl',
        'Portugal': 'pt',
        'Qatar': 'qa',
        'Romania': 'ro',
        'Russia': 'ru',
        'Singapore': 'sg',
        'South Africa': 'za',
        'Korea, South': 'kr',
        'Sri Lanka': 'lk',
        'Sweden': 'se',
        'Switzerland': 'ch',
        'Syria': 'sy',
        'Taiwan': 'tw',
        'Thailand': 'th',
        'Tunisia': 'tn',
        'Turkey': 'tr',
        'Ukraine': 'ua',
        'Yemen': 'ye',
        'Azerbaijan': 'az',
        'British Indian Ocean Territory': 'io',
    };
    
    // محاولة البحث الدقيق أولاً
    if (countryNameMap[countryName]) {
        return countryNameMap[countryName];
    }
    
    // محاولة البحث غير الحساس لحالة الأحرف
    for (const [name, code] of Object.entries(countryNameMap)) {
        const cleanMapName = name.toLowerCase();
        if (cleanMapName === cleanCountryName || 
            cleanMapName.includes(cleanCountryName) || 
            cleanCountryName.includes(cleanMapName)) {
            return code;
        }
    }
    
    return null;
}

// التحقق من رقم الهاتف
function validatePhoneNumber() {
    if (!iti) return true;
    
    if (phoneInput.value.trim()) {
        if (!iti.isValidNumber()) {
            const errorCode = iti.getValidationError();
            let errorMsg = 'Invalid phone number';
            
            // ترجمة رموز الخطأ إلى رسائل مفهومة
            switch(errorCode) {
                case 1:
                    errorMsg = 'Invalid country code';
                    break;
                case 2:
                    errorMsg = 'Phone number too short';
                    break;
                case 3:
                    errorMsg = 'Phone number too long';
                    break;
                case 4:
                    errorMsg = 'Not a valid phone number';
                    break;
            }
            
            phoneError.textContent = errorMsg;
            phoneError.style.display = 'block';
            return false;
        } else {
            // تخزين رقم الهاتف الكامل مع كود الدولة
            countryCodeInput.value = iti.getSelectedCountryData().dialCode;
            phoneError.style.display = 'none';
            return true;
        }
    } else {
        phoneError.style.display = 'none';
        return true;
    }
}

// دالة للتحقق من صحة الإيميل
function validateEmail(email) {
    // تعبير منتظم بسيط للتحقق من وجود @ و. في الإيميل
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// تهيئة عناصر المودال
function initializeModal() {
    // تعريف العناصر الأساسية
    inquiryModal = document.getElementById('inquiryModal');
    modalOverlay = document.querySelector('.inquiry-modal-overlay');
    closeButton = document.querySelector('.inquiry-modal-close');
    inquiryButtons = document.querySelectorAll('.inquiry-button');
    inquiryForm = document.getElementById('inquiryForm');
    productIdInput = document.getElementById('product_id');
    
    // عناصر نوع الاستفسار
    generalInquiryOption = document.getElementById('general-inquiry-option');
    productSpecificOption = document.getElementById('product-specific-option');
    generalInquiryInput = document.getElementById('general-inquiry-input');
    productSpecificInput = document.getElementById('product-specific-input');
    productsSection = document.getElementById('modal-products-section');
    productsSelect = document.getElementById('products-select');
    
    // عناصر الهاتف والدولة
    phoneInput = document.getElementById('phone');
    countrySelect = document.getElementById('country-select');
    phoneError = document.getElementById('phone-error');
    countryCodeInput = document.getElementById('country-code');
    
    // تفعيل خاصية البحث في حقل اختيار الدولة باستخدام Select2
    try {
        // تحقق من وجود jQuery وmكتبة select2
        if (typeof $ !== 'undefined' && $.fn && $.fn.select2) {
            const $countrySelect = $('select[name="country"]');
            // تحقق من وجود العنصر أولا
            if ($countrySelect.length > 0) {
                $countrySelect.select2({
                    placeholder: 'Select Country',
                    allowClear: true,
                    width: '100%'
                });
            }
        } else {
            console.warn('Select2 library not loaded. Country search disabled.');
        }
    } catch (error) {
        console.error('Error initializing Select2:', error);
    }
    
    // تهيئة حقل الهاتف الدولي
    if (phoneInput && countrySelect) {
        initializePhoneInput();
    }

    // ربط أزرار الاستفسار بوظيفة فتح المودال
    inquiryButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // الحصول على معرف المنتج من السمة المخصصة data-product-id
            const productId = this.getAttribute('data-product-id');
            openModal(productId);
        });
    });
    
    // التبديل بين أنواع الاستفسار
    if (generalInquiryOption && productSpecificOption) {
        generalInquiryOption.addEventListener('click', function() {
            generalInquiryInput.checked = true;
            productSpecificInput.checked = false;
            
            generalInquiryOption.classList.add('active');
            productSpecificOption.classList.remove('active');
            
            // إخفاء قسم المنتجات ومسح الاختيارات
            productsSection.classList.add('hidden');
            
            // عند اختيار الاستعلام العام، نمسح اختيارات المنتجات
            // لتجنب إرسال طلب غير صحيح
            productsSelect.selectedIndex = -1;
        });
        
        productSpecificOption.addEventListener('click', function() {
            generalInquiryInput.checked = false;
            productSpecificInput.checked = true;
            
            generalInquiryOption.classList.remove('active');
            productSpecificOption.classList.add('active');
            
            productsSection.classList.remove('hidden');
            
            // تأكد من جلب المنتجات إذا كانت غير موجودة
            fetchProducts();
        });
    }
    
    // إغلاق المودال عند النقر على زر الإغلاق
    if (closeButton) {
        closeButton.addEventListener('click', closeModal);
    }
    
    // إغلاق المودال عند النقر على الخلفية
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeModal);
    }
    
    // إغلاق المودال عند الضغط على زر Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && inquiryModal.classList.contains('active')) {
            closeModal();
        }
    });
    
    // معالجة إرسال النموذج
    if (inquiryForm) {
        inquiryForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // التحقق من صحة النموذج
            let isValid = true;
            
            // التحقق من صحة الإيميل
            const emailInput = document.querySelector('input[name="email"]');
            const emailError = document.getElementById('email-error');
            
            if (emailInput && emailInput.value.trim()) {
                if (!validateEmail(emailInput.value.trim())) {
                    emailError.textContent = 'Please enter a valid email address';
                    emailError.style.display = 'block';
                    isValid = false;
                    console.error('Validation failed: Invalid email');
                } else {
                    emailError.textContent = '';
                    emailError.style.display = 'none';
                }
            }
            
            // التحقق من وجود منتجات محددة في حالة اختيار نوع الاستفسار المتعلق بالمنتج
            if (productSpecificInput.checked) {
                const selectedProducts = productsSelect.selectedOptions;
                
                if (selectedProducts.length === 0) {
                    document.getElementById('products-error').textContent = 'Please select at least one product for product specific inquiries.';
                    document.getElementById('products-error').classList.remove('hidden');
                    isValid = false;
                    console.error('Validation failed: No products selected');
                } else {
                    document.getElementById('products-error').classList.add('hidden');
                }
            } else {
                // إخفاء أي أخطاء سابقة
                document.getElementById('products-error').classList.add('hidden');
            }
            
            // التحقق من صحة رقم الهاتف
            if (iti && phoneInput.value.trim()) {
                if (!validatePhoneNumber()) {
                    isValid = false;
                    console.error('Validation failed: Invalid phone number');
                } else {
                    // تخزين الرقم الدولي الكامل
                    const fullNumber = iti.getNumber();
                    
                    // تحديث قيمة حقل الهاتف برقم الهاتف الدولي الكامل
                    phoneInput.value = fullNumber;
                    
                    // إضافة رمز الدولة إلى الحقل المخفي
                    const countryData = iti.getSelectedCountryData();
                    countryCodeInput.value = '+' + countryData.dialCode;
                }
            }
            
            if (!isValid) return;
            
            // إرسال النموذج باستخدام Fetch API
            fetch(inquiryForm.action, {
                method: 'POST',
                body: new FormData(inquiryForm),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // عرض رسالة النجاح وإغلاق المودال باستخدام SweetAlert
                    const successMessage = 'Thank you for your inquiry. We will get back to you soon.';
                    
                    Swal.fire({
                        icon: 'success',
                        title: 'Success',
                        text: successMessage,
                        confirmButtonColor: '#39AE68',
                        confirmButtonText: 'OK',
                        timer: 7000,
                        timerProgressBar: true
                    });
                    
                    inquiryForm.reset();
                    closeModal();
                } else {
                    // عرض رسالة الخطأ باستخدام SweetAlert
                    const errorMessage = 'An error occurred while sending your inquiry. Please try again.';
                    
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: data.message || errorMessage,
                        confirmButtonColor: '#39AE68',
                        confirmButtonText: 'OK'
                    });
                    
                    // عرض أخطاء حقول محددة إذا كانت موجودة
                    if (data.errors) {
                        // عرض أخطاء الحقول المختلفة
                        if (data.errors.products) {
                            document.getElementById('products-error').textContent = data.errors.products[0];
                            document.getElementById('products-error').classList.remove('hidden');
                        }
                        // عرض أخطاء حقل الهاتف
                        if (data.errors.phone) {
                            phoneError.textContent = data.errors.phone[0];
                            phoneError.style.display = 'block';
                        }
                        // عرض أخطاء حقل الإيميل
                        if (data.errors.email) {
                            emailError.textContent = data.errors.email[0];
                            emailError.style.display = 'block';
                        }
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                
                // عرض رسالة الخطأ باستخدام SweetAlert
                const errorMessage = 'An error occurred while sending your inquiry. Please try again.';
                
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: errorMessage,
                    confirmButtonColor: '#39AE68',
                    confirmButtonText: 'OK'
                });
            });
        });
    }
}

// استدعاء وظائف التهيئة عند تحميل المستند
document.addEventListener('DOMContentLoaded', function() {
    // التحقق إذا كان المودال قد تم تهيئته بالفعل
    if (typeof window.inquiryModalInitialized === 'undefined') {
        // وضع علامة أن المودال قد تم تهيئته
        window.inquiryModalInitialized = true;
        
        // تهيئة عناصر المودال
        initializeModal();
        
        // تحميل المنتجات مقدمًا لتحسين الأداء
        preloadProducts();
    }
});