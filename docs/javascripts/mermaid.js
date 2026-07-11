// Mermaid 暗色自动适配
(function() {
    var mermaidSource = {};

    function saveOriginalSource() {
        document.querySelectorAll('.mermaid').forEach(function(el) {
            var key = el.dataset.mermaidId || (el.dataset.mermaidId = 'mermaid-' + Math.random().toString(36).slice(2));
            if (!mermaidSource[key]) {
                mermaidSource[key] = el.textContent;
            }
        });
    }

    function initMermaid() {
        var isDark = document.body.getAttribute('data-md-color-scheme') === 'slate';
        mermaid.initialize({
            startOnLoad: false,
            theme: isDark ? 'dark' : 'default',
            flowchart: { useMaxWidth: true }
        });

        saveOriginalSource();

        document.querySelectorAll('.mermaid').forEach(function(el) {
            var key = el.dataset.mermaidId;
            if (key && mermaidSource[key]) {
                el.innerHTML = mermaidSource[key];
                el.removeAttribute('data-processed');
            }
        });

        mermaid.run({ querySelector: '.mermaid' });
    }

    document.addEventListener('DOMContentLoaded', initMermaid);

    var observer = new MutationObserver(function() {
        initMermaid();
    });
    observer.observe(document.body, { attributes: true, attributeFilter: ['data-md-color-scheme'] });
})();
