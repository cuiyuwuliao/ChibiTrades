import matplotlib.pyplot as plt
from matplotlib import rcParams
import mplcursors

# 参数输入：
# lines: 可选参数，要生成的线的条数。一般要同时显示几组数据，就生成几条线，默认1。
#        如果lines为1，data视为一维数组。当lines大于1时，会将data视为二维数组，data中的每一项都是一组待绘制数据。
# data: 数据，必传，是数组或二维数组。
# labels: 可选，如果要画多条曲线对比的话建议给每个曲线起个名字，放在labels数组里
# grid: 可选，是否显示网格，默认否
def draw(data, labels=None, lines=1, xAxis=None, grid=False):
    # 设置一下中文字体，让中文字在图里也能正常显示
    rcParams['font.family'] = 'SimHei'
    if lines < 1:
        lines = 1
    elif lines > 1:
        lines = int(lines)
    
    if not (xAxis and len(xAxis)):
        if lines == 1:
            xAxis = range(len(data))
        else:
            xAxis = range(len(data[0]))
            
    if not (labels and len(labels)):
        labels = range(lines)
    elif len(labels) != lines:
        labels = range(lines)
        
    
    fig = plt.figure(figsize=(15, 6))
    ax = fig.add_subplot(111)
    if lines == 1:
        ax.plot(xAxis, data, lable=labels[0])
    elif lines > 1:
        for i in range(lines):
            arr = data[i]
            ax.plot(xAxis, arr, label=labels[i])
    if grid:
        ax.grid(color='#caf')
    mplcursors.cursor(hover=True).connect("add", lambda sel: sel.annotation.set_text(f"label:{sel.artist.get_label()}\nx:{int(sel.target[0])}\ny:{sel.target[1]}"))
    plt.show()
