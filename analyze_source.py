# analyze_source.py - 分析所有markdown源文件中的潜在渲染问题
import os, re, json

DOCS = r"d:\学习\数电\数电wiki\docs"
issues = []

def check_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    rel_path = os.path.relpath(filepath, DOCS).replace('\\', '/')
    file_issues = []
    
    # 1. Mermaid 中使用 <br/> 或 <br>
    mermaid_blocks = re.findall(r'```mermaid\n(.*?)```', content, re.DOTALL)
    for i, block in enumerate(mermaid_blocks):
        if re.search(r'<br/?>', block):
            file_issues.append({
                "type": "Mermaid-br标签",
                "detail": f"第{i+1}个mermaid块中包含<br>标签",
                "context": [l for l in block.split('\n') if '<br' in l][:3]
            })
        # 检查 emoji
        if re.search(r'[\U0001F300-\U0001F9FF\u2600-\u27BF]', block):
            file_issues.append({
                "type": "Mermaid-emoji",
                "detail": f"第{i+1}个mermaid块中包含emoji字符",
            })
        # 检查未引用的标签内容中的特殊字符
        labels = re.findall(r'\["([^"]*)"\]', block)
        for label in labels:
            if '(' in label or ')' in label or '[' in label:
                file_issues.append({
                    "type": "Mermaid-特殊字符",
                    "detail": f"标签中包含括号: \"{label}\"",
                })
    
    # 2. MathJax 中使用 \hline
    math_blocks = re.findall(r'\\\[(.*?)\\\]', content, re.DOTALL)
    for i, block in enumerate(math_blocks):
        if '\\hline' in block:
            file_issues.append({
                "type": "MathJax-hline",
                "detail": f"第{i+1}个display math块中包含\\hline",
            })
    
    # 3. 模板变量 {{ }}
    template_vars = re.findall(r'\{\{[^}]+\}\}', content)
    if template_vars:
        file_issues.append({
            "type": "模板变量",
            "detail": f"发现{len(template_vars)}个未渲染模板变量",
            "context": template_vars[:3]
        })
    
    # 4. 检查 $$ 公式 (MkDocs Material 用 \( \) 而非 $ $)
    dollar_math = re.findall(r'\$\$[^$]+\$\$', content)
    if dollar_math:
        file_issues.append({
            "type": "双美元符号公式",
            "detail": f"发现{len(dollar_math)}个$$公式块(可能不被支持)",
            "context": [d[:50] for d in dollar_math[:3]]
        })
    
    single_dollar = re.findall(r'(?<!\$)\$(?!\$)[^$\n]+(?<!\$)\$(?!\$)', content)
    if single_dollar:
        file_issues.append({
            "type": "单美元符号公式",
            "detail": f"发现{len(single_dollar)}个$...$行内公式(可能不被支持)",
            "context": [d[:50] for d in single_dollar[:3]]
        })
    
    # 5. 检查未闭合的公式标记
    open_paren = content.count('\\(')
    close_paren = content.count('\\)')
    if open_paren != close_paren:
        file_issues.append({
            "type": "公式未闭合",
            "detail": f"\\( 出现{open_paren}次, \\) 出现{close_paren}次",
        })
    
    open_bracket = content.count('\\[')
    close_bracket = content.count('\\]')
    if open_bracket != close_bracket:
        file_issues.append({
            "type": "公式未闭合",
            "detail": f"\\[ 出现{open_bracket}次, \\] 出现{close_bracket}次",
        })
    
    # 6. 检查 HTML 标签泄露到正文中
    raw_html = re.findall(r'<(?!\/?(?:a|img|b|i|strong|em|span|div|p|br|hr|table|tr|td|th|thead|tbody|ul|ol|li|code|pre|blockquote|h[1-6]|sup|sub|details|summary|mark|dl|dt|dd)\b)[a-zA-Z][^>]*>', content)
    if raw_html:
        file_issues.append({
            "type": "可疑HTML标签",
            "detail": f"发现{len(raw_html)}个可疑标签",
            "context": raw_html[:5]
        })
    
    # 7. 检查重复内容 (完全相同的段落)
    paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 50]
    seen = {}
    for p in paragraphs:
        p_clean = re.sub(r'[#*\-\[\]()`>]', '', p).strip()
        if p_clean in seen:
            file_issues.append({
                "type": "重复段落",
                "detail": f"重复内容: {p_clean[:60]}...",
            })
            break
        seen[p_clean] = True
    
    # 8. 检查 markdown 表格语法问题
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '|' in line and i > 0 and i < len(lines)-1:
            # 检查表格分隔行是否正确
            if re.match(r'^\s*\|[\s\-:|]+\|\s*$', line):
                # 这是分隔行,检查上下行是否有|
                if i > 0 and '|' not in lines[i-1]:
                    file_issues.append({
                        "type": "表格语法",
                        "detail": f"第{i+1}行: 表格分隔行前无表头",
                    })
    
    # 9. 检查 admonition 语法
    adm_errors = re.findall(r'!!!\s*(\w+)\s*(?:"([^"]*)")?', content)
    valid_types = {'note', 'abstract', 'info', 'tip', 'success', 'question', 'warning', 'failure', 'danger', 'bug', 'example', 'quote', 'compatibility'}
    for adm_type, adm_title in adm_errors:
        if adm_type.lower() not in valid_types:
            file_issues.append({
                "type": "admonition类型",
                "detail": f"未知admonition类型: !!!{adm_type}",
            })
    
    # 10. 检查 code block 语法
    code_blocks = re.findall(r'```(\w*)', content)
    for lang in code_blocks:
        if lang and lang not in {'mermaid', 'verilog', 'python', 'bash', 'yaml', 'json', 'javascript', 'js', 'html', 'css', 'text', 'c', 'cpp', 'java', 'sh', 'powershell', 'vhdl', '', 'plaintext'}:
            file_issues.append({
                "type": "代码块语言",
                "detail": f"未知代码块语言: {lang}",
            })
    
    if file_issues:
        issues.append({"file": rel_path, "issues": file_issues})

# 遍历所有 md 文件
for root, dirs, files in os.walk(DOCS):
    # 跳过 assets/javascripts/stylesheets
    dirs[:] = [d for d in dirs if d not in {'javascripts', 'stylesheets', 'assets'}]
    for f in sorted(files):
        if f.endswith('.md'):
            check_file(os.path.join(root, f))

# 输出结果
print(f"扫描完成: {len(issues)} 个文件有问题\n")
for item in sorted(issues, key=lambda x: x['file']):
    print(f"### {item['file']}")
    for iss in item['issues']:
        detail = iss['detail']
        ctx = iss.get('context', [])
        ctx_str = f" | 示例: {ctx}" if ctx else ""
        print(f"  - [{iss['type']}] {detail}{ctx_str}")
    print()

with open(r'c:\Users\34873\.trae-cn\work\6a525fecb1d572d2e33e23bd\source_issues.json', 'w', encoding='utf-8') as f:
    json.dump(issues, f, ensure_ascii=False, indent=2)
