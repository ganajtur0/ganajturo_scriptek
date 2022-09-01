import curses

# this is probably a distinguishable name for something
# that has been written a million times
class CurSelect:

    def __init__(self, items, title=None, window=None, pagination=10, char='| ', ret_type="index", highlight=curses.A_STANDOUT):

        # check if we're running in a script
        # in which ncurses hasn't yet been initialized
        if window == None:
            self.auto_init = True
            self.window = self._start_curses()
        else:
            self.window = window
            self.auto_init = False

        # aesthetic -> leading string to menu items
        self.char = char

        # which item we're on with pagination
        self.pag_start = 0

        # keeps track of the cursors position in the visible area
        self.y = 0

        # this one is self-explanatory
        # ^
        # |
        # and this is bad practice but it causes significant increase in LOC
        self.items = items

        # used to use len(items) and even though it runs in O(1)
        # it's probably cleaner this way, and also takes up more memory!
        self.item_count = len(items)

        # what ncurses attribute to use to highlight
        # the currently slected element
        self.highlight = highlight

        # how many elements should be visible at once
        # may not be the best name for it...
        self.pagination = pagination

        # this ones important 'cause it gets returned later on
        self.current_selection = 0

        # "index" or "value"
        # index returns current_selection
        # value returns the element in items idexed by it
        self.ret_type = ret_type

        # title offsets the menu if there is one
        if title:
            self.offset = 3
        else:
            self.offset = 0
        self.title = title

    def _start_curses(self):
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        stdscr.keypad(True)
        curses.curs_set(False)
        return stdscr

    def _end_curses(self):
        self._clear_line(0)
        self._clear()
        curses.curs_set(True)
        curses.nocbreak()
        self.window.keypad(False)
        curses.echo()
        curses.endwin()

    # we want to stop curses when a script finishes
    def __del__(self):
        if self.auto_init:
            self._end_curses()

    def _clear_line(self, line_num):
        self.window.move(line_num, 0)
        self.window.clrtoeol()

    def _display_item(self, index, attr=0):
        if self.pag_start + index > self.item_count-1:
            return
        self.window.addstr(index+self.offset, 0, self.char+self.items[self.pag_start+index], attr)

    def _update(self, direction):
        self._display_item(self.y+direction)
        self._display_item(self.y, self.highlight)
        self.window.refresh()

    def _clear(self):
        for i in range(self.pagination+2):
            self._clear_line(self.offset + i)

    def _display(self):
        for i in range(self.pagination):
            self._display_item(i)
        self._update(0)

    # didn't care about making it "non-blocking" because it seemed redundant
    # and also more confusing to use (plus I am not a smart thread expert)
    def activate(self):

        if self.title:
            self.window.addstr(0, 0, self.title, curses.A_BOLD)

        self._display()

        while True:
            try:
                self.window.addstr(self.pagination+1+self.offset, 0, "=== page "+str(self.current_selection//self.pagination+1)+" ===")
                self.window.addstr(self.pagination+2+self.offset, 0, "=== item "+str(self.current_selection+1)+" ===")
                c = self.window.getch()

                if c == ord('q'):
                    if self.auto_init:
                        self._end_curses()
                    return None

                elif c == curses.KEY_ENTER or c == 10:
                    if self.auto_init:
                        self._end_curses()
                    if (self.ret_type=="index"):
                        return self.current_selection
                    elif (self.ret_type=="value"):
                        return self.items[self.current_selection]

                # this is the meat of it all
                # could maybe simplify or abstract it away more
                # but it's fairly readable
                elif c == curses.KEY_DOWN:

                    if self.y < self.pagination-1 and self.current_selection < self.item_count - 1:
                        self.y+=1
                        self.current_selection+=1
                        self._update(-1)
                    elif not (self.pag_start + self.pagination > self.item_count-1):
                        self.y = 0
                        self.current_selection+=1
                        self.pag_start+=self.pagination
                        self._clear()
                        self._display()
                        continue

                elif c == curses.KEY_UP:

                    if self.y > 0 and self.current_selection > 0:
                        self.y-=1
                        self.current_selection-=1
                        self._update(1)
                    elif not (self.pag_start - self.pagination < 0):
                        self.y = self.pagination - 1 
                        self.current_selection-=1
                        self.pag_start-=self.pagination
                        self._clear()
                        self._display()
                        continue

            except KeyboardInterrupt:
                if self.auto_init:
                    self._end_curses()
                return None
