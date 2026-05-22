import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# 数据
chapters = ['Preface', 'Introduction', 'Ch1', 'Ch2', 'Ch3', 'Ch4', 'Ch5', 'Ch6', 'Ch7', 'Appendix']
civ = [52, 27, 54, 13, 7, 0, 0, 0, 1, 7]
moral = [19, 16, 133, 8, 0, 0, 8, 0, 4, 1]

# 1. 折线图
plt.figure(figsize=(10,5))
plt.plot(chapters, civ, marker='o', linewidth=2, label='civilisation')
plt.plot(chapters, moral, marker='s', linewidth=2, label='moral word family')
plt.xticks(rotation=45, ha='right')
plt.ylabel('Frequency')
plt.title('Trend of keyword frequencies across chapters')
plt.legend()
plt.tight_layout()
plt.savefig('line_chart.png', dpi=150)
plt.close()

# 2. 堆积柱状图
plt.figure(figsize=(10,5))
plt.bar(chapters, civ, label='civilisation', color='steelblue')
plt.bar(chapters, moral, bottom=civ, label='moral', color='coral')
plt.xticks(rotation=45, ha='right')
plt.ylabel('Frequency')
plt.title('Stacked frequency per chapter')
plt.legend()
plt.tight_layout()
plt.savefig('stacked_bar.png', dpi=150)
plt.close()

# 3. 热力图
df = pd.DataFrame({'civilisation': civ, 'moral': moral}, index=chapters)
plt.figure(figsize=(8,6))
sns.heatmap(df, annot=True, fmt='d', cmap='coolwarm', linewidths=.5)
plt.title('Heatmap of keyword frequencies')
plt.tight_layout()
plt.savefig('heatmap.png', dpi=150)
plt.close()

# 4. 归一化百分比堆积柱状图（修复除零问题）
total = np.array(civ) + np.array(moral)
# 忽略除零警告，计算百分比
with np.errstate(divide='ignore', invalid='ignore'):
    civ_pct = 100 * np.array(civ) / total
    moral_pct = 100 * np.array(moral) / total
# 将 NaN（除以零的结果）替换为 0
civ_pct = np.nan_to_num(civ_pct)
moral_pct = np.nan_to_num(moral_pct)

plt.figure(figsize=(10,5))
plt.bar(chapters, civ_pct, label='civilisation %', color='steelblue')
plt.bar(chapters, moral_pct, bottom=civ_pct, label='moral %', color='coral')
plt.xticks(rotation=45, ha='right')
plt.ylabel('Percentage (%)')
plt.title('Relative proportion of civilisation vs moral per chapter')
plt.legend()
plt.tight_layout()
plt.savefig('percentage_stack.png', dpi=150)
plt.close()

# 5. 集中度饼图（第一章 vs 其余章节）
ch1_civ = civ[2]      # Chapter 1 的 civilisation 次数
ch1_moral = moral[2]  # Chapter 1 的 moral 次数
other_civ = sum(civ) - ch1_civ
other_moral = sum(moral) - ch1_moral

labels = ['Ch1 civilisation', 'Other chapters civilisation', 'Ch1 moral', 'Other chapters moral']
values = [ch1_civ, other_civ, ch1_moral, other_moral]
plt.figure(figsize=(6,6))
plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
plt.title('Concentration of keywords in Chapter 1 vs the rest')
plt.tight_layout()
plt.savefig('concentration_pie.png', dpi=150)
plt.close()

print("所有图表已生成！")