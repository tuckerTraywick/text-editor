rmport os
import pathlib
import blessed
from buffer import Buffer


class VerticalSplitView:
    def __init__(self, children, parent=None):
        self.children = children
        self.parent = parent

    @property
    def name(self):
        return f"({len(self.children)}){self.children[0].name}"

    @property
    def hasTabs(self):
        return any(child.hasTabs for child in self.children)

    def drawVerticalLine(self, editor, x, y, height):
        border = editor.getSetting("verticalBorder")
        for i in range(y, y + height):
            if i == y + height - 1:
                editor.print("verticalBorder", editor.format("statusLine", " "), x, i, width=len(border), height=1, end="")
            else:
                editor.print("verticalBorder", border, x, i, width=len(border), height=1, end="")

    def drawHorizontalLine(self, editor, x, y, width):
        editor.print("", " "*width, x, y, width, 1, end="")

    def draw(self, editor, x, y, width, height):
        childWidth = width//len(self.children)
        for i, child in enumerate(self.children[:-1]):
            if self.hasTabs and editor.getSetting("showTabList") and not child.hasTabs:#isinstance(child, TabView):
                childY = y + 1
                childHeight = height - 1
                self.drawHorizontalLine(editor, x, y, childWidth)
            else:
                childY = y
                childHeight = height
            child.draw(editor, x + childWidth*i, childY, childWidth - 1, childHeight)
            self.drawVerticalLine(editor, x + childWidth*(i + 1) - 1, y, height)

        if self.hasTabs and editor.getSetting("showTabList") and not self.children[-1].hasTabs:#isinstance(self.children[-1], TabView):
            childY = y + 1
            childHeight = height - 1
            self.drawHorizontalLine(editor, x + childWidth*(len(self.children) - 1), y, width - childWidth*(len(self.children) - 1))
        else:
            childY = y
            childHeight = height
        self.children[-1].draw(editor, x + childWidth*(len(self.children) - 1), childY, width - childWidth*(len(self.children) - 1), childHeight)


class HorizontalSplitView:
    def __init__(self, children, parent=None):
        self.children = children
        self.parent = parent

    @property
    def name(self):
        return f"({len(self.children)}){self.children[0].name}"

    @property
    def hasTabs(self):
        return any(child.hasTabs for child in self.children)

    def draw(self, editor, x, y, width, height):
        childHeight = height//len(self.children)
        for i, child in enumerate(self.children[:-1]):
            child.draw(editor, x, y + childHeight*i, width, childHeight)
        self.children[-1].draw(editor, x, y + childHeight*(len(self.children) - 1), width, height - childHeight*(len(self.children) - 1))


class TabView:
    def __init__(self, children, currentTab=0, parent=None):
        self.children = children
        self.parent = parent
        self.currentTab = currentTab

    @property
    def name(self):
        return f"({len(self.children)}){self.children[0].name}"

    @property
    def hasTabs(self):
        return True

    def draw(self, editor, x, y, width, height):
        if editor.getSetting("showTabList"):
            tabLine = ""
            length = 0
            for i, child in enumerate(self.children):
                tab = f" {i+1} {child.name} "
                if i == self.currentTab:
                    tabLine += editor.format("currentTabSeparator", editor.getSetting("currentTabSeparator")) + editor.terminal.normal \
                            +  editor.format("currentTabName",  tab) + editor.terminal.normal
                else:
                    tabLine += editor.format("tabSeparator", editor.getSetting("tabSeparator")) + editor.terminal.normal \
                            +  editor.format("tabName",  tab) + editor.terminal.normal
                length += len(tab) + 1
            editor.print("", tabLine, x, y, width, 1)
            editor.print("tabName", " "*(width - length), x + length, y, width, 1)

        self.children[self.currentTab].draw(editor, x, y + 1, width, height - 1)


class BufferView:
    def __init__(self, buffer, isActive=False, parent=None):
        self.buffer = buffer
        self.isActive = isActive
        self.parent = parent

    @property
    def name(self):
        return self.buffer.name

    @property
    def hasTabs(self):
        return False

    @property
    def statusLine(self):
        if self.buffer.hasUnsavedChanges:
            line = "+ "
        elif self.buffer.isReadonly:
            line = "ro "
        else:
            line = ""
        return line + f"{self.buffer.name} {(self.buffer.cursorY, self.buffer.cursorX)}"

    def draw(self, editor, x, y, width, height):
        gutterWidth = max(editor.getSetting("minimumGutterWidth"), len(str(self.buffer.numberOfLines)))
        originalY = y

        # Draw the lines and line numbers.
        for i, line in enumerate(self.buffer.lines):
            if height <= 1:
                break

            if editor.getSetting("showLineNumbers"):
                editor.print("currentLineNumber" if i == self.buffer.cursorY else "lineNumber", f"{i:>{gutterWidth}} ", x, y, width, 1)
            editor.print("currentLine" if i == self.buffer.cursorY else "", line.ljust(width-gutterWidth-1), x=x+gutterWidth+1, y=y, width=width-gutterWidth-1, height=1)
            y += 1
            height -= 1

        # Draw the empty lines.
        while height > 1:
            editor.print("emptyLineFill", editor.getSetting("emptyLineFill"), x, y, width, height, end="")
            y += 1
            height -= 1

        # Draw the statusline.
        left = editor.format("currentStatusLineIndicator", editor.getSetting("currentStatusLineLeftIndicator")) if self.isActive else editor.format("statusLineIndicator", editor.getSetting("statusLineLeftIndicator"))
        right = editor.format("currentStatusLineIndicator", editor.getSetting("currentStatusLineRightIndicator")) if self.isActive else editor.format("statusLineIndicator", editor.getSetting("statusLineRightIndicator"))
        editor.print("", left + editor.terminal.normal + editor.format("currentStatusLine" if self.isActive else "statusLine", self.statusLine) + editor.terminal.normal + right + " " \
                + editor.terminal.normal + editor.format("statusLine", " ".ljust(width - len(self.statusLine) - 4)), x, y, width, height, end="")

        # Draw the cursor.
        editor.print("activeCursor" if self.isActive else "inactiveCursor", self.buffer.currentCharacter or " ", x + gutterWidth + 1 + self.buffer.cursorX, originalY + self.buffer.cursorY, 1, 1, end="")


