// Mermaid 暗色自动适配 + instant navigation 支持
(function() {
    var MERMAID_SRC = 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js?v=3';
    var STORE = {};
    window.__mermaidSource = STORE;
    var loaded = false;

    function getSource(el) {
        // 已渲染为 SVG 的节点 innerHTML 以标签开头，不能当作源码
        var html = el.innerHTML || '';
        if (/^\s*</.test(html)) return '';
        var txt = el.textContent || '';
        return txt.trim() ? txt : '';
    }

    function capture() {
        document.querySelectorAll('.mermaid').forEach(function(el) {
            var key = el.dataset.mermaidId ||
                (el.dataset.mermaidId = 'mermaid-' + Math.random().toString(36).slice(2));
            if (!STORE[key]) {
                var src = getSource(el);
                if (src) STORE[key] = src;
            }
        });
    }

    function allCaptured() {
        var els = document.querySelectorAll('.mermaid');
        if (!els.length) return true;
        for (var i = 0; i < els.length; i++) {
            var key = els[i].dataset.mermaidId;
            if (!key || !STORE[key] || !STORE[key].trim()) return false;
        }
        return true;
    }

    function initTheme() {
        var isDark = document.body.getAttribute('data-md-color-scheme') === 'slate';
        mermaid.initialize({
            startOnLoad: false,
            theme: isDark ? 'dark' : 'default',
            flowchart: { useMaxWidth: true },
            securityLevel: 'loose'
        });
    }

    function render() {
        if (!loaded || !window.mermaid) return;
        initTheme();
        var hadSource = false;
        document.querySelectorAll('.mermaid').forEach(function(el) {
            var key = el.dataset.mermaidId;
            if (key && STORE[key]) {
                el.textContent = STORE[key];
                el.removeAttribute('data-processed');
                hadSource = true;
            }
        });
        if (hadSource) {
            try {
                mermaid.run({ querySelector: '.mermaid' });
            } catch (e) {
                console.error('Mermaid render error', e);
            }
        }
    }

    function loadMermaid() {
        if (window.mermaid) {
            loaded = true;
            render();
            return;
        }
        var script = document.createElement('script');
        script.async = false;
        script.src = MERMAID_SRC;
        script.onload = function() { loaded = true; render(); };
        script.onerror = function() { console.error('Failed to load Mermaid'); };
        document.head.appendChild(script);
    }

    function start() {
        capture();
        if (allCaptured()) {
            loadMermaid();
        } else {
            setTimeout(start, 100);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', start);
    } else {
        start();
    }

    // 监听 instant navigation 内容变化
    if (typeof document$ !== 'undefined') {
        document$.subscribe(function() {
            STORE = {};
            start();
        });
    }

    // 仅监听主题切换（attribute 变化），不监听 childList 以避免干扰 MathJax
    var debounceTimer;
    var observer = new MutationObserver(function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(function() {
            if (loaded) render();
        }, 50);
    });
    observer.observe(document.body, {
        attributes: true,
        attributeFilter: ['data-md-color-scheme']
    });
})();
