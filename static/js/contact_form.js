/**
 * ملف JavaScript لإدارة صفحة الاتصال
 */

// تفعيل التصريح الصارم
'use strict';

// العناصر الأساسية
var phoneInput, countrySelect, phoneError, countryCodeInput, emailInput, emailError;
var contactForm;

// كائن intlTelInput
var iti;

// استدعاء دالة التهيئة عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', initializeContactForm);

// تهيئة نموذج الاتصال
function initializeContactForm() {
    // تعريف العناصر
    contactForm = document.querySelector('.contact-form form');
    phoneInput = document.querySelector('input[name="phone"]');
    countrySelect = document.querySelector('select[name="country"]');
    countryCodeInput = document.querySelector('select[name="country_code"]');
    emailInput = document.querySelector('input[name="email"]');
    
    // إنشاء عناصر الخطأ إذا لم تكن موجودة
    if (!document.getElementById('phone-error')) {
        phoneError = document.createElement('div');
        phoneError.id = 'phone-error';
        phoneError.className = 'text-xs text-red-500 mt-1';
        if (phoneInput) {
            phoneInput.parentNode.appendChild(phoneError);
        }
    } else {
        phoneError = document.getElementById('phone-error');
    }
    
    if (!document.getElementById('email-error')) {
        emailError = document.createElement('div');
        emailError.id = 'email-error';
        emailError.className = 'text-xs text-red-500 mt-1';
        if (emailInput) {
            emailInput.parentNode.appendChild(emailError);
        }
    } else {
        emailError = document.getElementById('email-error');
    }
    
    // تأكد من تحميل مكتبة SweetAlert إذا لم تكن محملة
    if (typeof Swal === 'undefined') {
        // تحميل SweetAlert ديناميكيا
        loadSweetAlertLibrary();
    }
    
    // تفعيل مكتبة Select2 لحقل اختيار الدولة إذا كانت متاحة
    initializeSelect2();
    
    // تهيئة حقل الهاتف الدولي
    if (phoneInput && countrySelect) {
        initializePhoneInput();
    }
    
    // ربط التحقق من البريد الإلكتروني
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            validateEmail();
        });
    }
    
    // معالجة إرسال النموذج
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            // منع السلوك الافتراضي للنموذج
            e.preventDefault();
            
            // التحقق من صحة النموذج قبل الإرسال
            if (validateForm()) {
                // إرسال النموذج باستخدام Fetch API
                fetch(contactForm.action, {
                    method: 'POST',
                    body: new FormData(contactForm),
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => {
                    // في حالة نجاح الإرسال
                    if (response.ok) {
                        // عرض رسالة النجاح باستخدام SweetAlert
                        Swal.fire({
                            icon: 'success',
                            title: 'Success',
                            text: 'Thank you for your message. We will get back to you soon.',
                            confirmButtonColor: '#39AE68',
                            confirmButtonText: 'OK',
                            timer: 7000,
                            timerProgressBar: true
                        });
                        
                        // إعادة تعيين النموذج
                        contactForm.reset();
                    } else {
                        // عرض رسالة الخطأ باستخدام SweetAlert
                        Swal.fire({
                            icon: 'error',
                            title: 'Error',
                            text: 'An error occurred while sending your message. Please try again.',
                            confirmButtonColor: '#39AE68',
                            confirmButtonText: 'OK'
                        });
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    
                    // عرض رسالة الخطأ باستخدام SweetAlert
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'An error occurred while sending your message. Please try again.',
                        confirmButtonColor: '#39AE68',
                        confirmButtonText: 'OK'
                    });
                });
            }
        });
    }
}