class Editor:
    def __init__(self):
        self.terminal = blessed.Terminal()
        self.settings = {
            "all": {
                "defaultMode": "all",
                "visualTabWidth": 4,
                "softTabWidth": 4,
                "minimumGutterWidth": 2,
                "emptyLineFill": "",
                "commandBufferPrompt": "> ",
                "verticalBorder": "\N{box drawings heavy vertical}",
                "tabSeparator": "\N{box drawings light vertical}",
                "currentTabSeparator": "\N{box drawings heavy vertical}",
                "statusLineLeftIndicator": "\N{black lower left triangle} ",
                "currentStatusLineLeftIndicator": "\N{black lower left triangle} ",
                "statusLineRightIndicator": "\N{black lower right triangle}",
                "currentStatusLineRightIndicator": "\N{black lower right triangle}",
                "terminalNewline": "\r\n",
                "terminalCarriageReturn": "\r",
                "terminalNewline": "\n",
                "terminalCarraigeReturnNewline": "\r\n",
                #"lineEnd": "unix",
                "softTabs": True,
                "showLineNumbers": True,
                "relativeLineNumbers": False,
                "showEmptyLineFill": True,
                "showTabList": True,
                "showStatusLine": True,
                "alwaysShowCommandBuffer": True,
                "syntaxHighlighting": False,
                "highlightCurrentLineNumber": True,
                "highlightCurrentLine": True,
            }
        }
        self.colors = {
            "all": {
                "default": "",
                "lineNumber": self.terminal.gray50,
                "currentLineNumber": self.terminal.gray80,
                "currentLine": "",
                "activeSelection": self.terminal.reverse,
                "emptyLineFill": "",
                "tabName": self.terminal.gray70_on_gray20,
                "currentTabName": self.terminal.bright_white_on_gray28,
                "statusLine": self.terminal.gray70_on_gray30,
                "currentStatusLine": self.terminal.bright_white_on_gray30,
                "verticalBorder": self.terminal.gray30,#self.terminal.on_gray30,
                "tabSeparator": self.terminal.gray60_on_gray20,
                "currentTabSeparator": self.terminal.lightblue_on_gray30,
                "statusLineIndicator": self.terminal.gray40_on_gray30,
                "currentStatusLineIndicator": self.terminal.lemonchiffon_on_gray30,
                "commandBuffer": "",
                "prompt": self.terminal.bold,
                "input": "",
                "activeCursor": self.terminal.reverse,
                "inactiveCursor": self.terminal.on_gray30,
                "fileName": "",
                "workingDirectory": self.terminal.italic,
                "directoryName": "",
                "match": self.terminal.reverse,
            }
        }
        self.keybindings = {"all": {"q": self.quit}}
        self.actions = {"all": {"draw": self.defaultDraw}}
        self.mode = "all"
        self.setup()

    def setup(self):
        # Sets up the state of the editor.
        self.mode = "all"
        self.workingDirectory = os.getcwd()
        self.currentKeybindings = self.keybindings[self.mode]
        self.currentGlobalKeybindings = self.keybindings["all"]
        self.currentKeySequence = ""
        self.buffers = [Buffer("*untitled*")]
        self.commandBuffer = Buffer("*command*")
        #self.rootView = VerticalSplitView([HorizontalSplitView(2*[BufferView(self.buffers[0])]), HorizontalSplitView([VerticalSplitView([BufferView(self.buffers[0], isActive=True), BufferView(self.buffers[0], isActive=False)]), BufferView(self.buffers[0], isActive=False), BufferView(self.buffers[0], isActive=False)])])
        self.rootView = VerticalSplitView([BufferView(self.buffers[0]), TabView(2*[BufferView(self.buffers[0])], currentTab=1), BufferView(self.buffers[0])])
        #self.rootView = HorizontalSplitView(2*[BufferView(self.buffers[0])])
        self.rootView = HorizontalSplitView([TabView([self.rootView, BufferView(self.buffers[0]), BufferView(self.buffers[0])]), VerticalSplitView([TabView(2*[BufferView(self.buffers[0])]), BufferView(self.buffers[0], True)])])
        #self.rootView = TabView(2*[BufferView(self.buffers[0])])
        #self.rootView = VerticalSplitView([self.rootView, BufferView(self.buffers[0])])
        self.currentView = self.rootView
        self.previousView = self.currentView
        self.keepRunning = True
        self.redraw = True
        self.clearCommandBuffer = False

    def getSetting(self, *settings):
        # Returns the given setting(s).
        if len(settings) == 1:
            return self.settings[self.mode].get(settings[0], self.settings["all"].get(settings[0], None))
        else:
            return {setting: self.getSetting(setting) for setting in settings}

    def getColor(self, *colors):
        # Returns the given color(s).
        if len(colors) == 1:
            return self.colors[self.mode].get(colors[0], self.colors["all"].get(colors[0], None))
        else:
            return {color: self.getColor(color) for color in colors}

    def runAction(self, action, *args):
        # Runs the given action for this mode and returns the value if any.
        return self.actions[self.mode].get(action, self.actions["all"].get(action, None))(*args)

    def format(self, color, text):
        # Formats the given string with the given color.
        if color == "":
            return text
        else:
            color = self.getColor(color)
            return color + text if isinstance(color, str) else color(text)

    def print(self, color, text, x=None, y=None, width=None, height=None, end="rn"):
        # Prints the given text in the given color with the given end type.
        end = {"r": self.getSetting("terminalCarriageReturn"), "n": self.getSetting("terminalNewline"), "rn": self.getSetting("terminalCarraigeReturnNewline"), "": ""}[end]
        #text = self.format(color, text[:min(len(text), width)])  # Length bug. need actual length, not formatted length.
        text = self.format(color, text)
        if x is not None or y is not None:
            with self.terminal.location(x, y):
                print(text + self.terminal.normal, end=end)
        else:
            print(text + self.terminal.normal, end=end)

    def registerKeypress(self, key):
        # Registers the given key and performs an action if it is bound to something.
        if self.currentGlobalKeybindings is not None:
            self.currentGlobalKeybindings = self.currentGlobalKeybindings.get(key, self.currentGlobalKeybindings.get("Printable" if len(key) == 1 else "Unbound", 
                None))
        self.currentKeybindings = self.currentKeybindings.get(key, self.currentKeybindings.get("Printable" if len(key) == 1 else "Unbound", self.currentKeybindings.get(
            "Unbound", self.currentGlobalKeybindings)))

        if self.currentKeybindings is None:
            self.currentKeybindings = self.keybindings[self.mode]
            self.currentGlobalKeybindings = self.keybindings["all"]
            self.currentKeySequence = ""
        elif isinstance(self.currentKeybindings, dict):
            self.currentKeySequence += key + " "
        else:
            self.currentKeybindings(key)
            self.currentKeybindings = self.keybindings[self.mode]
            self.currentGlobalKeybindings = self.keybindings["all"]
            self.currentKeySequence = ""
        self.redraw = True

    def update(self):
        # Takes input from the keyboard and updates the editor.
        aliases = {
            "KEY_ESCAPE": "Alt",
            "KEY_UP": "Up",
            "KEY_DOWN": "Down",
            "KEY_LEFT": "Left",
            "KEY_RIGHT": "Right",
            "KEY_ENTER": "Enter",
            "KEY_BACKSPACE": "Backspace",
            "KEY_INSERT": "Insert",
            "KEY_DELETE": "Delete",
            "KEY_TAB": "Tab",
            "KEY_F1": "F1",
            "KEY_F2": "F2",
            "KEY_F3": "F3",
            "KEY_F4": "F4",
            "KEY_F5": "F5",
            "KEY_F6": "F6",
            "KEY_F7": "F7",
            "KEY_F8": "F8",
            "KEY_F9": "F9",
            "KEY_F10": "F10",
            "KEY_F11": "F11",
            "KEY_F12": "F12",
        }
        key = self.terminal.inkey(0)

        if key:
            if self.clearCommandBuffer:
                self.commandBuffer.clear()
                self.clearCommandBuffer = False

            if key.is_sequence:
                self.registerKeypress(aliases.get(key.name, key.name))
            elif str(key).isascii() and 0 <= ord(key) <= 31:
                self.registerKeypress("Ctrl")
                self.registerKeypress(chr(ord(key) + 96).lower())
            elif key == " ":
                self.registerKeypress("Space")
            elif len(str(key)) == 1 and str(key).isascii() and str(key).isprintable():
                self.registerKeypress(str(key))

    def draw(self):
        # Draws the screen.
        if self.redraw:
            print(self.terminal.home + self.terminal.clear, end="")
            self.runAction("draw", 0, 0, self.terminal.width, self.terminal.height)
            self.redraw = False

    def run(self, *args):
        # Starts the editor.
        self.setup()
        self.buffers[0].name = "example.txt"
        self.buffers[0].readFromFile(self.buffers[0].name)
        with self.terminal.fullscreen(), self.terminal.raw(), self.terminal.keypad(), self.terminal.hidden_cursor():
            while self.keepRunning:
                self.draw()
                self.update()
        print(self.terminal.home + self.terminal.clear, end="")

    def defaultBegin(self):
        # The default behavior when a mode begins.
        pass

    def defaultEnd(self):
        # The default behavior when a mode ends.
        pass

    def defaultDraw(self, x, y, width, height):
        # The default behavior when the editor draws the screen.
        self.rootView.draw(self, x, y, width, height)
        #self.print("commandBuffer", "> command here", 0, height, width, 1, end="")

    def quit(self, key):
        # Quits the editor.
        self.keepRunning = False









