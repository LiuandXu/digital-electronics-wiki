# generate_stats.py - 生成站点统计并注入 mkdocs.yml
import os, re
from ruamel.yaml import YAML

def collect_stats(docs_dir):
    stats = {"pages": 0, "formulas": 0, "images": 0, "code_blocks": 0}
    for root, _, files in os.walk(docs_dir):
        for f in files:
            if not f.endswith(".md"):
                continue
            rp = root.replace("\\", "/")
            if rp.endswith("/assets/js") or rp.endswith("/assets/css") or rp.endswith("/assets"):
                continue
            stats["pages"] += 1
            with open(os.path.join(root, f), "r", encoding="utf-8") as fp:
                content = fp.read()
            stats["formulas"] += len(re.findall(r'\\\(.*?\\\)|\\\[.*?\\\]', content, re.DOTALL))
            stats["images"] += len(re.findall(r'!\[.*?\]\(.*?\)', content))
            stats["code_blocks"] += len(re.findall(r'```', content)) // 2
    return stats

if __name__ == "__main__":
    stats = collect_stats("docs")
    yaml = YAML()
    yaml.preserve_quotes = True
    with open("mkdocs.yml", "r", encoding="utf-8") as f:
        config = yaml.load(f)
    if config.get("extra") is None:
        config["extra"] = {}
    config["extra"]["stats"] = stats
    with open("mkdocs.yml", "w", encoding="utf-8") as f:
        yaml.dump(config, f)
    print(f"站点统计: {stats['pages']} 页 | {stats['formulas']} 公式 | {stats['images']} 图片 | {stats['code_blocks']} 代码块")
