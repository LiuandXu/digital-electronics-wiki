window.MathJax = {
  tex: {
    inlineMath: [['\\(', '\\)']],
    displayMath: [['\\[', '\\]']]
  },
  options: {
    skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
  },
  startup: {
    pageReady: () => {
      return MathJax.startup.defaultPageReady().then(() => {
        if (typeof document$ !== 'undefined') {
          document$.subscribe(() => {
            MathJax.typesetPromise();
          });
        }
      });
    }
  }
};
