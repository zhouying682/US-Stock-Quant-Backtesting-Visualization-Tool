import os
os.environ['CURL_CA_BUNDLE'] = ''

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.font_manager import FontProperties
import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns
import threading

font = FontProperties(fname='/System/Library/Fonts/Supplemental/Songti.ttc')

CHART_TABS = ['收盘价走势', '累计收益率', '最大回撤', '滚动波动率',
              '收益率分布', '相关性热力图', '风险收益散点图', '均线与布林带', 'Beta与Alpha']


class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title('股票可视化对比工具')
        self.root.geometry('1400x900')

        top = ttk.Frame(root, padding=10)
        top.pack(fill=tk.X)

        ttk.Label(top, text='股票代码 (逗号分隔):').pack(side=tk.LEFT)
        self.ticker_entry = ttk.Entry(top, width=35)
        self.ticker_entry.pack(side=tk.LEFT, padx=5)
        self.ticker_entry.insert(0, 'AAPL, MSFT, GOOGL')

        ttk.Label(top, text='基准:').pack(side=tk.LEFT, padx=(10, 0))
        self.bench_entry = ttk.Entry(top, width=8)
        self.bench_entry.pack(side=tk.LEFT, padx=3)
        self.bench_entry.insert(0, 'SPY')

        ttk.Label(top, text='开始:').pack(side=tk.LEFT, padx=(10, 0))
        self.start_entry = ttk.Entry(top, width=12)
        self.start_entry.pack(side=tk.LEFT, padx=3)
        self.start_entry.insert(0, (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d'))

        ttk.Label(top, text='结束:').pack(side=tk.LEFT, padx=(10, 0))
        self.end_entry = ttk.Entry(top, width=12)
        self.end_entry.pack(side=tk.LEFT, padx=3)
        self.end_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))

        self.btn = ttk.Button(top, text='开始分析', command=self.run)
        self.btn.pack(side=tk.LEFT, padx=15)

        self.status = ttk.Label(top, text='')
        self.status.pack(side=tk.LEFT, padx=10)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        self.figures = {}
        self.canvases = {}
        for name in CHART_TABS:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=name)
            fig = plt.Figure(figsize=(12, 5.5), dpi=100)
            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            self.figures[name] = fig
            self.canvases[name] = canvas

        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text='指标面板')
        cols = ('股票', '总收益率%', '年化收益率%', '年化波动率%', '夏普比率',
                '索提诺比率', 'Calmar比率', '最大回撤%', '最大回撤日期',
                'VaR(95%)%', 'CVaR(95%)%', 'Beta', 'Alpha%')
        self.tree = ttk.Treeview(stats_frame, columns=cols, show='headings', height=15)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=95, anchor=tk.CENTER)
        self.tree.column('股票', width=70)
        self.tree.column('最大回撤日期', width=110)
        scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def run(self):
        raw = self.ticker_entry.get().strip()
        tickers = [t.strip().upper() for t in raw.replace('，', ',').split(',') if t.strip()]
        bench = self.bench_entry.get().strip().upper()
        start = self.start_entry.get().strip()
        end = self.end_entry.get().strip()
        if not tickers:
            messagebox.showerror('错误', '请输入股票代码')
            return
        try:
            datetime.strptime(start, '%Y-%m-%d')
            datetime.strptime(end, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror('错误', '日期格式应为 YYYY-MM-DD')
            return
        self.btn.config(state='disabled')
        self.status.config(text='正在获取数据...')
        threading.Thread(target=self._fetch, args=(tickers, bench, start, end), daemon=True).start()

    def _fetch(self, tickers, bench, start, end):
        try:
            all_tickers = tickers + [bench]
            close_data = pd.DataFrame()
            volume_data = pd.DataFrame()
            high_data = pd.DataFrame()
            low_data = pd.DataFrame()
            failed = []
            for t in all_tickers:
                df = yf.download(t, start=start, end=end, progress=False)
                if df.empty:
                    failed.append(t)
                    continue
                if isinstance(df.columns, pd.MultiIndex):
                    close_data[t] = df[('Close', t)]
                    volume_data[t] = df[('Volume', t)]
                    high_data[t] = df[('High', t)]
                    low_data[t] = df[('Low', t)]
                else:
                    close_data[t] = df['Close']
                    volume_data[t] = df['Volume']
                    high_data[t] = df['High']
                    low_data[t] = df['Low']
            if close_data.empty or not any(t in close_data.columns for t in tickers):
                self.root.after(0, lambda: messagebox.showerror('错误', '股票数据获取失败'))
                return
            close_data = close_data.dropna()
            high_data = high_data.reindex(close_data.index).dropna()
            low_data = low_data.reindex(close_data.index).dropna()
            volume_data = volume_data.reindex(close_data.index).dropna()
            stock_cols = [t for t in tickers if t in close_data.columns]
            has_bench = bench in close_data.columns
            daily_returns = close_data.pct_change().dropna()
            cum_ret = (1 + daily_returns).cumprod() - 1
            roll_vol = daily_returns[stock_cols].rolling(window=30).std() * np.sqrt(252)
            corr = daily_returns[stock_cols].corr()

            drawdowns = pd.DataFrame()
            for t in stock_cols:
                peak = close_data[t].cummax()
                drawdowns[t] = (close_data[t] - peak) / peak

            trading_days = len(daily_returns)
            stats = {}
            for t in stock_cols:
                ret_t = daily_returns[t]
                total_ret = close_data[t].iloc[-1] / close_data[t].iloc[0] - 1
                ann_ret = (1 + total_ret) ** (252 / trading_days) - 1
                ann_vol = ret_t.std() * np.sqrt(252)
                sharpe = ann_ret / ann_vol if ann_vol != 0 else 0
                downside = ret_t[ret_t < 0].std() * np.sqrt(252)
                sortino = ann_ret / downside if downside != 0 else 0
                max_dd = drawdowns[t].min()
                max_dd_date = drawdowns[t].idxmin().strftime('%Y-%m-%d')
                calmar = ann_ret / abs(max_dd) if max_dd != 0 else 0
                var_95 = np.percentile(ret_t, 5)
                cvar_95 = ret_t[ret_t <= var_95].mean()
                beta, alpha = 0.0, 0.0
                if has_bench:
                    cov = np.cov(ret_t, daily_returns[bench])
                    beta = cov[0, 1] / cov[1, 1] if cov[1, 1] != 0 else 0
                    bench_ann = (1 + (close_data[bench].iloc[-1] / close_data[bench].iloc[0] - 1)) ** (252 / trading_days) - 1
                    alpha = ann_ret - beta * bench_ann
                stats[t] = {
                    'total_ret': total_ret, 'ann_ret': ann_ret, 'ann_vol': ann_vol,
                    'sharpe': sharpe, 'sortino': sortino, 'calmar': calmar,
                    'max_dd': max_dd, 'max_dd_date': max_dd_date,
                    'var95': var_95, 'cvar95': cvar_95,
                    'beta': beta, 'alpha': alpha
                }

            data = {
                'close': close_data, 'high': high_data, 'low': low_data,
                'volume': volume_data, 'daily_returns': daily_returns,
                'cum_ret': cum_ret, 'roll_vol': roll_vol, 'corr': corr,
                'drawdowns': drawdowns, 'stats': stats,
                'stock_cols': stock_cols, 'bench': bench,
                'has_bench': has_bench, 'failed': failed
            }
            self.root.after(0, lambda: self._plot(data))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror('错误', str(e)))
        finally:
            self.root.after(0, lambda: self.btn.config(state='normal'))

    def _plot(self, d):
        close = d['close']
        stock_cols = d['stock_cols']
        cum_ret = d['cum_ret']
        roll_vol = d['roll_vol']
        corr = d['corr']
        drawdowns = d['drawdowns']
        stats = d['stats']
        daily_returns = d['daily_returns']
        bench = d['bench']
        has_bench = d['has_bench']

        fig = self.figures['收盘价走势']
        fig.clear()
        ax = fig.add_subplot(111)
        for t in stock_cols:
            ax.plot(close.index, close[t], label=t)
        if has_bench:
            ax.plot(close.index, close[bench], label=bench, linestyle='--', color='gray', alpha=0.7)
        ax.set_title('收盘价走势', fontproperties=font, fontsize=14)
        ax.set_xlabel('日期', fontproperties=font)
        ax.set_ylabel('价格 (USD)', fontproperties=font)
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        self.canvases['收盘价走势'].draw()

        fig = self.figures['累计收益率']
        fig.clear()
        ax = fig.add_subplot(111)
        for t in stock_cols:
            ax.plot(cum_ret.index, cum_ret[t] * 100, label=t)
        if has_bench:
            ax.plot(cum_ret.index, cum_ret[bench] * 100, label=bench, linestyle='--', color='gray', alpha=0.7)
        ax.set_title('累计收益率', fontproperties=font, fontsize=14)
        ax.set_xlabel('日期', fontproperties=font)
        ax.set_ylabel('累计收益率 (%)', fontproperties=font)
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        self.canvases['累计收益率'].draw()

        fig = self.figures['最大回撤']
        fig.clear()
        ax = fig.add_subplot(111)
        for t in stock_cols:
            ax.plot(drawdowns.index, drawdowns[t] * 100, label=t)
        ax.set_title('最大回撤', fontproperties=font, fontsize=14)
        ax.set_xlabel('日期', fontproperties=font)
        ax.set_ylabel('回撤 (%)', fontproperties=font)
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        self.canvases['最大回撤'].draw()

        fig = self.figures['滚动波动率']
        fig.clear()
        ax = fig.add_subplot(111)
        for t in stock_cols:
            ax.plot(roll_vol.index, roll_vol[t] * 100, label=t)
        ax.set_title('30日滚动年化波动率', fontproperties=font, fontsize=14)
        ax.set_xlabel('日期', fontproperties=font)
        ax.set_ylabel('波动率 (%)', fontproperties=font)
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        self.canvases['滚动波动率'].draw()

        fig = self.figures['收益率分布']
        fig.clear()
        n = len(stock_cols)
        ncols = min(n, 3)
        nrows = (n + ncols - 1) // ncols
        for i, t in enumerate(stock_cols):
            ax = fig.add_subplot(nrows, ncols, i + 1)
            ret = daily_returns[t]
            ax.hist(ret, bins=50, alpha=0.7, edgecolor='black', density=True)
            x = np.linspace(ret.min(), ret.max(), 200)
            ax.plot(x, (1 / (ret.std() * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - ret.mean()) / ret.std()) ** 2),
                    'r-', linewidth=1.5)
            ax.set_title(f'{t}', fontsize=11)
            ax.set_xlabel('收益率', fontproperties=font, fontsize=9)
            ax.axvline(np.percentile(ret, 5), color='orange', linestyle='--', linewidth=1)
        fig.suptitle('每日收益率分布 (橙线=VaR 95%)', fontproperties=font, fontsize=13)
        fig.tight_layout()
        self.canvases['收益率分布'].draw()

        fig = self.figures['相关性热力图']
        fig.clear()
        ax = fig.add_subplot(111)
        sns.heatmap(corr, annot=True, fmt='.3f', cmap='RdYlGn', ax=ax, vmin=-1, vmax=1)
        ax.set_title('收益率相关性热力图', fontproperties=font, fontsize=14)
        fig.tight_layout()
        self.canvases['相关性热力图'].draw()

        fig = self.figures['风险收益散点图']
        fig.clear()
        ax = fig.add_subplot(111)
        colors = plt.cm.tab10(np.linspace(0, 1, len(stock_cols)))
        for i, t in enumerate(stock_cols):
            s = stats[t]
            ax.scatter(s['ann_vol'] * 100, s['ann_ret'] * 100, s=120, color=colors[i], zorder=5)
            ax.annotate(t, (s['ann_vol'] * 100, s['ann_ret'] * 100), fontsize=11,
                        xytext=(8, 5), textcoords='offset points')
        if has_bench:
            b_ret = (close[bench].iloc[-1] / close[bench].iloc[0] - 1)
            b_ann = (1 + b_ret) ** (252 / len(daily_returns)) - 1
            b_vol = daily_returns[bench].std() * np.sqrt(252)
            ax.scatter(b_vol * 100, b_ann * 100, s=120, marker='D', color='gray', zorder=5)
            ax.annotate(bench, (b_vol * 100, b_ann * 100), fontsize=11,
                        xytext=(8, 5), textcoords='offset points')
        ax.set_title('风险收益散点图', fontproperties=font, fontsize=14)
        ax.set_xlabel('年化波动率 (%)', fontproperties=font)
        ax.set_ylabel('年化收益率 (%)', fontproperties=font)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        self.canvases['风险收益散点图'].draw()

        fig = self.figures['均线与布林带']
        fig.clear()
        n = len(stock_cols)
        ncols = min(n, 2)
        nrows = (n + ncols - 1) // ncols
        for i, t in enumerate(stock_cols):
            ax = fig.add_subplot(nrows, ncols, i + 1)
            c = close[t]
            ma20 = c.rolling(20).mean()
            ma60 = c.rolling(60).mean()
            std20 = c.rolling(20).std()
            upper = ma20 + 2 * std20
            lower = ma20 - 2 * std20
            ax.plot(c.index, c, label='Close', linewidth=0.8)
            ax.plot(c.index, ma20, label='MA20', linewidth=0.8)
            ax.plot(c.index, ma60, label='MA60', linewidth=0.8)
            ax.fill_between(c.index, upper, lower, alpha=0.15, color='blue')
            ax.set_title(f'{t}', fontsize=11)
            ax.legend(fontsize=7)
            ax.grid(True, alpha=0.3)
        fig.suptitle('均线与布林带 (MA20/MA60/BB20)', fontproperties=font, fontsize=13)
        fig.tight_layout()
        self.canvases['均线与布林带'].draw()

        fig = self.figures['Beta与Alpha']
        fig.clear()
        if has_bench and len(stock_cols) > 0:
            ax1 = fig.add_subplot(121)
            betas = [stats[t]['beta'] for t in stock_cols]
            bars1 = ax1.barh(stock_cols, betas, color=plt.cm.tab10(np.linspace(0, 1, len(stock_cols))))
            ax1.axvline(1.0, color='red', linestyle='--', linewidth=1)
            ax1.set_title('Beta (vs ' + bench + ')', fontproperties=font, fontsize=13)
            ax1.set_xlabel('Beta', fontproperties=font)
            for bar, val in zip(bars1, betas):
                ax1.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
                         f'{val:.3f}', va='center', fontsize=10)
            ax1.grid(True, alpha=0.3, axis='x')

            ax2 = fig.add_subplot(122)
            alphas = [stats[t]['alpha'] * 100 for t in stock_cols]
            bars2 = ax2.barh(stock_cols, alphas, color=plt.cm.tab10(np.linspace(0, 1, len(stock_cols))))
            ax2.axvline(0, color='red', linestyle='--', linewidth=1)
            ax2.set_title('Alpha (vs ' + bench + ')', fontproperties=font, fontsize=13)
            ax2.set_xlabel('Alpha (%)', fontproperties=font)
            for bar, val in zip(bars2, alphas):
                ax2.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                         f'{val:.2f}%', va='center', fontsize=10)
            ax2.grid(True, alpha=0.3, axis='x')
        fig.tight_layout()
        self.canvases['Beta与Alpha'].draw()

        for row in self.tree.get_children():
            self.tree.delete(row)
        for t in stock_cols:
            s = stats[t]
            self.tree.insert('', tk.END, values=(
                t,
                f"{s['total_ret']*100:.2f}",
                f"{s['ann_ret']*100:.2f}",
                f"{s['ann_vol']*100:.2f}",
                f"{s['sharpe']:.3f}",
                f"{s['sortino']:.3f}",
                f"{s['calmar']:.3f}",
                f"{s['max_dd']*100:.2f}",
                s['max_dd_date'],
                f"{s['var95']*100:.2f}",
                f"{s['cvar95']*100:.2f}",
                f"{s['beta']:.3f}",
                f"{s['alpha']*100:.2f}"
            ))

        msg = f"获取失败: {', '.join(d['failed'])}" if d['failed'] else ''
        self.status.config(text=f"完成 ({len(stock_cols)}只股票, {len(close)}交易日) {msg}")


if __name__ == '__main__':
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()
