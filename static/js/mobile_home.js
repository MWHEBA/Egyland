/**
 * Mobile optimizations for the home page
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a mobile device
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        // Fix for 100vh on mobile browsers
        fixMobileVh();
        window.addEventListener('resize', fixMobileVh);
        
        // Set mobile slider images
        setMobileSliderImages();
        
        // Ensure mobile menu works properly (no need to create hamburger here, it's in header.html)
        enhanceMobileMenu();
        
        // Improve slider for mobile
        improveSliderForMobile();
        
        // Add swipe support
        addSwipeSupport();
        
        // Improve transitions
        improveTransitions();
        
        // Improve header interaction
        improveHeaderInteraction();
    }
});

/**
 * Fixes the 100vh issue on mobile browsers
 * by setting a CSS variable with the actual viewport height
 */
function fixMobileVh() {
    // First we get the viewport height and we multiply it by 1% to get a value for a vh unit
    let vh = window.innerHeight * 0.01;
    // Then we set the value in the --vh custom property to the root of the document
    document.documentElement.style.setProperty('--vh', `${vh}px`);
}

/**
 * Sets mobile slider images explicitly for mobile view
 */
function setMobileSliderImages() {
    const slides = document.querySelectorAll('#hero-slider .slide');
    
    slides.forEach(slide => {
        const mobileBgUrl = slide.getAttribute('data-mobile-bg');
        if (mobileBgUrl) {
            // Save original background in case of resize
            const originalBg = slide.style.backgroundImage;
            if (!slide.getAttribute('data-original-bg')) {
                slide.setAttribute('data-original-bg', originalBg);
            }
            
            // Set mobile background
            slide.style.backgroundImage = `url('${mobileBgUrl}')`;
            
            // Add additional mobile styling
            slide.style.backgroundSize = 'cover';
            slide.style.backgroundPosition = 'center';
        }
    });
}

/**
 * Enhances the mobile menu interaction
 */
function enhanceMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    const header = document.getElementById('main-header');
    
    if (mobileMenuButton && mobileMenu) {
        // Add subtle animation to the menu
        mobileMenu.addEventListener('transitionend', function() {
            if (mobileMenu.classList.contains('hidden')) {
                // Re-enable body scroll
                document.body.style.overflow = '';
            }
        });
        
        // Add ripple effect on menu items
        const mobileMenuLinks = mobileMenu.querySelectorAll('a');
        mobileMenuLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                // Add ripple effect on menu items
                addRippleEffect(e, this);
            });
        });
    }
}

/**
 * Creates a ripple effect on the clicked element
 */
function addRippleEffect(event, element) {
    // Create ripple element
    const ripple = document.createElement('span');
    ripple.classList.add('ripple');
    
    // Set ripple style
    ripple.style.position = 'absolute';
    ripple.style.borderRadius = '50%';
    ripple.style.backgroundColor = 'rgba(39, 174, 96, 0.3)';
    ripple.style.width = '100px';
    ripple.style.height = '100px';
    ripple.style.transform = 'translate(-50%, -50%) scale(0)';
    ripple.style.animation = 'ripple 0.6s linear forwards';
    
    // Get click position
    const rect = element.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    // Position ripple
    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;
    
    // Add ripple to element
    element.style.position = 'relative';
    element.style.overflow = 'hidden';
    element.appendChild(ripple);
    
    // Remove ripple after animation
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

/**
 * Improves the slider for mobile devices
 */
function improveSliderForMobile() {
    const slider = document.getElementById('hero-slider');
    if (!slider) return;
    
    // Make slider dots more visible and accessible
    const dots = document.querySelectorAll('.slider-nav-dot');
    dots.forEach(dot => {
        // Make dots bigger and easier to tap
        dot.style.width = '16px';
        dot.style.height = '16px';
        
        // Add ripple effect on tap
        dot.addEventListener('click', function(e) {
            addRippleEffect(e, this);
        });
    });
    
    // Add CSS for ripple animation if not already added
    if (!document.querySelector('style[data-type="ripple-animation"]')) {
        const style = document.createElement('style');
        style.setAttribute('data-type', 'ripple-animation');
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: translate(-50%, -50%) scale(2);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Optimize text sizes for mobile
    const slideTitles = document.querySelectorAll('.slide-title');
    slideTitles.forEach(title => {
        title.style.fontSize = '36px';
        title.style.lineHeight = '1.2';
        // Allow wrapping on mobile
        title.style.whiteSpace = 'normal';
    });
    
    // Adjust love text specifically
    const loveText = document.querySelector('.love-text');
    if (loveText) {
        loveText.style.fontSize = '42px';
    }
}

/**
 * Improves header interaction on scroll
 */
function improveHeaderInteraction() {
    const header = document.getElementById('main-header');
    let lastScrollTop = 0;
    const scrollThreshold = 10;
    
    if (!header) return;
    
    window.addEventListener('scroll', function() {
        const currentScroll = window.pageYOffset || document.documentElement.scrollTop;
        
        // If we've scrolled more than the threshold
        if (Math.abs(lastScrollTop - currentScroll) > scrollThreshold) {
            // Scrolling down
            if (currentScroll > lastScrollTop) {
                // Don't hide if menu is open
                if (document.getElementById('mobile-menu').classList.contains('hidden')) {
                    header.style.transform = 'translateY(-100%)';
                    header.style.transition = 'transform 0.3s ease';
                }
            } 
            // Scrolling up
            else {
                header.style.transform = 'translateY(0)';
                header.style.transition = 'transform 0.3s ease';
            }
            lastScrollTop = currentScroll;
        }
        
        // Change header appearance based on scroll position
        if (currentScroll > 50) {
            header.style.boxShadow = '0 2px 15px rgba(0, 0, 0, 0.15)';
        } else {
            // Only change if menu is not open
            if (document.getElementById('mobile-menu').classList.contains('hidden')) {
                header.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
            }
        }
    });
}

/**
 * Adds swipe support for the slider
 */
function addSwipeSupport() {
    const slider = document.getElementById('hero-slider');
    if (!slider) return;
    
    let startX;
    let endX;
    
    slider.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
    }, false);
    
    slider.addEventListener('touchend', function(e) {
        endX = e.changedTouches[0].clientX;
        handleSwipe();
    }, false);
    
    function handleSwipe() {
        const dots = document.querySelectorAll('.slider-nav-dot');
        let activeIndex = -1;
        
        // Find current active dot
        dots.forEach((dot, index) => {
            if (dot.classList.contains('active')) {
                activeIndex = index;
            }
        });
        
        if (activeIndex === -1) return;
        
        // Calculate swipe distance
        const swipeDistance = startX - endX;
        
        // Handle left/right swipe
        if (Math.abs(swipeDistance) > 50) {
            if (swipeDistance > 0) {
                // Swipe left - go to next slide
                const nextIndex = (activeIndex + 1) % dots.length;
                dots[nextIndex].click();
            } else {
                // Swipe right - go to previous slide
                const prevIndex = (activeIndex - 1 + dots.length) % dots.length;
                dots[prevIndex].click();
            }
        }
    }
}

/**
 * Improves transitions for mobile
 */
function improveTransitions() {
    // Make sure slide transitions are smooth
    const slides = document.querySelectorAll('#hero-slider .slide');
    slides.forEach(slide => {
        slide.style.transition = 'opacity 0.5s ease-out';
    });
} 