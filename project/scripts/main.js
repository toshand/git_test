// DOM読み込み完了後に実行
document.addEventListener('DOMContentLoaded', function() {
    // モバイルナビゲーション
    initMobileNavigation();
    
    // スムーズスクロール
    initSmoothScroll();
    
    // チェックボックスの機能
    initCheckboxes();
    
    // スクロールアニメーション
    initScrollAnimations();
    
    // アクティブナビゲーション
    initActiveNavigation();
});

// モバイルナビゲーション機能
function initMobileNavigation() {
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
        
        // メニューリンクをクリックしたときにメニューを閉じる
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
        
        // メニュー外をクリックしたときにメニューを閉じる
        document.addEventListener('click', function(event) {
            if (!hamburger.contains(event.target) && !navMenu.contains(event.target)) {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            }
        });
    }
}

// スムーズスクロール機能
function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 80; // ヘッダーの高さを考慮
                
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// チェックボックス機能
function initCheckboxes() {
    const checkboxes = document.querySelectorAll('.checklist-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const label = this.nextElementSibling;
            const details = label.nextElementSibling;
            
            if (this.checked) {
                // チェックされたときのアニメーション
                label.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    label.style.transform = 'scale(1)';
                }, 200);
                
                // 詳細表示のアニメーション
                if (details) {
                    details.style.maxHeight = details.scrollHeight + 'px';
                    details.style.opacity = '1';
                }
            } else {
                // 詳細表示を非表示
                if (details) {
                    details.style.maxHeight = '0';
                    details.style.opacity = '0';
                }
            }
        });
        
        // 初期状態で詳細を非表示
        const details = checkbox.nextElementSibling.nextElementSibling;
        if (details) {
            details.style.maxHeight = '0';
            details.style.opacity = '0';
            details.style.overflow = 'hidden';
            details.style.transition = 'max-height 0.3s ease, opacity 0.3s ease';
        }
    });
}

// スクロールアニメーション
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // アニメーション対象の要素
    const animatedElements = document.querySelectorAll('.about-card, .service-card, .news-item, .toc-card, .checklist-item, .support-card, .department-card, .business-card, .executive-card');
    
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(element);
    });
}

// アクティブナビゲーション
function initActiveNavigation() {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    window.addEventListener('scroll', function() {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (pageYOffset >= sectionTop - 200) {
                current = section.getAttribute('id');
            }
        });
        
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === `#${current}`) {
                link.classList.add('active');
            }
        });
    });
}

// ユーティリティ関数
const utils = {
    // デバウンス関数
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // スロットル関数
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // 要素が画面内にあるかチェック
    isElementInViewport: function(el) {
        const rect = el.getBoundingClientRect();
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
            rect.right <= (window.innerWidth || document.documentElement.clientWidth)
        );
    }
};

// パフォーマンス最適化
window.addEventListener('scroll', utils.throttle(function() {
    // スクロール時の処理を最適化
}, 16)); // 約60fps

// リサイズ時の処理
window.addEventListener('resize', utils.debounce(function() {
    // リサイズ時の処理
}, 250));

// エラーハンドリング
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

// ページの読み込み完了
window.addEventListener('load', function() {
    // ページ読み込み完了後の処理
    console.log('ページの読み込みが完了しました');
    
    // ローディングアニメーションがあれば非表示にする
    const loader = document.querySelector('.loader');
    if (loader) {
        loader.style.opacity = '0';
        setTimeout(() => {
            loader.style.display = 'none';
        }, 300);
    }
});

// アクセシビリティの改善
document.addEventListener('keydown', function(e) {
    // ESCキーでモバイルメニューを閉じる
    if (e.key === 'Escape') {
        const hamburger = document.querySelector('.hamburger');
        const navMenu = document.querySelector('.nav-menu');
        
        if (hamburger && navMenu) {
            hamburger.classList.remove('active');
            navMenu.classList.remove('active');
        }
    }
});

// フォーカス管理
document.addEventListener('focusin', function(e) {
    // フォーカス可能な要素にフォーカスが当たったときの処理
    if (e.target.classList.contains('nav-link')) {
        e.target.style.outline = '2px solid var(--primary-color)';
        e.target.style.outlineOffset = '2px';
    }
});

document.addEventListener('focusout', function(e) {
    // フォーカスが外れたときの処理
    if (e.target.classList.contains('nav-link')) {
        e.target.style.outline = 'none';
    }
});

// データ属性を使用した機能拡張
document.querySelectorAll('[data-animate]').forEach(element => {
    const animationType = element.getAttribute('data-animate');
    
    switch(animationType) {
        case 'fade-in':
            element.style.opacity = '0';
            element.style.transition = 'opacity 0.6s ease';
            setTimeout(() => {
                element.style.opacity = '1';
            }, 100);
            break;
            
        case 'slide-up':
            element.style.transform = 'translateY(30px)';
            element.style.opacity = '0';
            element.style.transition = 'transform 0.6s ease, opacity 0.6s ease';
            setTimeout(() => {
                element.style.transform = 'translateY(0)';
                element.style.opacity = '1';
            }, 100);
            break;
    }
});

// ローカルストレージを使用した設定保存
const settings = {
    save: function(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('設定の保存に失敗しました:', e);
        }
    },
    
    load: function(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('設定の読み込みに失敗しました:', e);
            return defaultValue;
        }
    }
};

// チェックボックスの状態を保存
document.querySelectorAll('.checklist-checkbox').forEach(checkbox => {
    const id = checkbox.id;
    const savedState = settings.load(`checklist_${id}`, false);
    
    if (savedState) {
        checkbox.checked = true;
        checkbox.dispatchEvent(new Event('change'));
    }
    
    checkbox.addEventListener('change', function() {
        settings.save(`checklist_${id}`, this.checked);
    });
});

// コンソールログ（開発用）
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    console.log('開発モードで実行中');
    console.log('利用可能な機能:');
    console.log('- モバイルナビゲーション');
    console.log('- スムーズスクロール');
    console.log('- チェックボックス機能');
    console.log('- スクロールアニメーション');
    console.log('- 設定保存機能');
}
