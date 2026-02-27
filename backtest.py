import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import pandas as pd
import numpy as np
import os
import seaborn as sns

save_dir = os.path.dirname(os.path.abspath(__file__))
font = FontProperties(fname='/System/Library/Fonts/Supplemental/Songti.ttc')
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

close_data = pd.DataFrame()
volume_data = pd.DataFrame()
for t in tickers:
    df = pd.read_csv(os.path.join(save_dir, f"{t}.csv"), header=[0, 1], index_col=0, parse_dates=True).dropna()
    close_data[t] = df[('Close', t)]
    volume_data[t] = df[('Volume', t)]

daily_returns = close_data.pct_change().dropna()
cumulative_returns = (1 + daily_returns).cumprod() - 1
rolling_vol = daily_returns.rolling(window=30).std() * np.sqrt(252)

drawdowns = pd.DataFrame()
for t in tickers:
    peak = close_data[t].cummax()
    drawdowns[t] = (close_data[t] - peak) / peak

trading_days = len(daily_returns)
annual_returns = (close_data.iloc[-1] / close_data.iloc[0]) ** (252 / trading_days) - 1
annual_vol = daily_returns.std() * np.sqrt(252)
sharpe = annual_returns / annual_vol
corr = daily_returns.corr()

txt = []

def save_fig(fig, num, name):
    fig.savefig(os.path.join(save_dir, f"图{num}_{name}.png"), dpi=150, bbox_inches='tight')
    plt.close(fig)

fig, ax = plt.subplots(figsize=(12, 6))
for t in tickers:
    ax.plot(close_data.index, close_data[t], label=t)
ax.set_title('收盘价走势', fontproperties=font, fontsize=14)
ax.set_xlabel('日期', fontproperties=font)
ax.set_ylabel('价格 (USD)', fontproperties=font)
ax.legend()
ax.grid(True, alpha=0.3)
save_fig(fig, 1, '收盘价走势')
txt.append("=" * 60)
txt.append("图1_收盘价走势")
txt.append("=" * 60)
for t in tickers:
    txt.append(f"{t}: 起始价={close_data[t].iloc[0]:.2f}, 最终价={close_data[t].iloc[-1]:.2f}, 最高价={close_data[t].max():.2f}, 最低价={close_data[t].min():.2f}")

fig, ax = plt.subplots(figsize=(12, 6))
for t in tickers:
    ax.plot(cumulative_returns.index, cumulative_returns[t] * 100, label=t)
ax.set_title('累计收益率', fontproperties=font, fontsize=14)
ax.set_xlabel('日期', fontproperties=font)
ax.set_ylabel('累计收益率 (%)', fontproperties=font)
ax.legend()
ax.grid(True, alpha=0.3)
save_fig(fig, 2, '累计收益率')
txt.append("")
txt.append("=" * 60)
txt.append("图2_累计收益率")
txt.append("=" * 60)
for t in tickers:
    txt.append(f"{t}: 最终={cumulative_returns[t].iloc[-1]*100:.2f}%, 最高={cumulative_returns[t].max()*100:.2f}%, 最低={cumulative_returns[t].min()*100:.2f}%")

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()
for i, t in enumerate(tickers):
    axes[i].hist(daily_returns[t], bins=50, alpha=0.7, edgecolor='black')
    axes[i].set_title(f'{t}', fontsize=11)
    axes[i].set_xlabel('收益率', fontproperties=font)
    axes[i].set_ylabel('频次', fontproperties=font)
axes[-1].set_visible(False)
fig.suptitle('每日收益率分布', fontproperties=font, fontsize=14)
fig.tight_layout()
save_fig(fig, 3, '每日收益率分布')
txt.append("")
txt.append("=" * 60)
txt.append("图3_每日收益率分布")
txt.append("=" * 60)
for t in tickers:
    txt.append(f"{t}: 均值={daily_returns[t].mean()*100:.4f}%, 标准差={daily_returns[t].std()*100:.4f}%, 偏度={daily_returns[t].skew():.4f}, 峰度={daily_returns[t].kurtosis():.4f}")

