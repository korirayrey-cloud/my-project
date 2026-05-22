"""
Lin Yutang - My Country and My People 文本分析（修复版）
"""

import re
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import zipfile

# ============================================
# 1. 解析EPUB文件
# ============================================

def extract_epub_text(epub_path):
    """从epub文件中提取纯文本"""
    text_content = []
    
    with zipfile.ZipFile(epub_path, 'r') as zip_ref:
        for file_name in zip_ref.namelist():
            if file_name.endswith(('.xhtml', '.html', '.htm')):
                with zip_ref.open(file_name) as f:
                    content = f.read().decode('utf-8', errors='ignore')
                    text = re.sub(r'<[^>]+>', ' ', content)
                    text = re.sub(r'\s+', ' ', text)
                    text_content.append(text)
    
    return ' '.join(text_content)

# ============================================
# 2. 关键词统计
# ============================================

def count_keywords_lin(text):
    """统计林语堂文本中的关键词"""
    
    keywords = {
        'civilisation': r'\bcivilisation\b|\bcivilization\b',
        'moral': r'\bmoral\w*\b',
        'character': r'\bcharacter\w*\b',
        'virtue': r'\bvirtue\w*\b',
        'spirit': r'\bspirit\w*\b',
        'nature': r'\bnature\w*\b',
        'chinese': r'\bchinese\b',
        'people': r'\bpeople\b',
        'nation': r'\bnation\w*\b',
        'west': r'\bwest\w*\b|\bwestern\w*\b',
        'east': r'\beast\w*\b|\beastern\w*\b',
        'confucius': r'\bconfuci\w*\b',
        'tao': r'\btao\w*\b',
        'buddh': r'\bbuddh\w*\b',
        'woman': r'\bwoman\w*\b|\bgirl\w*\b|\bwomen\b',
        'family': r'\bfamily\b',
        'home': r'\bhome\b',
        'man': r'\bman\b|\bmen\b',
        'life': r'\blife\b',
        'society': r'\bsociety\b',
    }
    
    results = {}
    
    for name, pattern in keywords.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        results[name] = len(matches)
        
        # 存储moral上下文
        if name == 'moral':
            contexts = re.finditer(r'\.\s*([^.]*' + pattern + r'[^.]*\.)', text, re.IGNORECASE)
            moral_examples = []
            for i, c in enumerate(contexts):
                if i < 20:
                    moral_examples.append(c.group(1)[:200])
            results['moral_examples'] = moral_examples
    
    return results

# ============================================
# 3. 情感分析
# ============================================

def sentiment_analysis(text):
    """情感倾向分析"""
    positive_words = set([
        'great', 'good', 'beautiful', 'wonderful', 'excellent', 'fine', 'noble',
        'wise', 'virtuous', 'kind', 'gentle', 'peaceful', 'happy', 'content',
        'civilized', 'cultured', 'refined', 'graceful', 'charming', 'admirable',
        'profound', 'deep', 'rich', 'splendid', 'magnificent', 'glorious',
        'lovely', 'delightful', 'pleasant', 'joyful', 'cheerful', 'genial'
    ])
    
    negative_words = set([
        'bad', 'poor', 'terrible', 'awful', 'wretched', 'miserable', 'sad',
        'ignorant', 'backward', 'corrupt', 'decadent', 'degenerate', 'decayed',
        'weak', 'feeble', 'helpless', 'pathetic', 'hopeless', 'chaotic',
        'futile', 'useless', 'vain', 'foolish', 'stupid',
        'selfish', 'greedy', 'cruel', 'harsh', 'brutal', 'savage'
    ])
    
    sentences = re.split(r'[.!?]+', text)
    
    pos_count = 0
    neg_count = 0
    
    for sent in sentences[:5000]:
        sent_lower = sent.lower()
        pos_matches = sum(1 for w in positive_words if w in sent_lower)
        neg_matches = sum(1 for w in negative_words if w in sent_lower)
        
        if pos_matches > neg_matches:
            pos_count += 1
        elif neg_matches > pos_matches:
            neg_count += 1
    
    total = pos_count + neg_count
    if total > 0:
        sentiment_score = (pos_count - neg_count) / total
        pos_ratio = pos_count / total
        neg_ratio = neg_count / total
    else:
        sentiment_score = 0
        pos_ratio = 0
        neg_ratio = 0
    
    return {
        'positive_ratio': pos_ratio,
        'negative_ratio': neg_ratio,
        'sentiment_score': sentiment_score,
        'pos_sentences': pos_count,
        'neg_sentences': neg_count
    }

# ============================================
# 4. 章节分割（基于关键词）
# ============================================