// تحميل مكتبة SweetAlert2 ديناميكيًا
function loadSweetAlertLibrary() {
    return new Promise((resolve, reject) => {
        // تحميل JavaScript
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/sweetalert2@11';
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// تهيئة مكتبة Select2 للدول
function initializeSelect2() {
    // التأكد من وجود jQuery و مكتبة Select2
    if (typeof $ !== 'undefined' && $.fn && $.fn.select2) {
        try {
            $(countrySelect).select2({
                placeholder: "Select Country",
                width: '100%',
            }).on('select2:select', function(e) {
                // عند تغيير الدولة، تحديث حقل الهاتف
                const countryName = e.params.data.text;
                const countryCode = getCountryCodeByName(countryName);
                
                if (countryCode && iti) {
                    iti.setCountry(countryCode.toLowerCase());
                } else {
                    // محاولة تطابق الاسم مع نمط مختلف إذا لم يتم العثور عليه
                    const alternativeCode = findAlternativeCountryCode(countryName);
                    if (alternativeCode && iti) {
                        iti.setCountry(alternativeCode.toLowerCase());
                    }
                }
            });
        } catch (error) {
            console.error('Error initializing Select2:', error);
        }
    } else {
        // تحميل المكتبات الضرورية لـ Select2 إذا لم تكن موجودة
        loadSelect2Library();
    }
}

// تحميل مكتبة Select2 ديناميكيًا
function loadSelect2Library() {
    if (typeof $ === 'undefined') {
        console.warn('jQuery is not loaded. Select2 cannot be initialized.');
        return;
    }
    
    return new Promise((resolve, reject) => {
        // تحميل CSS
        const cssLink = document.createElement('link');
        cssLink.rel = 'stylesheet';
        cssLink.href = 'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css';
        document.head.appendChild(cssLink);
        
        // تحميل JavaScript
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js';
        script.onload = () => {
            initializeSelect2();
            resolve();
        };
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// تنسيق عرض الدولة في القائمة المنسدلة - لم تعد مستخدمة
function formatCountryOption(country) {
    return country.text;
}

// تنسيق عرض الدولة المختارة - لم تعد مستخدمة
function formatCountrySelection(country) {
    return country.text;
}

// تهيئة حقل الهاتف الدولي
function initializePhoneInput() {
    // التأكد من تحميل مكتبة intlTelInput
    if (typeof window.intlTelInput === 'undefined') {
        // تحميل المكتبة ديناميكيًا إذا لم تكن محملة
        loadIntlTelInputLibrary().then(() => {
            setupIntlTelInput();
        }).catch(error => {
            console.error('Failed to load intlTelInput library:', error);
        });
    } else {
        // المكتبة محملة بالفعل
        setupIntlTelInput();
    }
}

// تحميل مكتبة intlTelInput ديناميكيًا
function loadIntlTelInputLibrary() {
    return new Promise((resolve, reject) => {
        // تحميل CSS
        const cssLink = document.createElement('link');
        cssLink.rel = 'stylesheet';
        cssLink.href = 'https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/css/intlTelInput.min.css';
        document.head.appendChild(cssLink);
        
        // تحميل JavaScript
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/intlTelInput.min.js';
        script.onload = () => {
            // تحميل ملف utils.js بعد تحميل المكتبة الرئيسية
            const utilsScript = document.createElement('script');
            utilsScript.src = 'https://cdn.jsdelivr.net/npm/intl-tel-input@18.2.1/build/js/utils.js';
            utilsScript.onload = resolve;
            utilsScript.onerror = reject;
            document.head.appendChild(utilsScript);
        };
        script.onerror = reject;
        document.head.appendChild(script);
    });
}

// إعداد مكتبة intlTelInput
function setupIntlTelInput() {
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
                    updateCountryCode('+' + countryData.dialCode);
                    
                    // تحديث اختيار الدولة في select إذا كان مختلفًا
                    updateCountrySelect(countryData.iso2);
                }
            }
        });
        
        // ربط حقل البلد بمكتبة الهاتف
        if (typeof $ !== 'undefined' && $.fn && $.fn.select2) {
            // إذا كانت select2 نشطة
            $(countrySelect).on('select2:select', function(e) {
                const countryName = e.params.data.text;
                const countryCode = getCountryCodeByName(countryName);
                
                if (countryCode && iti) {
                    iti.setCountry(countryCode.toLowerCase());
                }
            });
        } else {
            // استخدام الحدث العادي للتغيير
            countrySelect.addEventListener('change', function() {
                const selectedOption = countrySelect.options[countrySelect.selectedIndex];
                const countryName = selectedOption.text;
                let countryCode = getCountryCodeByName(countryName);
                
                if (countryCode && iti) {
                    iti.setCountry(countryCode.toLowerCase());
                }
            });
        }
    } catch (error) {
        console.error('Error initializing phone input:', error);
    }
}

// تحديث حقل رمز الدولة
function updateCountryCode(code) {
    // إذا كان الحقل قائمة منسدلة
    if (countryCodeInput.tagName === 'SELECT') {
        // تبحث عن الخيار المناسب أو تختار الأقرب
        const cleanCode = code.replace(/[^0-9]/g, '');
        let bestMatch = null;
        
        for (let i = 0; i < countryCodeInput.options.length; i++) {
            const optionValue = countryCodeInput.options[i].value.replace(/[^0-9]/g, '');
            if (optionValue === cleanCode) {
                countryCodeInput.selectedIndex = i;
                return;
            }
            
            // احتفظ بأفضل تطابق
            if (cleanCode.startsWith(optionValue) || optionValue.startsWith(cleanCode)) {
                if (!bestMatch || optionValue.length > bestMatch.length) {
                    bestMatch = optionValue;
                    countryCodeInput.selectedIndex = i;
                }
            }
        }
    } else {
        // إذا كان حقل نصي عادي
        countryCodeInput.value = code;
    }
}

// تحديث اختيار الدولة في القائمة المنسدلة
function updateCountrySelect(countryCode) {
    if (!countrySelect || !countryCode) return;
    
    // تحويل رمز الدولة إلى اسم الدولة
    const countryName = getCountryNameByCode(countryCode);
    if (!countryName) return;
    
    // البحث عن الخيار المناسب في القائمة المنسدلة
    let found = false;
    
    // تحديث باستخدام Select2 إذا كانت مستخدمة
    if (typeof $ !== 'undefined' && $.fn && $.fn.select2) {
        for (let i = 0; i < countrySelect.options.length; i++) {
            const optionText = countrySelect.options[i].text.trim();
            
            if (optionText.toLowerCase() === countryName.toLowerCase() || 
                optionText.toLowerCase().includes(countryName.toLowerCase()) || 
                countryName.toLowerCase().includes(optionText.toLowerCase())) {
                
                // استخدام API الخاصة بـ Select2
                $(countrySelect).val(countrySelect.options[i].value).trigger('change');
                
                found = true;
                break;
            }
        }
    } else {
        // استخدام الطريقة التقليدية
        for (let i = 0; i < countrySelect.options.length; i++) {
            const optionText = countrySelect.options[i].text.trim();
            
            if (optionText.toLowerCase() === countryName.toLowerCase() || 
                optionText.toLowerCase().includes(countryName.toLowerCase()) || 
                countryName.toLowerCase().includes(optionText.toLowerCase())) {
                
                countrySelect.selectedIndex = i;
                found = true;
                break;
            }
        }
    }
    
    if (!found) {
        console.warn(`Country not found in the dropdown: ${countryName}`);
    }
}

// الحصول على اسم الدولة من رمز الدولة
function getCountryNameByCode(countryCode) {
    // استخدام البيانات من مكتبة intlTelInput إذا كانت متاحة
    if (window.intlTelInputGlobals && window.intlTelInputGlobals.getCountryData) {
        const countryData = window.intlTelInputGlobals.getCountryData();
        const country = countryData.find(c => c.iso2.toLowerCase() === countryCode.toLowerCase());
        if (country) {
            // استخراج الجزء الإنجليزي فقط من اسم الدولة إذا أمكن
            const simplifiedName = country.name.split('(')[0].trim();
            return simplifiedName || country.name;
        }
    }
    
    // قائمة مبسطة للدول الشائعة
    const countryCodeMap = {
        'eg': 'Egypt',
        'sa': 'Saudi Arabia',
        'ae': 'UAE',
        'us': 'USA',
        'gb': 'UK',
        'ca': 'Canada',
        'fr': 'France',
        'de': 'Germany',
        'fi': 'Finland',
        'gr': 'Greece'
    };
    
    return countryCodeMap[countryCode.toLowerCase()] || null;
}

// الحصول على رمز الدولة من اسم الدولة
function getCountryCodeByName(countryName) {
    if (!countryName) return null;
    
    // القائمة المبسطة للدول الشائعة
    const countryNameMap = {
        'egypt': 'eg',
        'saudi arabia': 'sa',
        'saudi': 'sa',
        'uae': 'ae',
        'emirates': 'ae',
        'united arab emirates': 'ae',
        'usa': 'us',
        'united states': 'us',
        'uk': 'gb',
        'united kingdom': 'gb',
        'britain': 'gb',
        'canada': 'ca',
        'france': 'fr',
        'germany': 'de',
        'finland': 'fi',
        'greece': 'gr',
        'italy': 'it',
        'spain': 'es',
        'russia': 'ru',
        'russian federation': 'ru',
        'china': 'cn',
        'japan': 'jp',
        'south korea': 'kr',
        'korea, south': 'kr',
        'australia': 'au',
        'brazil': 'br',
        'india': 'in',
        'mexico': 'mx',
        'netherlands': 'nl',
        'holland': 'nl',
        'sweden': 'se',
        'switzerland': 'ch',
        'turkey': 'tr',
        'argentina': 'ar',
        'belgium': 'be',
        'denmark': 'dk',
        'ireland': 'ie',
        'norway': 'no',
        'poland': 'pl',
        'portugal': 'pt',
        'austria': 'at',
        'chile': 'cl',
        'colombia': 'co',
        'czechia': 'cz',
        'czech republic': 'cz',
        'czech': 'cz',
        'hungary': 'hu',
        'new zealand': 'nz',
        'singapore': 'sg',
        'south africa': 'za',
        'thailand': 'th',
        'vietnam': 'vn',
        'israel': 'il',
        'malaysia': 'my',
        'philippines': 'ph',
        'afghanistan': 'af',
        'albania': 'al',
        'algeria': 'dz',
        'andorra': 'ad',
        'angola': 'ao',
        'antigua': 'ag',
        'antigua and barbuda': 'ag',
        'barbuda': 'ag',
        'armenia': 'am',
        'azerbaijan': 'az',
        'bahamas': 'bs',
        'bahrain': 'bh',
        'bangladesh': 'bd',
        'barbados': 'bb',
        'belarus': 'by',
        'belize': 'bz',
        'benin': 'bj',
        'bhutan': 'bt',
        'bolivia': 'bo',
        'bosnia': 'ba',
        'herzegovina': 'ba',
        'bosnia and herzegovina': 'ba',
        'botswana': 'bw',
        'brunei': 'bn',
        'bulgaria': 'bg',
        'burkina': 'bf',
        'burkina faso': 'bf',
        'faso': 'bf',
        'burundi': 'bi',
        'cabo verde': 'cv',
        'cape verde': 'cv',
        'cambodia': 'kh',
        'cameroon': 'cm',
        'central african republic': 'cf',
        'central african': 'cf',
        'chad': 'td',
        'comoros': 'km',
        'congo': 'cg',
        'costa rica': 'cr',
        'costa': 'cr',
        'croatia': 'hr',
        'cuba': 'cu',
        'cyprus': 'cy',
        'djibouti': 'dj',
        'dominica': 'dm',
        'dominican republic': 'do',
        'dominican': 'do',
        'east timor': 'tl',
        'timor': 'tl',
        'timor-leste': 'tl',
        'ecuador': 'ec',
        'el salvador': 'sv',
        'salvador': 'sv',
        'equatorial guinea': 'gq',
        'equatorial': 'gq',
        'eritrea': 'er',
        'estonia': 'ee',
        'eswatini': 'sz',
        'swaziland': 'sz',
        'ethiopia': 'et',
        'fiji': 'fj',
        'gabon': 'ga',
        'gambia': 'gm',
        'georgia': 'ge',
        'ghana': 'gh',
        'grenada': 'gd',
        'guatemala': 'gt',
        'guinea': 'gn',
        'guinea-bissau': 'gw',
        'bissau': 'gw',
        'guyana': 'gy',
        'haiti': 'ht',
        'honduras': 'hn',
        'iceland': 'is',
        'indonesia': 'id',
        'iran': 'ir',
        'iraq': 'iq',
        'jamaica': 'jm',
        'jordan': 'jo',
        'kazakhstan': 'kz',
        'kenya': 'ke',
        'kiribati': 'ki',
        'korea, north': 'kp',
        'north korea': 'kp',
        'kosovo': 'xk',
        'kuwait': 'kw',
        'kyrgyzstan': 'kg',
        'kyrgyz': 'kg',
        'laos': 'la',
        'latvia': 'lv',
        'lebanon': 'lb',
        'lesotho': 'ls',
        'liberia': 'lr',
        'libya': 'ly',
        'liechtenstein': 'li',
        'lithuania': 'lt',
        'luxembourg': 'lu',
        'madagascar': 'mg',
        'malawi': 'mw',
        'maldives': 'mv',
        'mali': 'ml',
        'malta': 'mt',
        'marshall islands': 'mh',
        'marshall': 'mh',
        'mauritania': 'mr',
        'mauritius': 'mu',
        'micronesia': 'fm',
        'moldova': 'md',
        'monaco': 'mc',
        'mongolia': 'mn',
        'montenegro': 'me',
        'morocco': 'ma',
        'mozambique': 'mz',
        'myanmar': 'mm',
        'burma': 'mm',
        'namibia': 'na',
        'nauru': 'nr',
        'nepal': 'np',
        'nicaragua': 'ni',
        'niger': 'ne',
        'nigeria': 'ng',
        'north macedonia': 'mk',
        'macedonia': 'mk',
        'oman': 'om',
        'pakistan': 'pk',
        'palau': 'pw',
        'palestine': 'ps',
        'palestinian': 'ps',
        'panama': 'pa',
        'papua new guinea': 'pg',
        'papua': 'pg',
        'paraguay': 'py',
        'peru': 'pe',
        'qatar': 'qa',
        'romania': 'ro',
        'rwanda': 'rw',
        'saint kitts and nevis': 'kn',
        'kitts': 'kn',
        'nevis': 'kn',
        'saint lucia': 'lc',
        'lucia': 'lc',
        'saint vincent': 'vc',
        'saint vincent and the grenadines': 'vc',
        'grenadines': 'vc',
        'samoa': 'ws',
        'san marino': 'sm',
        'sao tome and principe': 'st',
        'sao tome': 'st',
        'principe': 'st',
        'senegal': 'sn',
        'serbia': 'rs',
        'seychelles': 'sc',
        'sierra leone': 'sl',
        'sierra': 'sl',
        'leone': 'sl',
        'slovakia': 'sk',
        'slovenia': 'si',
        'solomon islands': 'sb',
        'solomon': 'sb',
        'somalia': 'so',
        'south sudan': 'ss',
        'sri lanka': 'lk',
        'ceylon': 'lk',
        'sudan': 'sd',
        'suriname': 'sr',
        'syria': 'sy',
        'syrian': 'sy',
        'taiwan': 'tw',
        'tajikistan': 'tj',
        'tanzania': 'tz',
        'togo': 'tg',
        'tonga': 'to',
        'trinidad': 'tt',
        'tobago': 'tt',
        'trinidad and tobago': 'tt',
        'tunisia': 'tn',
        'turkmenistan': 'tm',
        'tuvalu': 'tv',
        'uganda': 'ug',
        'ukraine': 'ua',
        'uruguay': 'uy',
        'uzbekistan': 'uz',
        'vanuatu': 'vu',
        'vatican': 'va',
        'vatican city': 'va',
        'holy see': 'va',
        'venezuela': 've',
        'yemen': 'ye',
        'zambia': 'zm',
        'zimbabwe': 'zw'
    };
    
    return countryNameMap[countryName.toLowerCase()] || null;
}

// التحقق من رقم الهاتف
function validatePhoneNumber() {
    if (!iti || !phoneInput) return true;
    
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
            updateCountryCode('+' + iti.getSelectedCountryData().dialCode);
            phoneError.style.display = 'none';
            return true;
        }
    } else {
        phoneError.style.display = 'none';
        return true;
    }
}

