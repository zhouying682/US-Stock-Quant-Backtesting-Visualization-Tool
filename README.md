# 美股量化回测与可视化分析工具

一个用于美股数据采集、回测分析和可视化对比的Python工具集，支持批量回测和交互式GUI分析。

## 功能特性

- 📊 **数据采集**: 自动爬取Yahoo Finance美股历史行情数据
- 📈 **批量回测**: 支持多只股票同时回测，生成7张专业分析图表
- 🎨 **交互式GUI**: 可视化界面，自由选择股票和时间范围进行对比分析
- 📉 **专业指标**: 计算夏普比率、索提诺比率、Calmar比率、Beta、Alpha等13项量化指标
- 🔥 **多维图表**: 收盘价走势、累计收益率、最大回撤、波动率、相关性热力图、风险收益散点图、均线布林带等

## 安装依赖

```bash
pip3 install yfinance pandas numpy matplotlib seaborn
```

## 文件说明

### fetch_stock_data.py
数据采集脚本，爬取指定股票的历史行情数据并保存为CSV文件。

**使用方法:**
```bash
# macOS需要设置环境变量解决SSL证书问题
CURL_CA_BUNDLE="" python3 fetch_stock_data.py
```

**输出:** 每只股票生成一个CSV文件 (如 `AAPL.csv`)

### backtest.py
批量回测脚本，读取CSV数据，进行买入持有策略回测，生成7张分析图表和汇总报告。

**使用方法:**
```bash
python3 backtest.py
```

**输出:**
- `图1_收盘价走势.png` - 收盘价时间序列
- `图2_累计收益率.png` - 累计收益率曲线
- `图3_每日收益率分布.png` - 收益率分布直方图
- `图4_滚动波动率.png` - 30日滚动年化波动率
- `图5_相关性热力图.png` - 收益率相关性矩阵
- `图6_最大回撤.png` - 回撤曲线
- `图7_风险收益散点图.png` - 风险收益散点图
- `图表详情汇总.txt` - 所有图表的数值详情

### stock_gui.py
交互式GUI工具，支持自由输入股票代码和时间范围，实时获取数据并展示多维度分析。

**使用方法:**
```bash
python3 stock_gui.py
```

**功能:**
- 输入多只股票代码（逗号分隔）
- 选择基准指数（默认SPY）
- 设置时间范围
- 查看10个分析标签页：
  - 收盘价走势
  - 累计收益率
  - 最大回撤
  - 滚动波动率
  - 收益率分布
  - 相关性热力图
  - 风险收益散点图
  - 均线与布林带
  - Beta与Alpha
  - 指标面板（13项量化指标表格）

## 量化指标说明

| 指标 | 说明 |
|------|------|
| 总收益率 | 期末价/期初价 - 1 |
| 年化收益率 | (1+总收益率)^(252/交易日数) - 1 |
| 年化波动率 | 日收益率标准差 × √252 |
| 夏普比率 | 年化收益率 / 年化波动率 |
| 索提诺比率 | 年化收益率 / 下行波动率 |
| Calmar比率 | 年化收益率 / \|最大回撤\| |
| 最大回撤 | 从历史高点到最低点的最大跌幅 |
| VaR(95%) | 日收益率的第5百分位数 |
| CVaR(95%) | 低于VaR的所有日收益率的均值 |
| Beta | Cov(股票收益, 基准收益) / Var(基准收益) |
| Alpha | 年化收益率 - Beta × 基准年化收益率 |

## 示例

### 批量回测示例
```python
# 修改 fetch_stock_data.py 中的股票列表
tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

# 运行数据采集
CURL_CA_BUNDLE="" python3 fetch_stock_data.py

# 运行回测分析
python3 backtest.py
```

### GUI使用示例
1. 启动GUI: `python3 stock_gui.py`
2. 输入股票代码: `AAPL, MSFT, GOOGL`
3. 设置基准: `SPY`
4. 选择时间范围: `2023-01-01` 至 `2024-12-31`
5. 点击"开始分析"
6. 在标签页中查看各种图表和指标

## 注意事项

- macOS系统需要设置 `CURL_CA_BUNDLE=""` 环境变量解决SSL证书问题
- 数据来源为Yahoo Finance，需要网络连接
- 图表使用系统宋体字体，macOS路径为 `/System/Library/Fonts/Supplemental/Songti.ttc`
- Windows系统需要修改字体路径为 `C:\Windows\Fonts\simsun.ttc`

## 技术栈

- Python 3.9+
- yfinance - 数据获取
- pandas - 数据处理
- numpy - 数值计算
- matplotlib - 图表绘制
- seaborn - 热力图
- tkinter - GUI框架

## License

MIT
