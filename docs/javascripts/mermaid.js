// Mermaid 暗色自动适配
(function() {
    var mermaidSource = {};
    window.__mermaidSource = mermaidSource;

    function saveOriginalSource() {
        document.querySelectorAll('.mermaid').forEach(function(el) {
            var key = el.dataset.mermaidId || (el.dataset.mermaidId = 'mermaid-' + Math.random().toString(36).slice(2));
            if (!mermaidSource[key]) {
                mermaidSource[key] = el.textContent;
            }
        });
    }

    function restoreAndRender() {
        var isDark = document.body.getAttribute('data-md-color-scheme') === 'slate';
        mermaid.initialize({
            startOnLoad: false,
            theme: isDark ? 'dark' : 'default',
            flowchart: { useMaxWidth: true }
        });

        document.querySelectorAll('.mermaid').forEach(function(el) {
            var key = el.dataset.mermaidId;
            if (key && mermaidSource[key]) {
                el.textContent = mermaidSource[key];
                el.removeAttribute('data-processed');
            }
        });

        mermaid.run({ querySelector: '.mermaid' });
    }

    function loadMermaid() {
        saveOriginalSource();
        var script = document.createElement('script');
        script.async = false;
        script.src = 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js';
        script.onload = restoreAndRender;
        document.head.appendChild(script);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadMermaid);
    } else {
        loadMermaid();
    }

    var observer = new MutationObserver(function() {
        restoreAndRender();
    });
    observer.observe(document.body, { attributes: true, attributeFilter: ['data-md-color-scheme'] });
})();