fig, ax = plt.subplots(figsize=(12, 6))
for t in tickers:
    ax.plot(rolling_vol.index, rolling_vol[t] * 100, label=t)
ax.set_title('30日滚动年化波动率', fontproperties=font, fontsize=14)
ax.set_xlabel('日期', fontproperties=font)
ax.set_ylabel('波动率 (%)', fontproperties=font)
ax.legend()
ax.grid(True, alpha=0.3)
save_fig(fig, 4, '滚动波动率')
txt.append("")
txt.append("=" * 60)
txt.append("图4_30日滚动年化波动率")
txt.append("=" * 60)
for t in tickers:
    rv = rolling_vol[t].dropna()
    txt.append(f"{t}: 均值={rv.mean()*100:.2f}%, 最高={rv.max()*100:.2f}%, 最低={rv.min()*100:.2f}%")

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(corr, annot=True, fmt='.3f', cmap='RdYlGn', ax=ax, vmin=-1, vmax=1)
ax.set_title('收益率相关性热力图', fontproperties=font, fontsize=14)
fig.tight_layout()
save_fig(fig, 5, '相关性热力图')
txt.append("")
txt.append("=" * 60)
txt.append("图5_收益率相关性热力图")
txt.append("=" * 60)
for i in range(len(tickers)):
    for j in range(i + 1, len(tickers)):
        txt.append(f"{tickers[i]}-{tickers[j]}: {corr.iloc[i, j]:.4f}")

fig, ax = plt.subplots(figsize=(12, 6))
for t in tickers:
    ax.plot(drawdowns.index, drawdowns[t] * 100, label=t)
ax.set_title('最大回撤', fontproperties=font, fontsize=14)
ax.set_xlabel('日期', fontproperties=font)
ax.set_ylabel('回撤 (%)', fontproperties=font)
ax.legend()
ax.grid(True, alpha=0.3)
save_fig(fig, 6, '最大回撤')
txt.append("")
txt.append("=" * 60)
txt.append("图6_最大回撤")
txt.append("=" * 60)
for t in tickers:
    txt.append(f"{t}: 最大回撤={drawdowns[t].min()*100:.2f}%, 日期={drawdowns[t].idxmin().strftime('%Y-%m-%d')}")

fig, ax = plt.subplots(figsize=(10, 7))
for t in tickers:
    ax.scatter(annual_vol[t] * 100, annual_returns[t] * 100, s=100, zorder=5)
    ax.annotate(t, (annual_vol[t] * 100, annual_returns[t] * 100), fontsize=12, ha='left', va='bottom')
ax.set_title('风险收益散点图', fontproperties=font, fontsize=14)
ax.set_xlabel('年化波动率 (%)', fontproperties=font)
ax.set_ylabel('年化收益率 (%)', fontproperties=font)
ax.grid(True, alpha=0.3)
save_fig(fig, 7, '风险收益散点图')
txt.append("")
txt.append("=" * 60)
txt.append("图7_风险收益散点图")
txt.append("=" * 60)
for t in tickers:
    txt.append(f"{t}: 年化收益率={annual_returns[t]*100:.2f}%, 年化波动率={annual_vol[t]*100:.2f}%, 夏普比率={sharpe[t]:.4f}")

txt.append("")
txt.append("=" * 60)
txt.append("回测汇总")
txt.append("=" * 60)
txt.append(f"回测区间: {close_data.index[0].strftime('%Y-%m-%d')} ~ {close_data.index[-1].strftime('%Y-%m-%d')}")
txt.append(f"交易日数: {trading_days}")
for t in tickers:
    txt.append(f"\n{t}:")
    txt.append(f"  总收益率: {(close_data[t].iloc[-1]/close_data[t].iloc[0]-1)*100:.2f}%")
    txt.append(f"  年化收益率: {annual_returns[t]*100:.2f}%")
    txt.append(f"  年化波动率: {annual_vol[t]*100:.2f}%")
    txt.append(f"  夏普比率: {sharpe[t]:.4f}")
    txt.append(f"  最大回撤: {drawdowns[t].min()*100:.2f}%")

with open(os.path.join(save_dir, '图表详情汇总.txt'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(txt))
