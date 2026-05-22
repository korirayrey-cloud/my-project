import re
import os
import csv
from collections import Counter
import matplotlib.pyplot as plt

# ========== 设置路径 ==========
source_dir = r"D:\20074\latex_source"          # LaTeX 源文件目录
output_dir = r"D:\20074\生成文档"              # 输出目录（已存在）

# 确保输出目录存在（如果不存在则创建，安全起见）
os.makedirs(output_dir, exist_ok=True)

# 按顺序定义要分析的文件（只统计正文部分）
chapters = {
    "Preface": "preface.tex",
    "Introduction": "introduction.tex",
    "Ch1 - Spirit": "chapter1.tex",
    "Ch2 - Chinese Woman": "chapter2.tex",
    "Ch3 - Chinese Language": "chapter3.tex",
    "Ch4 - John Smith": "chapter4.tex",
    "Ch5 - Great Sinologue": "chapter5.tex",
    "Ch6 - Scholarship I": "chapter6.tex",
    "Ch7 - Scholarship II": "chapter7.tex",
    "Appendix": "appendix.tex"
}

def clean_latex(text):
    """去除 LaTeX 命令、注释、环境，保留自然语言"""
    # 去掉注释
    text = re.sub(r'(?<!\\)%.*$', '', text, flags=re.MULTILINE)
    # 去掉 \begin{...} ... \end{...} 环境（简单去掉标记保留内容）
    text = re.sub(r'\\begin\{.*?\}', '', text)
    text = re.sub(r'\\end\{.*?\}', '', text)
    # 去掉 \input{} 等
    text = re.sub(r'\\(?:input|include|includegraphics)\{[^}]*\}', '', text)
    # 将 \section{标题} 或 \section*{标题} 替换为 "标题"
    text = re.sub(r'\\(?:[a-zA-Z]+)\*?(?:\[.*?\])?\{(.*?)\}', r'\1', text)
    # 去掉残留的 \命令
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    # 去掉花括号、方括号
    text = re.sub(r'[{}]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text

def count_words(text, targets):
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    cnt = Counter(words)
    return {w: cnt.get(w, 0) for w in targets}

# ========== 统计 ==========
results = []
print("\n按章节统计（基于 LaTeX 源文件）")
print("-" * 60)
for name, filename in chapters.items():
    filepath = os.path.join(source_dir, filename)
    if not os.path.exists(filepath):
        print(f"警告：文件 {filename} 不存在，跳过")
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = f.read()
    cleaned = clean_latex(raw)
    civ_cnt = count_words(cleaned, ['civilisation', 'civilization'])
    mor_cnt = count_words(cleaned, ['moral', 'morality', 'morally'])
    civ_total = sum(civ_cnt.values())
    mor_total = sum(mor_cnt.values())
    results.append((name, civ_total, mor_total))
    print(f"{name:20} | civilisation: {civ_total:3} | moral*: {mor_total:3}")

# 控制台输出总和验证
total_civ = sum(r[1] for r in results)
total_mor = sum(r[2] for r in results)
print("-" * 60)
print(f"{'总和':20} | civilisation: {total_civ:3} | moral*: {total_mor:3}")

# ========== 导出 CSV ==========
csv_path = os.path.join(output_dir, "chapter_stats.csv")
with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(["Chapter", "civilisation", "moral*"])
    for name, civ, mor in results:
        writer.writerow([name, civ, mor])
    writer.writerow(["Total", total_civ, total_mor])
print(f"\nCSV 表格已保存至: {csv_path}")

# ========== 导出 Markdown 表格 ==========
md_path = os.path.join(output_dir, "chapter_stats.md")
with open(md_path, 'w', encoding='utf-8') as f:
    f.write("| Chapter | civilisation | moral* |\n")
    f.write("|---------|--------------|--------|\n")
    for name, civ, mor in results:
        f.write(f"| {name} | {civ} | {mor} |\n")
    f.write(f"| **Total** | **{total_civ}** | **{total_mor}** |\n")
print(f"Markdown 表格已保存至: {md_path}")

# ========== 绘图 ==========
if results:
    names = [r[0] for r in results]
    civ_counts = [r[1] for r in results]
    mor_counts = [r[2] for r in results]
    x = range(len(names))
    width = 0.35
    fig, ax = plt.subplots(figsize=(12, 5))
    bars1 = ax.bar([i - width/2 for i in x], civ_counts, width, label='civilisation', color='steelblue')
    bars2 = ax.bar([i + width/2 for i in x], mor_counts, width, label='moral*', color='coral')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha='right')
    ax.set_ylabel('Frequency')
    ax.set_title('Keyword Frequency by Chapter (from LaTeX source)')
    ax.legend()
    # 在柱子上显示数值
    for bar in bars1 + bars2:
        height = bar.get_height()
        if height > 0:
            ax.annotate(f'{int(height)}',
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=8)
    plt.tight_layout()
    png_path = os.path.join(output_dir, "chapter_stats_latex.png")
    plt.savefig(png_path, dpi=150)
    plt.show()
    print(f"柱状图已保存至: {png_path}")
else:
    print("没有成功读取任何文件，请检查路径和文件名。")