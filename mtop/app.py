import curses
import psutil
import time
import click


def draw_bar(stdscr, x, y, value, length, basic=0, warning=70, critical=90, txt=""):
    if len(txt) > length:
        txt = txt[:length]
    else:
        while len(txt) != length:
            txt = ' ' + txt
    stdscr.addstr(x, y, '[', basic)
    y = y + 1
    for pos in range(0, length):
        if txt[pos] == " ":
            if value >= ((100/length) * (int(pos) + 1)):
                val = "|"
            else:
                val = ""
        else:
            val = txt[pos]
        color = curses.color_pair(0)
        if value >= ((100/length) * (int(pos) + 1)):
            color = curses.color_pair(1)
        if value >= warning:
            color = curses.color_pair(2)
        if value >= critical:
            color = curses.color_pair(3)
        stdscr.addstr(x, y, val, color)
        y = y + 1
    stdscr.addstr(x, y, ']', basic)


def formatInterval(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%d:%02d:%02d" % (h, m, s)


def toG(octet):
    giga = round(float(octet) / (1024*1024*1024), 1)
    if giga > 100:
        return "%.0f" % giga
    return "%.1f" % giga


def main(stdscr, size=30):
    size_bar = size
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    # Clear screen
    stdscr.clear()
    running = True
    curses.curs_set(0)

    # This raises ZeroDivisionError when i == 10.
    while running:
        try:
            i = 0
            stdscr.clear()
            for cpu in psutil.cpu_percent(interval=None, percpu=True):
                stdscr.addstr(i, 0, 'Cpu {}'.format(i + 1), curses.color_pair(4))
                if cpu > 50:
                    txt = "%.0f%%" % cpu
                else:
                    txt = ""
                draw_bar(stdscr, i, 10, cpu, size_bar, curses.color_pair(4), txt=txt)
                i = i + 1
            stdscr.addstr(i, 0, 'Mem', curses.color_pair(5))
            draw_bar(stdscr, i, 10, psutil.virtual_memory().percent, size_bar, curses.color_pair(5), txt=toG(psutil.virtual_memory().used) + '/' + toG(psutil.virtual_memory().total) + 'G')
            i = i + 1
            stdscr.addstr(i, 0, 'Swp', curses.color_pair(5))
            draw_bar(stdscr, i, 10, psutil.swap_memory().percent, size_bar, curses.color_pair(5), txt=toG(psutil.swap_memory().used) + '/' + toG(psutil.swap_memory().total) + 'G')
            i = i + 1
            for disk in psutil.disk_partitions():
                stdscr.addstr(i, 0, disk.device[:10], curses.color_pair(6))
                draw_bar(stdscr, i, 10, psutil.disk_usage(disk.mountpoint).percent, size_bar, curses.color_pair(6), txt=toG(psutil.disk_usage(disk.mountpoint).used)+'/'+toG(psutil.disk_usage(disk.mountpoint).total) + 'G')
                i = i + 1
            interval = time.time() - psutil.boot_time()
            stdscr.addstr(i, 0, "Uptime")
            fmt = '{:>' + str(size_bar) + '}'
            stdscr.addstr(i, 10, fmt.format(formatInterval(int(interval))))
            stdscr.refresh()
            time.sleep(1)
        except KeyboardInterrupt:
            running = False

@click.command()
@click.option('--size', default=30, help='size of bar')
def run(size):
    curses.wrapper(main, size)