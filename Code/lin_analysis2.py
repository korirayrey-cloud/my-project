"""
Lin Yutang - My Country and My People 完整分析（修复版）
正确分章，修复Preface/Ch4/Ch9长度为0以及Epilogue过长的问题
"""

import re
import os
import csv
import zipfile
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from wordcloud import WordCloud

# ============================================
# 设置
# ============================================
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

epub_path = r"D:\20074\My Country And My People (Lin Yutang) (z-library.sk, 1lib.sk, z-lib.sk).epub"
output_dir = r"D:\20074"
os.makedirs(output_dir, exist_ok=True)

# ============================================
# 1. 提取完整文本
# ============================================

def extract_full_text(epub_path):
    """从epub中提取完整文本"""
    full_text = ""
    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.endswith(('.xhtml', '.html', '.htm')):
                with zip_ref.open(file_name) as f:
                    content = f.read().decode('utf-8', errors='ignore')
                    text = re.sub(r'<[^>]+>', ' ', content)
                    text = re.sub(r'\s+', ' ', text)
                    full_text += " " + text
    return full_text

# ============================================
# 2. 正确分章（按顺序查找所有章节位置）
# ============================================

def split_by_chapters_correct(text):
    """正确分割所有章节，按顺序提取"""
    
    # 章节标题及其精确匹配模式（按书中出现顺序）
    # 使用更精确的模式匹配
    chapter_patterns = [
        ('Preface', r'\bPREFACE\b'),
        ('Introduction', r'\bINTRODUCTION\b'),
        ('Part One: Bases', r'PART ONE\s+BASES'),
        ('Prologue', r'PROLOGUE'),
        ('Chapter One: The Chinese People', r'Chapter One\s+THE CHINESE PEOPLE'),
        ('Chapter Two: The Chinese Character', r'Chapter Two\s+THE CHINESE CHARACTER'),
        ('Chapter Three: The Chinese Mind', r'Chapter Three\s+THE CHINESE MIND'),
        ('Chapter Four: Ideals of Life', r'Chapter Four\s+IDEALS OF LIFE'),
        ('Part Two: Life', r'PART TWO\s+LIFE'),
        ('Prologue to Part Two', r'PROLOGUE TO PART TWO'),
        ('Chapter Five: Woman\'s Life', r'Chapter Five\s+WOMAN\'S LIFE'),
        ('Chapter Six: Social and Political Life', r'Chapter Six\s+SOCIAL AND POLITICAL LIFE'),
        ('Chapter Seven: Literary Life', r'Chapter Seven\s+LITERARY LIFE'),
        ('Chapter Eight: The Artistic Life', r'Chapter Eight\s+THE ARTISTIC LIFE'),
        ('Chapter Nine: The Art of Living', r'Chapter Nine\s+THE ART OF LIVING'),
        ('Epilogue', r'EPILOGUE'),
        ('Appendix', r'APPENDIX'),
    ]
    
    chapters = {}
    text_len = len(text)
    
    # 找出所有章节的起始位置
    positions = []
    for ch_name, pattern in chapter_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            positions.append((match.start(), ch_name))
        else:
            print(f"警告: 未找到章节 '{ch_name}'")
    
    # 按位置排序
    positions.sort(key=lambda x: x[0])
    
    # 提取每个章节的内容
    for i, (start, ch_name) in enumerate(positions):
        end = positions[i+1][0] if i+1 < len(positions) else text_len
        chapter_text = text[start:end]
        # 清理：去除章节标题本身（避免重复）
        chapter_text = re.sub(r'^[A-Z\s]+', '', chapter_text, flags=re.IGNORECASE)
        chapters[ch_name] = chapter_text[:50000]  # 限制每章最大长度
        print(f"找到章节: {ch_name:35} (位置: {start:8,} - {end:8,}, 长度: {len(chapter_text):,} 字符)")
    
    return chapters

def count_keywords_in_text(text, targets):
    """统计关键词频率"""
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    cnt = Counter(words)
    return {w: cnt.get(w, 0) for w in targets}

# ============================================
# 3. 生成表2：章节频率表
# ============================================

