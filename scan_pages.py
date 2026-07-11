# scan_pages.py - 扫描所有页面HTML检测渲染问题
import urllib.request, re, os, json

BASE = "https://liuandxu.github.io/digital-electronics-wiki"

PAGES = [
    ("首页", "/"),
    ("1.1", "/ch01/"),
    ("1.2", "/ch01/1-2/"),
    ("1.3", "/ch01/1-3/"),
    ("1章总结", "/ch01/summary/"),
    ("2.1", "/ch02/"),
    ("2.2", "/ch02/2-2/"),
    ("2.3", "/ch02/2-3/"),
    ("2.4", "/ch02/2-4/"),
    ("2.5", "/ch02/2-5/"),
    ("2章总结", "/ch02/summary/"),
    ("3.1", "/ch03/"),
    ("3.2", "/ch03/3-2/"),
    ("3.3", "/ch03/3-3/"),
    ("3.4", "/ch03/3-4/"),
    ("3.5", "/ch03/3-5/"),
    ("3章总结", "/ch03/summary/"),
    ("4.1", "/ch04/"),
    ("4.2", "/ch04/4-2/"),
    ("4.3", "/ch04/4-3/"),
    ("4.4", "/ch04/4-4/"),
    ("4.5", "/ch04/4-5/"),
    ("4.6", "/ch04/4-6/"),
    ("4.7", "/ch04/4-7/"),
    ("4章总结", "/ch04/summary/"),
    ("5.1", "/ch05/"),
    ("5.2", "/ch05/5-2/"),
    ("5.3", "/ch05/5-3/"),
    ("5.4", "/ch05/5-4/"),
    ("5.5", "/ch05/5-5/"),
    ("5章总结", "/ch05/summary/"),
    ("6.1", "/ch06/"),
    ("6.2", "/ch06/6-2/"),
    ("6章总结", "/ch06/summary/"),
    ("7.1", "/ch07/"),
    ("7.2", "/ch07/7-2/"),
    ("7章总结", "/ch07/summary/"),
    ("8.1", "/ch08/"),
    ("8.2", "/ch08/8-2/"),
    ("8章总结", "/ch08/summary/"),
]

issues = []

for name, path in PAGES:
    url = BASE + path
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8')
    except Exception as e:
        issues.append({"page": name, "url": url, "error": f"HTTP请求失败: {e}"})
        continue

    page_issues = []

    # 1. MathJax 错误: "Misplaced", "Undefined", "Extra", "Missing"
    mathjax_errors = re.findall(r'(Misplaced \\\w+|Undefined control sequence|Extra .*?|Missing .*? inserted|Double superscript|Double subscript)', html)
    if mathjax_errors:
        page_issues.append({"type": "MathJax错误", "details": list(set(mathjax_errors))[:5]})

    # 2. Mermaid 错误: "Syntax error", "Parse error"
    mermaid_errors = re.findall(r'(Syntax error in text|Parse error|mermaid.*?error)', html, re.IGNORECASE)
    if mermaid_errors:
        page_issues.append({"type": "Mermaid错误", "details": list(set(mermaid_errors))[:5]})

    # 3. 未渲染的模板变量 {{ ... }}
    template_vars = re.findall(r'(\{\{[^}]+\}\})', html)
    if template_vars:
        page_issues.append({"type": "未渲染模板变量", "details": list(set(template_vars))[:5]})

    # 4. 原始 LaTeX 代码泄露到正文 (不是在script/style中)
    # 检查文章正文中是否有 \[ \] 或 \( \) 原始标记（未渲染）
    article_match = re.search(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    if article_match:
        article = article_match.group(1)
        # 去掉 script 和 style 标签内容
        article = re.sub(r'<script[^>]*>.*?</script>', '', article, flags=re.DOTALL)
        article = re.sub(r'<style[^>]*>.*?</style>', '', article, flags=re.DOTALL)
        # 检查是否有未渲染的 LaTeX 标记
        raw_latex = re.findall(r'(\\\[|\\\]|\\\(|\\\))', article)
        if raw_latex:
            page_issues.append({"type": "未渲染LaTeX标记", "details": f"发现 {len(raw_latex)} 个原始标记"})

    # 5. 检查是否有 <br/> 或 <br> 在 mermaid 代码块中
    br_in_mermaid = re.findall(r'class="mermaid"[^>]*>.*?<br/?>', html, re.DOTALL)
    if br_in_mermaid:
        page_issues.append({"type": "Mermaid中br标签", "details": f"发现 {len(br_in_mermaid)} 处"})

    # 6. 检查 \hline 在正文中
    hline_in_article = False
    if article_match:
        if '\\hline' in article_match.group(1):
            hline_in_article = True
    if '\\hline' in html and 'Misplaced' in html:
        page_issues.append({"type": "hline错误", "details": "MathJax hline渲染错误"})

    # 7. 404 检查
    if '404' in html and 'Not found' in html:
        page_issues.append({"type": "404错误", "details": "页面不存在"})

    # 8. 检查空 mermaid div (没有 svg)
    mermaid_divs = re.findall(r'class="mermaid"[^>]*>(.*?)</div>', html, re.DOTALL)
    empty_mermaid = [d for d in mermaid_divs if '<svg' not in d and 'data-processed' not in d]
    # Note: after JS rendering, mermaid divs contain SVGs. In raw HTML they contain the source code.
    # So this check only works for rendered pages. Skip for raw HTML.

    # 9. 检查重复内容 (admonition content duplicated)
    # Look for repeated text patterns

    # 10. 检查图片缺失
    img_srcs = re.findall(r'<img[^>]+src="([^"]+)"', html)
    for img_src in img_srcs:
        if not img_src.startswith('http') and not img_src.startswith('data:'):
            page_issues.append({"type": "图片路径", "details": img_src})

    if page_issues:
        issues.append({"page": name, "url": url, "issues": page_issues})

# 输出结果
print(f"扫描完成: {len(PAGES)} 页, 发现 {len(issues)} 页有问题\n")
for item in issues:
    print(f"### {item['page']} ({item['url']})")
    for iss in item.get('issues', []):
        print(f"  - {iss['type']}: {iss['details']}")
    if 'error' in item:
        print(f"  - 错误: {item['error']}")
    print()

# 保存JSON
with open(r'c:\Users\34873\.trae-cn\work\6a525fecb1d572d2e33e23bd\scan_results.json', 'w', encoding='utf-8') as f:
    json.dump(issues, f, ensure_ascii=False, indent=2)
print("详细结果已保存到 scan_results.json")
