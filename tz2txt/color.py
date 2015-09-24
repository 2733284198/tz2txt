# coding=utf-8

try:
    import colorama
except:
    colorama = None

if colorama:
    Fore = colorama.Fore
    Style = colorama.Style
else:
    class Fore:
        BLACK = None
        RED = None
        GREEN = None
        YELLOW = None
        BLUE = None
        MAGENTA = None
        CYAN = None
        WHITE = None
        RESET = None
        
def disable():
    global colorama
    colorama = None

# 参数：原始内容，颜色（如color.Fore.RED），高亮
def fore_color(raw, color, bright=True):
    if not colorama:
        return str(raw)

    if bright:
        return colorama.Style.BRIGHT + color + \
            str(raw) + \
            colorama.Fore.RESET + colorama.Style.RESET_ALL

    return color + str(raw) + colorama.Fore.RESET

# 初始化
def init():
    if colorama:
        colorama.init()

# 恢复stdout和stderr
def deinit():
    if colorama:
        colorama.deinit()