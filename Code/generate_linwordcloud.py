"""
生成林语堂词云 - 风格与辜鸿铭词云完全一致
"""

import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

# 输出路径
output_path = r"D:\20074\lin_wordcloud.png"

# 林语堂词频数据（从epub运行结果）
lin_freq = {
    'chinese': 1347, 'life': 543, 'man': 532, 'people': 502, 'woman': 472,
    'west': 262, 'confucius': 230, 'nation': 195, 'spirit': 191, 'character': 183,
    'family': 171, 'nature': 145, 'home': 101, 'moral': 100, 'tao': 93,
    'buddh': 86, 'society': 66, 'virtue': 60, 'civilisation': 45, 'east': 27
}

# 使用与辜鸿铭完全相同的词云参数
wordcloud = WordCloud(
    width=800,
    height=400,
    background_color='white',
    max_words=200,
    colormap='viridis'  # 与辜鸿铭相同
).generate_from_frequencies(lin_freq)

plt.figure(figsize=(12, 6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title("My Country and My People - Word Cloud (Lin Yutang)", fontsize=16)
plt.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close()

print(f"林语堂词云图已保存至: {output_path}")