// التحقق من صحة البريد الإلكتروني
function validateEmail() {
    if (!emailInput || !emailError) return true;
    
    const email = emailInput.value.trim();
    if (!email) return true;
    
    // تعبير منتظم للتحقق من صحة البريد الإلكتروني
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!emailRegex.test(email)) {
        emailError.textContent = 'Please enter a valid email address';
        emailError.style.display = 'block';
        return false;
    } else {
        emailError.style.display = 'none';
        return true;
    }
}

// التحقق من صحة النموذج بالكامل
function validateForm() {
    let isValid = true;
    
    // التحقق من البريد الإلكتروني
    if (!validateEmail()) {
        isValid = false;
    }
    
    // التحقق من رقم الهاتف
    if (!validatePhoneNumber()) {
        isValid = false;
    }
    
    return isValid;
}

// إضافة دالة جديدة للعثور على كود دولة بديل
function findAlternativeCountryCode(countryName) {
    if (!countryName) return null;
    
    // تحويل اسم الدولة إلى حروف صغيرة وإزالة الأحرف الخاصة
    const normalizedName = countryName.toLowerCase().trim();
    
    // البحث عن تطابق جزئي
    for (const [key, value] of Object.entries(getFullCountryMap())) {
        if (normalizedName.includes(key) || key.includes(normalizedName)) {
            return value;
        }
    }
    
    // إذا لم نجد مطابقة مباشرة أو جزئية، نحاول البحث عن كلمات رئيسية
    const keywords = normalizedName.split(/\s+/);
    for (const keyword of keywords) {
        if (keyword.length > 3) {  // تجاهل الكلمات القصيرة جدًا مثل "and" و "the"
            for (const [key, value] of Object.entries(getFullCountryMap())) {
                if (key.includes(keyword)) {
                    return value;
                }
            }
        }
    }
    
    return null;
}