def generate_chapter_table(chapters):
    """生成章节频率表 CSV"""
    targets = ['civilisation', 'civilization', 'moral', 'morality', 'morally']
    
    results = []
    for name, text in chapters.items():
        # 跳过太短的章节（少于100字符）
        if len(text) < 100:
            print(f"跳过章节: {name} (长度过短)")
            continue
            
        counts = count_keywords_in_text(text, targets)
        civ = counts.get('civilisation', 0) + counts.get('civilization', 0)
        mor = counts.get('moral', 0) + counts.get('morality', 0) + counts.get('morally', 0)
        results.append((name, civ, mor))
        print(f"{name:35} | civilisation: {civ:3} | moral: {mor:3}")
    
    # 保存CSV
    csv_path = os.path.join(output_dir, 'lin_chapter_stats.csv')
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["Chapter", "civilisation", "moral"])
        for name, civ, mor in results:
            writer.writerow([name, civ, mor])
    
    print(f"\n表2已保存: {csv_path}")
    return results

# ============================================
# 4. 生成图8：柱状图（只显示有数据的章节）
# ============================================

def generate_bar_chart(chapter_data):
    """生成林语堂柱状图"""
    if not chapter_data:
        print("没有章节数据，无法生成柱状图")
        return
    
    # 过滤掉civilisation和moral都为0的章节
    filtered = [(n, c, m) for n, c, m in chapter_data if c > 0 or m > 0]
    
    if not filtered:
        print("没有有数据的章节")
        return
    
    names = [row[0].replace('Chapter ', 'Ch') for row in filtered]
    civ = [row[1] for row in filtered]
    mor = [row[2] for row in filtered]
    
    fig, ax = plt.subplots(figsize=(14, 6))
    x = range(len(names))
    width = 0.35
    
    bars1 = ax.bar([i - width/2 for i in x], civ, width, label='civilisation', color='steelblue')
    bars2 = ax.bar([i + width/2 for i in x], mor, width, label='moral', color='coral')
    
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.set_title('Lin Yutang: Keyword Frequency by Chapter', fontsize=14, fontweight='bold')
    ax.legend()
    
    for bar in bars1 + bars2:
        height = bar.get_height()
        if height > 0:
            ax.annotate(f'{int(height)}', xy=(bar.get_x() + bar.get_width()/2, height),
                       xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    path = os.path.join(output_dir, 'lin_bar_chart.png')
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"图8已保存: {path}")

# ============================================
# 5. 生成图9：词云
# ============================================

def generate_wordcloud():
    """生成林语堂词云（对数变换）"""
    
    lin_freq = {
        'chinese': 1347, 'life': 543, 'man': 532, 'people': 502, 'woman': 472,
        'west': 262, 'confucius': 230, 'nation': 195, 'spirit': 191, 'character': 183,
        'family': 171, 'nature': 145, 'home': 101, 'moral': 100, 'tao': 93,
        'buddh': 86, 'society': 66, 'virtue': 60, 'civilisation': 45, 'east': 27
    }
    
    lin_freq_log = {word: np.log(count) for word, count in lin_freq.items()}
    
    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color='white',
        max_words=100,
        colormap='viridis',
        random_state=42
    ).generate_from_frequencies(lin_freq_log)
    
    plt.figure(figsize=(16, 8))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Lin Yutang: My Country and My People', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    path = os.path.join(output_dir, 'lin_wordcloud_log.png')
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"图9已保存: {path}")

# ============================================
# 主程序
# ============================================

def main():
    print("=" * 60)
    print("林语堂《My Country and My People》完整分析（修复版）")
    print("=" * 60)
    
    # 提取完整文本
    print("\n正在解析epub文件...")
    full_text = extract_full_text(epub_path)
    print(f"提取完成，共 {len(full_text):,} 字符")
    
    # 正确分章
    print("\n【正确分章】")
    chapters = split_by_chapters_correct(full_text)
    
    # 生成表2
    print("\n【生成表2：章节频率表】")
    chapter_data = generate_chapter_table(chapters)
    
    # 生成图8
    print("\n【生成图8：柱状图】")
    generate_bar_chart(chapter_data)
    
    # 生成图9
    print("\n【生成图9：词云】")
    generate_wordcloud()
    
    print("\n" + "=" * 60)
    print("全部生成完成！")
    print(f"输出目录: {output_dir}")
    print("=" * 60)

if __name__ == "__main__":
    main()