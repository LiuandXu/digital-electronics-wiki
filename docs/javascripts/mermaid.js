// Mermaid 暗色自动适配
function initMermaid() {
    var isDark = document.body.getAttribute('data-md-color-scheme') === 'slate';
    mermaid.initialize({
        theme: isDark ? 'dark' : 'default',
        flowchart: { useMaxWidth: true }
    });
    document.querySelectorAll('.mermaid').forEach(function(el) {
        el.removeAttribute('data-processed');
    });
    mermaid.run({ querySelector: '.mermaid' });
}

document.addEventListener('DOMContentLoaded', initMermaid);

var observer = new MutationObserver(function() {
    initMermaid();
});
observer.observe(document.body, { attributes: true, attributeFilter: ['data-md-color-scheme'] });