"""
class Editor:
    def __init__(self):
        self.terminal = blessed.Terminal()
        self.settings = {
            "all": {
                "defaultMode": "all",
                "visualTabWidth": 4,
                "softTabWidth": 4,
                "minimumGutterWidth": 2,
                "maximumListHeight": self.terminal.height//3,
                "emptyLineFill": "~",
                "softTabs": True,
                "showLineNumbers": True,
                "relativeLineNumbers": False,
                "showEmptyLineFill": True,
                "showTabList": True,
                "showStatusLine": True,
                "alwaysShowCommandLine": True,
                "syntaxHighlighting": False,
                "highlightCurrentLineNumber": True,
                "highlightCurrentLine": True,
            },
        }
        self.colors = {
            "all": {
                "default": self.terminal.normal,
                "lineNumber": self.terminal.normal,
                "currentLineNumber": self.terminal.bright,
                "currentLine": self.terminal.normal,
                "currentSelection": self.terminal.reverse,
                "emptyLineFill": self.terminal.normal,
                "tabList": self.terminal.reverse,
                "currentTab": self.terminal.bold,
                "statusLine": self.terminal.reverse,
                "commandLine": self.terminal.normal,
                "prompt": self.terminal.bold,
                "input": self.terminal.normal,
                "activeCursor": self.terminal.reverse,
                "inactiveCursor": self.terminal.reverse_underline,
                "file": self.terminal.normal,
                "workingDirectory": self.terminal.italic,
                "directory": self.terminal.normal,
                "match": self.terminal.reverse,
            },
        }
        self.keybindings = {"all": {},}
        self.mode = "all"
        self.setup()

    def setup(self):
        self.mode = self.getSetting("defaultMode")
        self.workingDirectory = os.getcwd()
        self.currentKeybindings = self.keybindings[self.mode]
        self.currentGlobalKeybindings = self.keybindings["all"]
        self.currentKeySequence = ""
        self.statusLine = ""
        #self.scratchBuffer = Buffer(self.terminal.width, self.documentHeight, self.getSetting("visualTabWidth"), self.getSetting("softTabWidth"),  name="*scratch*")
        #self.clipboardBuffer = Buffer(self.terminal.width, self.documentHeight, self.getSetting("visualTabWidth"), self.getSetting("softTabWidth"),  name="*clipboard*")
        self.findPromptBuffer = Buffer(self.terminal.width, 1, self.getSetting("visualTabWidth"), self.getSetting("softTabWidth"),  name="*find*")
        self.replacePromptBuffer = Buffer(self.terminal.width, 1, self.getSetting("visualTabWidth"), self.getSetting("softTabWidth"),  name="*replace*")
        self.listBuffer = Buffer(self.terminal.width, 1, self.getSetting("visualTabWidth"), self.getSetting("softTabWidth"),  name="*results*")
        self.buffers = []
        self.searchResults = []
        self.currentSearchResultIndex = 0
        self.inputBuffer = None
        self.displayBuffer = None
        self.currentBufferIndex = 0
        self.previousBufferIndex = 0
        self.keepRunning = True
        self.redraw = True
        self.resetStatusLine = True

    @property
    def currentBuffer(self):
        return self.buffers[self.currentBufferIndex]

    @property
    def previousBuffer(self):
        return self.buffers[self.previousBufferIndex]

    @property
    def currentActions(self):
        return self.actions[self.mode]

    @property
    def currentSearchResult(self):
        return self.searchResults[self.currentSearchResultIndex]

    @property
    def documentHeight(self):
        return self.terminal.height - self.runAction("overlap")

    @property
    def searchTerms(self):
        search = self.findPromptBuffer.currentLine.text.strip()
        if search:
            return [term for term in self.findPromptBuffer.currentLine.text.split(" ") if term]
        else:
            return [""]

    def addMode(self, name, actions):
        self.settings[name] = {}
        self.keybindings[name] = {}
        self.colors[name] = {}
        self.actions[name] = {
            "begin": self.defaultBegin,
            "end": self.defaultEnd,
            "draw": self.defaultDraw,
            "drawTabList": self.defaultDrawTabList,
            "drawStatusLine": self.defaultDrawStatusLine,
            "drawCommandLine": self.defaultDrawCommandLine,
            "overlap": self.defaultOverlap,
            "highlight": self.defaultHighlight,
            "refreshSearchResults": None,
            "chooseSearchResult": None,
            "nextSearchResult": None,
            "previousSearchResult": None,
        }
        self.actions[name].update(actions)

    def removeMode(self, *modes):
        for mode in modes:
            del self.settings[mode], self.keybindings[mode], self.colors[mode], self.actions[mode]

    def getSetting(self, *settings):
        if len(settings) == 1:
            if settings[0] in self.settings[self.mode]:
                return self.settings[self.mode][settings[0]]
            else:
                return self.settings["all"][settings[0]]
        else:
            return {s: self.getSetting(s) for s in self.settings if s in self.settings}

    def setSetting(self, mode, setting, value):
        if isinstance(mode, list):
            for m in mode:
                self.setSetting(m, setting, value)
            return
        self.settings[mode][setting] = value

    def setSettings(self, mode, settings):
        if isinstance(mode, list):
            for m in mode:
                self.setSettings(m, settings)
            return
        self.settings[mode].update(settings)

    def removeSetting(self, mode, *settings):
        if isinstance(mode, list):
            for m in mode:
                self.removeSetting(m, settings)
            return

        for setting in settings:
            if setting in self.settings[mode]:
                del self.settings[mode][setting]

    def getColor(self, *colors):
        if len(colors) == 1:
            if colors[0] in self.colors[self.mode]:
                return self.colors[self.mode][colors[0]]
            else:
                return self.colors["all"][colors[0]]
        else:
            return {c: self.colors[self.mode][c] for c in self.colors if c in self.colors}

    def setColor(self, mode, textType, color):
        self.colors[mode][textType] = color

    def setColors(self, mode, colors):
        self.colors[mode].update(colors)

    def removeColor(self, mode, *colors):
        for color in colors:
            if color in self.colors[mode]:
                del self.colors[mode][color]

    def highlight(self, text, normal=""):
        return self.actions[self.mode]["highlight"](text, normal)

    def addKeybinding(self, modes, sequence, action):
        if isinstance(modes, list):
            for mode in modes:
                self.addKeybinding(mode, sequence, action)
            return

        mode = modes
        if mode[0] == "!":
            for key in self.keybindings:
                if key != mode[1:]:
                    self.addKeybinding(key, sequence, action)
            return

        if isinstance(sequence, list):
            for seq in sequence:
                self.addKeybinding(modes, seq, action)
            return

        currentBinding = self.keybindings[mode]
        previousBinding = currentBinding
        for key in sequence.split(" "):
            if key not in currentBinding:
                currentBinding[key] = {}
            previousBinding = currentBinding
            currentBinding = currentBinding[key]
        previousBinding[key] = action

    def removeKeybinding(modes, *bindings):
        pass

    def runAction(self, action):
        return self.currentActions[action]()

    def untitledFileName(self):
        # TODO: Make this append a number to the end of the name to make it unique.
        return "untitled"

    def print(self, color, text, end="\r\n"):
        if color in self.colors[self.mode]:
            colorCode = self.colors[self.mode][color]
        else:
            colorCode = self.colors["all"][color]
            
        if isinstance(colorCode, str):
            print(colorCode + text, end=end)
        else:
            print(colorCode(text), end=end)
        print(self.terminal.normal, end="")

    def printToStatusLine(self, text):
        self.statusLine = text
        self.redraw = True
        self.resetStatusLine = True

    def printPrompt(self, text, buffer, y):
        self.print("prompt", text, end="")
        buffer.draw(self, 1, len(text), y,
            showLineNumbers=False, relativeLineNumbers=False,
            showEmptyLineFill=False, showCursor=True,
            activeCursor=True, highlightCurrentLine=False,
            highlighting=False)

    def highlightMatches(self, string, normal):
        result = ""
        i = 0
        while i < len(string):
            for term in self.searchTerms:
                if term and string.startswith(term, i):
                    result += self.getColor("match") + term + normal
                    i += len(term)
                    break
            else:
                result += string[i]
                i += 1
        return result

    def newBuffer(self, name=None):
        if name is None:
            name = self.untitledFileName()
        self.previousBufferIndex = self.currentBufferIndex
        self.currentBufferIndex = len(self.buffers)
        self.buffers.append(Buffer(self.terminal.width, self.terminal.height, self.getSetting("visualTabWidth"), 
            self.getSetting("visualTabWidth"), name))

    def openFileInPlace(self, filePath):
        filePath = os.path.join(self.workingDirectory, filePath)
        if self.buffers:
            self.currentBuffer.open(filePath)
        else:
            self.newBuffer()
            self.currentBuffer.open(filePath)
        self.currentBuffer.name = filePath

    def openFile(self, *filePaths):
        for path in filePaths:
            for i, buffer in enumerate(self.buffers):
                if buffer.name == path:
                    self.switchToBuffer(i)
                    break
            else:
                self.newBuffer()
                self.openFileInPlace(path)

    def switchToBuffer(self, bufferIndex):
        if bufferIndex != self.currentBufferIndex:
            self.previousBufferIndex = self.currentBufferIndex
            self.currentBufferIndex = bufferIndex

    def draw(self):
        if self.redraw:
            self.redraw = False
            print(self.terminal.home + self.terminal.clear + self.terminal.home, end="")
            self.runAction("draw")

    def registerKeypress(self, key):
        if self.currentGlobalKeybindings is not None:
            self.currentGlobalKeybindings = self.currentGlobalKeybindings.get(key, self.currentGlobalKeybindings.get("Printable" if len(key) == 1 else "Unbound", 
                None))
        self.currentKeybindings = self.currentKeybindings.get(key, self.currentKeybindings.get("Printable" if len(key) == 1 else "Unbound", self.currentKeybindings.get(
            "Unbound", self.currentGlobalKeybindings)))

        if self.currentKeybindings is None:
            self.currentKeybindings = self.keybindings[self.mode]
            self.currentGlobalKeybindings = self.keybindings["all"]
            self.currentKeySequence = ""
        elif isinstance(self.currentKeybindings, dict):
            self.currentKeySequence += key + " "
        else:
            self.currentKeybindings(key)
            self.currentKeybindings = self.keybindings[self.mode]
            self.currentGlobalKeybindings = self.keybindings["all"]
            self.currentKeySequence = ""
        self.redraw = True

    def update(self):
        aliases = {
            "KEY_ESCAPE": "Alt",
            "KEY_UP": "Up",
            "KEY_DOWN": "Down",
            "KEY_LEFT": "Left",
            "KEY_RIGHT": "Right",
            "KEY_ENTER": "Enter",
            "KEY_BACKSPACE": "Backspace",
            "KEY_INSERT": "Insert",
            "KEY_DELETE": "Delete",
            "KEY_TAB": "Tab",
            "KEY_F1": "F1",
            "KEY_F2": "F2",
            "KEY_F3": "F3",
            "KEY_F4": "F4",
            "KEY_F5": "F5",
            "KEY_F6": "F6",
            "KEY_F7": "F7",
            "KEY_F8": "F8",
            "KEY_F9": "F9",
            "KEY_F10": "F10",
            "KEY_F11": "F11",
            "KEY_F12": "F12",
        }
        key = self.terminal.inkey(0)

        if key:
            if self.resetStatusLine:
                self.statusLine = ""

            if key.is_sequence:
                self.registerKeypress(aliases.get(key.name, key.name))
            elif str(key).isascii() and 0 <= ord(key) <= 31:
                self.registerKeypress("Ctrl")
                self.registerKeypress(chr(ord(key)+96).lower())
            elif key == " ":
                self.registerKeypress("Space")
            elif len(str(key)) == 1 and str(key).isascii() and str(key).isprintable():
                self.registerKeypress(str(key))

    def run(self, *filePaths):
        self.setup()
        for path in filePaths:
            self.open(path)
        #self.openFile("notes.txt")
        self.openFile("example.txt")
        self.switchToBuffer(0)
        self.runAction("begin")

        with self.terminal.fullscreen(), self.terminal.raw(), self.terminal.keypad(), self.terminal.hidden_cursor():
            while self.keepRunning:
                self.draw()
                self.update()
        print(self.terminal.home + self.terminal.clear, end="")

    def defaultBegin(self):
        pass

    def defaultEnd(self):
        pass

    def defaultDraw(self):
        # Draw the tab list.
        if self.getSetting("showTabList"):
            self.runAction("drawTabList")
            print("", end="\r\n")

        # Draw the current buffer.
        self.displayBuffer.draw(self, self.documentHeight, 0, int(self.getSetting("showTabList")),
            showLineNumbers=self.getSetting("showLineNumbers"), relativeLineNumbers=self.getSetting("relativeLineNumbers"),
            showEmptyLineFill=self.getSetting("showEmptyLineFill"), showCursor=True,
            activeCursor=self.mode == "edit", highlightCurrentLine=True)

        # Draw the status line.
        if self.getSetting("showStatusLine") or self.statusLine:
            print("", end="\n")
            self.runAction("drawStatusLine")

        # Draw the command line.
        if self.getSetting("alwaysShowCommandLine"):
            print("", end="\n")
            self.runAction("drawCommandLine")
            print("", end="\r")

    def defaultDrawTabList(self):
        for i, buffer in enumerate(self.buffers):
            self.print("currentTab" if i == self.currentBufferIndex else "tabList", f" {i+1} {os.path.basename(buffer.name) + buffer.status} ", end="")
        self.print("tabList", " "*(self.terminal.width - self.terminal.get_location()[1]), end="")

    def defaultDrawStatusLine(self):
        if self.statusLine:
            self.print("statusLine", self.terminal.ljust(self.statusLine), end="\r")
        elif self.currentKeySequence:
            self.print("statusLine", self.terminal.ljust(self.currentKeySequence), end="\r")
        else:
            self.print("statusLine", self.terminal.ljust(self.currentBuffer.fullName), end="\r")

    def defaultDrawCommandLine(self):
        self.print("commandLine", "command text here", end="")

    def defaultOverlap(self):
        return int(self.getSetting("alwaysShowCommandLine")) + int(self.getSetting("showStatusLine")) + int(self.getSetting("showTabList"))

    def defaultHighlight(self, line, normal=""):
        return line

    def homeMenuDraw(self):
        self.print("default", self.terminal.center("Text Editor"))

    def editBegin(self):
        self.inputBuffer = self.displayBuffer = self.currentBuffer
        self.redraw = True

    def editEnd(self):
        pass

    def findBufferBegin(self):
        self.findPromptBuffer.clear()
        self.refreshSearchResults()
        self.currentBuffer.pageHeight = self.documentHeight
        self.inputBuffer = self.findPromptBuffer
        self.displayBuffer = self.currentBuffer

    def findBufferEnd(self):
        self.findPromptBuffer.clear()
        self.listBuffer.clear()

    def findBufferDraw(self):
        # Draw the document if not in fullscreen mode.
        if not self.getSetting("fullscreen"):
            self.defaultDraw()
            print("", end="\n")
        
        # Set the height of the document and draw the prompt first if in fullscreen mode.
        if self.getSetting("fullscreen"):
            height = min(self.terminal.height - 1, self.listBuffer.numberOfLines)
            self.printPrompt("Find buffer: ", self.findPromptBuffer, 0)
            print("", end="\r\n")
        else:
            height = min(self.getSetting("maximumListHeight"), self.listBuffer.numberOfLines)

        # Draw the search results.
        if self.searchResults:
            self.listBuffer.draw(self, height, 0, 0,
                showLineNumbers=True, relativeLineNumbers=False,
                showEmptyLineFill=False, showCursor=False,
                activeCursor=False, highlightCurrentLine=True)
        else:
            self.print("lineNumber", "No results", end="\r")

        # Draw the prompt last if not in fullscreen mode.
        if not self.getSetting("fullscreen"):
            print("", end="\r\n")
            self.printPrompt("Find buffer: ", self.findPromptBuffer, self.terminal.height)

    def findBufferRefreshSearchResults(self):
        self.searchResults = []
        self.currentSearchResultIndex = 0
        for i, buffer in enumerate(self.buffers):
            for term in self.searchTerms:
                if term in buffer.name:
                    self.searchResults.append((buffer.fullName, i, buffer))
                    break

        if self.searchResults:
            self.displayBuffer = self.searchResults[0][2]
        else:
            self.displayBuffer = self.currentBuffer

    def findBufferChooseSearchResult(self):
        if self.searchResults:
            self.previousBufferIndex = self.currentBufferIndex
            self.currentBufferIndex = self.currentSearchResult[1]
        self.setMode("edit")()

    def findBufferNextSearchResult(self):
        self.displayBuffer = self.currentSearchResult[2]

    def findBufferPreviousSearchResult(self):
        self.displayBuffer = self.currentSearchResult[2]

    def findBufferOverlap(self):
        if self.getSetting("fullscreen"):
            return 0
        else:
            return max(1, min(self.listBuffer.numberOfLines, self.getSetting("maximumListHeight"))) + 1 + (1 if self.getSetting("showStatusLine") else 0)

    def findFileBegin(self):
        self.findPromptBuffer.clear()
        self.refreshSearchResults()
        self.currentBuffer.pageHeight = self.documentHeight
        self.inputBuffer = self.findPromptBuffer
        self.displayBuffer = self.currentBuffer

    def findFileEnd(self):
        self.findPromptBuffer.clear()
        self.listBuffer.clear()

    def findFileDraw(self):
        # Draw the document if not in fullscreen mode.
        if not self.getSetting("fullscreen"):
            self.defaultDraw()
            print("", end="\n")
        
        # Set the height of the document and draw the prompt first if in fullscreen mode.
        if self.getSetting("fullscreen"):
            height = min(self.terminal.height - 2, self.listBuffer.numberOfLines)
            self.printPrompt("Open file: ", self.findPromptBuffer, 0)
            print("", end="\r\n")
        else:
            height = min(self.getSetting("maximumListHeight"), self.listBuffer.numberOfLines)

        # Draw the search results.
        self.print("workingDirectory", f"{self.fileName(self.workingDirectory)} [{len(self.searchResults)}]", end="\r\n")
        if self.searchResults:
            self.listBuffer.draw(self, height, 0, 0,
                showLineNumbers=True, relativeLineNumbers=False,
                showEmptyLineFill=False, showCursor=False,
                activeCursor=False, highlightCurrentLine=True)
        else:
            self.print("lineNumber", "No results", end="\r")

        # Draw the prompt last if not in fullscreen mode.
        if not self.getSetting("fullscreen"):
            print("", end="\r\n")
            self.printPrompt("Open file: ", self.findPromptBuffer, self.terminal.height)

    def fileName(self, path):
        return path + "/" if os.path.isdir(os.path.join(self.workingDirectory, path)) and path != "/" else path

    def upDirectory(self, path, amount=1):
        head, tail = os.path.split(path)
        for i in range(amount):
            split = os.path.split(head)
            head = split[0]
            tail = os.path.join(split[1], tail)
        return tail

    def recursivelyFindFiles(self, path="", root=""):
        if path != "":
            for term in self.searchTerms:
                if term in self.upDirectory(os.path.join(root, path), term.count("/")):
                    self.searchResults.append((self.fileName(os.path.join(root, path)), os.path.join(root, path)))
                    break

        if os.path.isdir(os.path.join(self.workingDirectory, root, path)):
            for subpath in os.listdir(os.path.join(self.workingDirectory, root, path)):
                self.recursivelyFindFiles(subpath, os.path.join(root, path))

    def findFileRefreshSearchResults(self):
        if self.findPromptBuffer.currentLine.hasText():
            self.searchResults = []
            self.listBuffer.clear()
            self.currentSearchResultIndex = 0
            self.recursivelyFindFiles()
        else:
            self.searchResults = [("..", "..")]
            for path in os.listdir(self.workingDirectory):
                for term in self.searchTerms:
                    if term in path:
                        self.searchResults.append((self.fileName(path), path))
                        break

            if len(self.searchResults) > 1:
                self.currentSearchResultIndex = 1
            else:
                self.currentSearchResultIndex = 0

    def findFileChooseSearchResult(self):
        if self.currentSearchResult[1] == "..":
            self.workingDirectory = os.path.dirname(self.workingDirectory)
            self.refreshSearchResults()
            return

        path = os.path.join(self.workingDirectory, self.currentSearchResult[1])
        if os.path.isdir(path):
            self.workingDirectory = path
            self.findPromptBuffer.clear()
            self.refreshSearchResults()
        elif os.path.isfile(path):
            self.openFile(path)
            self.setMode("edit")()

    def findFileNextSearchResult(self):
        pass

    def findFilePreviousSearchResult(self):
        pass

    def findFileOverlap(self):
        if self.getSetting("fullscreen"):
            return 0
        else:
            return max(1, min(self.listBuffer.numberOfLines, self.getSetting("maximumListHeight"))) + 2 + (1 if self.getSetting("showStatusLine") else 0)

    def setMode(self, mode):
        def process(key=None):
            self.runAction("end")
            self.mode = mode
            self.runAction("begin")
        return process

    def refreshSearchResults(self, key=None):
        # Populate the search results.
        self.runAction("refreshSearchResults")
        self.listBuffer.clear()
        for result in self.searchResults:
            self.listBuffer.insert(1, result[0])
            self.listBuffer.insertLineBelow()

        # Delete the extraneous newline.
        if self.searchResults:
            self.listBuffer.deleteLine()

        # Resize the list buffer.
        if self.getSetting("fullscreen"):
            self.listBuffer.pageHeight = self.terminal.height
        else:
            self.listBuffer.pageHeight = min(len(self.searchResults), self.getSetting("maximumListHeight"))
        # Position the cursor.
        self.listBuffer.cursorBufferStart()
        self.listBuffer.cursorLineDown(self.currentSearchResultIndex)
        self.redraw = True

    def chooseSearchResult(self, key=None):
        self.runAction("chooseSearchResult")

    def copySearchResult(self, key=None):
        self.findPromptBuffer.clear()
        self.findPromptBuffer.insert(1, self.currentSearchResult[0])
        self.refreshSearchResults()

    def nextSearchResult(self, key=None):
        if self.currentSearchResultIndex < len(self.searchResults) - 1:
            self.listBuffer.cursorLineDown()
            self.currentSearchResultIndex += 1
            self.redraw = True
            self.runAction("nextSearchResult")

    def previousSearchResult(self, key=None):
        if self.currentSearchResultIndex > 0:
            self.listBuffer.cursorLineUp()
            self.currentSearchResultIndex -= 1
            self.redraw = True
            self.runAction("previousSearchResult")

    def saveBuffer(self, key=None):
        if self.currentBuffer.hasUnsavedChanges:
            self.currentBuffer.write(self.workingDirectory + self.currentBuffer.name)
            self.satusLine = f"{self.currentBuffer.name} saved."
            self.redraw = True
            self.clearStatusLine = True

    def saveAllBuffers(self, key=None):
        for buffer in self.buffers:
            if buffer.hasUnsavedChanges:
                buffer.write(self.workingDirectory + self.currentBuffer.name)
                self.statusLine = "All buffers saved."
                self.redraw = True
                self.clearStatusLine = True

    def killBuffer(self, key=None):
        self.currentBuffer.clear()
        if len(self.buffers) == 1:
            self.currentBuffer.clear()
            self.currentBuffer.name = untitledFileName(self.workingDirectory)
        else:
            del self.buffers[self.currentBufferIndex]
            if self.currentBufferIndex == len(self.buffers):
                self.currentBufferIndex -= 1
        self.previousBufferIndex = self.currentBufferIndex
        self.redraw = True

    def closeBuffer(self, key=None):
        if self.currentBuffer.hasUnsavedChanges:
            self.statusLine = "This buffer has unsaved changes. Press Ctrl x to kill the buffer without saving."
            self.redraw = True
            self.clearStatusLine = True
        else:
            self.killBuffer(key)

    def cursorCharacterRight(self, key=None):
        self.redraw = self.inputBuffer.cursorY < self.inputBuffer.numberOfLines or self.inputBuffer.cursorX < self.inputBuffer.currentLine.length \
            or self.inputBuffer.scrollY < self.inputBuffer.numberOfLines - 1
        self.inputBuffer.cursorCharacterRight()

    def cursorCharacterLeft(self, key=None):
        self.redraw = self.inputBuffer.cursorY > 0 or self.inputBuffer.cursorX > 0
        self.inputBuffer.cursorCharacterLeft()

    def cursorLineUp(self, key=None):
        self.inputBuffer.cursorLineUp()
        self.redraw = self.inputBuffer.cursorY > 0 or self.inputBuffer.cursorX > 0

    def cursorLineDown(self, key=None):
        if self.mode == "findBuffer":
            self.nextSearchResult()
            self.currentBufferIndex = self.searchResults[self.listBuffer.cursorY][1]
        else:
            self.inputBuffer.cursorLineDown()
            self.redraw = self.inputBuffer.cursorY < self.inputBuffer.numberOfLines or self.inputBuffer.cursorX < self.inputBuffer.currentLine.length \
                or self.inputBuffer.scrollY < self.inputBuffer.numberOfLines - 1

    def cursorLineStart(self, key=None):
        self.redraw = self.inputBuffer.cursorX > 0 or self.inputBuffer.cursorY > 0
        self.inputBuffer.cursorLineStart()

    def cursorLineEnd(self, key=None):
        self.redraw = self.inputBuffer.cursorX < self.inputBuffer.currentLine.length or self.inputBuffer.cursorY < self.inputBuffer.numberOfLines - 1
        self.inputBuffer.cursorLineEnd()

    def insertLineAbove(self, key=None):
        self.inputBuffer.insertLineAbove()
        self.redraw = True

    def insertLineBelow(self, key=None):
        self.inputBuffer.insertLineBelow()
        self.redraw = True

    def insertCharacter(self, key):
        if key == "Space":
            self.inputBuffer.insert(1, " ")
        else:
            self.inputBuffer.insert(1, key)

        if self.inputBuffer is self.findPromptBuffer:
            self.refreshSearchResults()
        self.redraw = True

    def delete(self, key=None):
        self.inputBuffer.delete()
        self.redraw = True

    def deleteCharacterLeft(self, key=None):
        self.inputBuffer.deleteCharacterLeft()
        if self.inputBuffer is self.findPromptBuffer:
            self.refreshSearchResults()
        self.redraw = True

    def deleteCharacterRight(self, key=None):
        self.inputBuffer.deleteCharacterRight()
        if self.inputBuffer is self.findPromptBuffer:
            self.refreshSearchResults()
        self.redraw = True

    def deleteLine(self, key=None):
        self.inputBuffer.deleteLine()
        if self.inputBuffer is self.findPromptBuffer:
            self.refreshSearchResults()
        self.redraw = True

    def quit(self, key=None):
        for i, buffer in enumerate(self.buffers):
            if buffer.hasUnsavedChanges:
                self.statusLine = "A buffer has unsaved changes. Press Ctrl e to exit without saving."
                self.redraw = True
                self.clearStatusLine = True
                return
        self.keepRunning = False
        
    def exit(self, key=None):
        self.keepRunning = False

    def chooseBuffer(self, key=None):
        self.setMode("edit")(key)
        self.currentBufferIndex = self.searchResults[self.listBuffer.cursorY][1]
        self.bufferIndexBeforeSearch = self.currentBufferIndex

    def cancelBufferSearch(self, key=None):
        self.currentBufferIndex = self.bufferIndexBeforeSearch
        self.setMode("edit")(key)
"""