// دالة تعيد الخريطة الكاملة للدول
function getFullCountryMap() {
    return {
        'egypt': 'eg',
        'saudi arabia': 'sa',
        'saudi': 'sa',
        'uae': 'ae',
        'emirates': 'ae',
        'united arab emirates': 'ae',
        'usa': 'us',
        'united states': 'us',
        'uk': 'gb',
        'united kingdom': 'gb',
        'britain': 'gb',
        'canada': 'ca',
        'france': 'fr',
        'germany': 'de',
        'finland': 'fi',
        'greece': 'gr',
        'italy': 'it',
        'spain': 'es',
        'russia': 'ru',
        'russian federation': 'ru',
        'china': 'cn',
        'japan': 'jp',
        'south korea': 'kr',
        'korea, south': 'kr',
        'australia': 'au',
        'brazil': 'br',
        'india': 'in',
        'mexico': 'mx',
        'netherlands': 'nl',
        'holland': 'nl',
        'sweden': 'se',
        'switzerland': 'ch',
        'turkey': 'tr',
        'argentina': 'ar',
        'belgium': 'be',
        'denmark': 'dk',
        'ireland': 'ie',
        'norway': 'no',
        'poland': 'pl',
        'portugal': 'pt',
        'austria': 'at',
        'chile': 'cl',
        'colombia': 'co',
        'czechia': 'cz',
        'czech republic': 'cz',
        'czech': 'cz',
        'hungary': 'hu',
        'new zealand': 'nz',
        'singapore': 'sg',
        'south africa': 'za',
        'thailand': 'th',
        'vietnam': 'vn',
        'israel': 'il',
        'malaysia': 'my',
        'philippines': 'ph',
        'afghanistan': 'af',
        'albania': 'al',
        'algeria': 'dz',
        'andorra': 'ad',
        'angola': 'ao',
        'antigua': 'ag',
        'antigua and barbuda': 'ag',
        'barbuda': 'ag',
        'armenia': 'am',
        'azerbaijan': 'az',
        'bahamas': 'bs',
        'bahrain': 'bh',
        'bangladesh': 'bd',
        'barbados': 'bb',
        'belarus': 'by',
        'belize': 'bz',
        'benin': 'bj',
        'bhutan': 'bt',
        'bolivia': 'bo',
        'bosnia': 'ba',
        'herzegovina': 'ba',
        'bosnia and herzegovina': 'ba',
        'botswana': 'bw',
        'brunei': 'bn',
        'bulgaria': 'bg',
        'burkina': 'bf',
        'burkina faso': 'bf',
        'faso': 'bf',
        'burundi': 'bi',
        'cabo verde': 'cv',
        'cape verde': 'cv',
        'cambodia': 'kh',
        'cameroon': 'cm',
        'central african republic': 'cf',
        'central african': 'cf',
        'chad': 'td',
        'comoros': 'km',
        'congo': 'cg',
        'costa rica': 'cr',
        'costa': 'cr',
        'croatia': 'hr',
        'cuba': 'cu',
        'cyprus': 'cy',
        'djibouti': 'dj',
        'dominica': 'dm',
        'dominican republic': 'do',
        'dominican': 'do',
        'east timor': 'tl',
        'timor': 'tl',
        'timor-leste': 'tl',
        'ecuador': 'ec',
        'el salvador': 'sv',
        'salvador': 'sv',
        'equatorial guinea': 'gq',
        'equatorial': 'gq',
        'eritrea': 'er',
        'estonia': 'ee',
        'eswatini': 'sz',
        'swaziland': 'sz',
        'ethiopia': 'et',
        'fiji': 'fj',
        'gabon': 'ga',
        'gambia': 'gm',
        'georgia': 'ge',
        'ghana': 'gh',
        'grenada': 'gd',
        'guatemala': 'gt',
        'guinea': 'gn',
        'guinea-bissau': 'gw',
        'bissau': 'gw',
        'guyana': 'gy',
        'haiti': 'ht',
        'honduras': 'hn',
        'iceland': 'is',
        'indonesia': 'id',
        'iran': 'ir',
        'iraq': 'iq',
        'jamaica': 'jm',
        'jordan': 'jo',
        'kazakhstan': 'kz',
        'kenya': 'ke',
        'kiribati': 'ki',
        'korea, north': 'kp',
        'north korea': 'kp',
        'kosovo': 'xk',
        'kuwait': 'kw',
        'kyrgyzstan': 'kg',
        'kyrgyz': 'kg',
        'laos': 'la',
        'latvia': 'lv',
        'lebanon': 'lb',
        'lesotho': 'ls',
        'liberia': 'lr',
        'libya': 'ly',
        'liechtenstein': 'li',
        'lithuania': 'lt',
        'luxembourg': 'lu',
        'madagascar': 'mg',
        'malawi': 'mw',
        'maldives': 'mv',
        'mali': 'ml',
        'malta': 'mt',
        'marshall islands': 'mh',
        'marshall': 'mh',
        'mauritania': 'mr',
        'mauritius': 'mu',
        'micronesia': 'fm',
        'moldova': 'md',
        'monaco': 'mc',
        'mongolia': 'mn',
        'montenegro': 'me',
        'morocco': 'ma',
        'mozambique': 'mz',
        'myanmar': 'mm',
        'burma': 'mm',
        'namibia': 'na',
        'nauru': 'nr',
        'nepal': 'np',
        'nicaragua': 'ni',
        'niger': 'ne',
        'nigeria': 'ng',
        'north macedonia': 'mk',
        'macedonia': 'mk',
        'oman': 'om',
        'pakistan': 'pk',
        'palau': 'pw',
        'palestine': 'ps',
        'palestinian': 'ps',
        'panama': 'pa',
        'papua new guinea': 'pg',
        'papua': 'pg',
        'paraguay': 'py',
        'peru': 'pe',
        'qatar': 'qa',
        'romania': 'ro',
        'rwanda': 'rw',
        'saint kitts and nevis': 'kn',
        'kitts': 'kn',
        'nevis': 'kn',
        'saint lucia': 'lc',
        'lucia': 'lc',
        'saint vincent': 'vc',
        'saint vincent and the grenadines': 'vc',
        'grenadines': 'vc',
        'samoa': 'ws',
        'san marino': 'sm',
        'sao tome and principe': 'st',
        'sao tome': 'st',
        'principe': 'st',
        'senegal': 'sn',
        'serbia': 'rs',
        'seychelles': 'sc',
        'sierra leone': 'sl',
        'sierra': 'sl',
        'leone': 'sl',
        'slovakia': 'sk',
        'slovenia': 'si',
        'solomon islands': 'sb',
        'solomon': 'sb',
        'somalia': 'so',
        'south sudan': 'ss',
        'sri lanka': 'lk',
        'ceylon': 'lk',
        'sudan': 'sd',
        'suriname': 'sr',
        'syria': 'sy',
        'syrian': 'sy',
        'taiwan': 'tw',
        'tajikistan': 'tj',
        'tanzania': 'tz',
        'togo': 'tg',
        'tonga': 'to',
        'trinidad': 'tt',
        'tobago': 'tt',
        'trinidad and tobago': 'tt',
        'tunisia': 'tn',
        'turkmenistan': 'tm',
        'tuvalu': 'tv',
        'uganda': 'ug',
        'ukraine': 'ua',
        'uruguay': 'uy',
        'uzbekistan': 'uz',
        'vanuatu': 'vu',
        'vatican': 'va',
        'vatican city': 'va',
        'holy see': 'va',
        'venezuela': 've',
        'yemen': 'ye',
        'zambia': 'zm',
        'zimbabwe': 'zw'
    };
}