def split_chapters_rough(text):
    """粗略分章，用于热力图"""
    
    # 林语堂书的主要章节标题关键词
    chapter_keywords = [
        ('Preface', 'preface'),
        ('Introduction', 'introduction'),
        ('North_South', 'north and south'),
        ('Degeneration', 'degeneration'),
        ('Infusion', 'infusion of new blood'),
        ('Stability', 'cultural stability'),
        ('Racial_Youth', 'racial youth'),
        ('Mellowness', 'mellowness'),
        ('Patience', 'patience'),
        ('Indifference', 'indifference'),
        ('Old_Roguery', 'old roguery'),
        ('Pacifism', 'pacifism'),
        ('Contentment', 'contentment'),
        ('Humour', 'humour'),
        ('Conservatism', 'conservatism'),
        ('Intelligence', 'intelligence'),
        ('Femininity', 'femininity'),
        ('Lack_Science', 'lack of science'),
        ('Logic', 'logic'),
        ('Intuition', 'intuition'),
        ('Imagination', 'imagination'),
        ('Humanism', 'humanism'),
        ('Religion', 'religion'),
        ('Golden_Mean', 'golden mean'),
        ('Taoism', 'taoism'),
        ('Buddhism', 'buddhism'),
        ('Woman', "woman's life"),
        ('Social_Political', 'social and political'),
        ('Literary', 'literary life'),
        ('Artistic', 'artistic life'),
        ('Art_Living', 'art of living'),
        ('Epilogue', 'epilogue'),
    ]
    
    chapters = {}
    text_lower = text.lower()
    
    for ch_name, keyword in chapter_keywords:
        # 简单统计该章节关键词所在段落
        # 更精确的方法需要解析epub的章节结构，这里先用关键词频率代理
        pattern = r'\.\s*([^.]*' + re.escape(keyword) + r'[^.]*\.)'
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        chapters[ch_name] = len(matches) * 10  # 粗略权重
    
    return chapters

# ============================================
# 5. 生成报告
# ============================================

def generate_report(lin_text):
    """生成完整分析报告"""
    
    print("=" * 60)
    print("林语堂《My Country and My People》文本分析报告")
    print("=" * 60)
    
    # 基本统计
    word_count = len(re.findall(r'\b\w+\b', lin_text))
    char_count = len(lin_text)
    
    print(f"\n【基本统计】")
    print(f"  总字符数: {char_count:,}")
    print(f"  总词数: {word_count:,}")
    
    # 关键词统计
    print(f"\n【关键词频率】")
    results = count_keywords_lin(lin_text)
    
    # 修复：过滤掉示例列表，只显示数字
    for keyword, count in sorted(results.items(), key=lambda x: x[1] if isinstance(x[1], (int, float)) else 0, reverse=True):
        if isinstance(count, (int, float)):
            print(f"  {keyword}: {count}")
    
    # 情感分析
    print(f"\n【情感倾向】")
    sentiment = sentiment_analysis(lin_text)
    print(f"  正面句子比例: {sentiment['positive_ratio']:.2%}")
    print(f"  负面句子比例: {sentiment['negative_ratio']:.2%}")
    print(f"  情感得分 (-1到1): {sentiment['sentiment_score']:.3f}")
    
    # Moral关键词上下文
    if 'moral_examples' in results and results['moral_examples']:
        print(f"\n【Moral关键词上下文示例（前3条）】")
        for i, ctx in enumerate(results['moral_examples'][:3]):
            print(f"  {i+1}. ...{ctx}...")
    
    # 粗略分章
    print(f"\n【章节分布（基于关键词热度）】")
    chapters = split_chapters_rough(lin_text)
    for ch_name, score in sorted(chapters.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {ch_name}: {score}")
    
    return results, sentiment

# ============================================
# 6. 保存结果
# ============================================

def save_results(results, sentiment):
    """保存结果到CSV"""
    # 分离数值和文本
    numeric_results = {k: v for k, v in results.items() if isinstance(v, (int, float))}
    
    df = pd.DataFrame([numeric_results])
    df.to_csv('lin_yutang_results.csv', index=False)
    print("\n数值结果已保存到 lin_yutang_results.csv")
    
    # 保存moral上下文
    if 'moral_examples' in results:
        with open('lin_moral_contexts.txt', 'w', encoding='utf-8') as f:
            for i, ctx in enumerate(results['moral_examples']):
                f.write(f"{i+1}. {ctx}\n\n")
        print("Moral上下文已保存到 lin_moral_contexts.txt")

# ============================================
# 7. 主程序
# ============================================

def main():
    lin_path = r"D:\20074\My Country And My People (Lin Yutang) (z-library.sk, 1lib.sk, z-lib.sk).epub"
    
    print("正在解析林语堂epub文件...")
    
    try:
        lin_text = extract_epub_text(lin_path)
        print(f"解析完成，共提取 {len(lin_text):,} 字符")
        
        results, sentiment = generate_report(lin_text)
        save_results(results, sentiment)
        
        return results, sentiment, lin_text
        
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None

if __name__ == "__main__":
    results, sentiment, text = main()