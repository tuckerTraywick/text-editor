import blessed
from buffer import Buffer


def untitledFileName(directory):
    # TODO: Make this append a number to the end of the file name if one already exists.
    return "untitled"


class Editor:
    def __init__(self):
        self.terminal = blessed.Terminal()
        self.settings = {
            "visualTabWidth": 4,
            "softTabWidth": 4,
            "minimumGutterWidth": 2,
            "maximumListSize": 5,
            "emptyLineFill": "~",
            "softTabs": False,
            "showLineNumbers": True,
            "relativeLineNumbers": False,
            "showEmptyLineFill": True,
            "showStatusLine": True,
            "highlighting": False,
        }
        self.colorscheme = {
            "default": self.terminal.normal,
            "lineNumber": self.terminal.normal,
            "currentLineNumber": self.terminal.bright,
            "currentLine": self.terminal.normal,
            "currentSelection": self.terminal.reverse,
            "emptyLineFill": self.terminal.normal,
            "statusLine": self.terminal.reverse,
            "prompt": self.terminal.bold,
            "input": self.terminal.normal,
            "activeCursor": self.terminal.reverse,
            "inactiveCursor": self.terminal.reverse_underline,
        }
        self.keybindings = {
            "edit": {},
            "find": {},
            "findInBuffers": {},
            "findInFiles": {},
            "replace": {},
            "findBuffer": {},
            "findFile": {},
        }
        self.setup()

    def setup(self):
        self.mode = "edit"
        self.workingDirectory = ""
        self.currentKeybindings = self.keybindings[self.mode]
        self.currentKeySequence = ""
        self.statusLine = ""
        self.scratchBuffer = Buffer(self.terminal.width, self.bufferHeight, self.settings.get("visualTabwidth", 4), self.settings.get("softTabWidth", 4), index=-1, name="*scratch*")
        self.clipboardBuffer = Buffer(self.terminal.width, self.bufferHeight, self.settings.get("visualTabWidth", 4), self.settings.get("softTabWidth", 4), index=-1, name="*clipboard*")
        self.promptBuffer = Buffer(self.terminal.width, 1, self.settings.get("visualTabWidth", 4), self.settings.get("softTabWidth", 4), index=-1, name="*prompt*")
        self.listBuffer = Buffer(self.terminal.width, 1, self.settings.get("visualTabWidth", 4), self.settings.get("softTabWidth", 4), index=-1, name="*list*")
        self.buffers = []
        self.searchResults = []
        self.currentBufferIndex = 0
        self.previousBufferIndex = 0
        self.bufferIndexBeforeSearch = self.currentBufferIndex
        self.keepRunning = True
        self.needsRedraw = True
        self.resetStatusLine = True

    @property
    def currentBuffer(self):
        return self.buffers[self.currentBufferIndex]

    @property
    def previousBuffer(self):
        return self.buffers[self.previousBufferIndex]

    @property
    def focusedBuffer(self):
        return self.currentBuffer if self.mode == "edit" else self.promptBuffer

    @property
    def bufferHeight(self):
        height = self.terminal.height - 1 if self.getSetting("showStatusLine") or self.statusLine else self.terminal.height
        if self.mode in ["findBuffer", "findFile"]:
            height -= self.promptBuffer.numberOfLines + self.listBuffer.pageHeight
        return height

    def getSetting(self, *settings):
        if len(settings) == 1:
            return self.settings[settings[0]]
        else:
            return {s: self.settings[s] for s in self.settings if s in self.settings}

    def setSetting(self, setting, value):
        self.settings[setting] = value

    def setSettings(self, settings):
        self.settings.update(settings)

    def getColor(self, *colors):
        if len(colors) == 1:
            return self.colorscheme[colors[0]]
        else:
            return {c: self.colorscheme[c] for c in self.colorscheme if c in self.colorscheme}

    def setColor(self, textType, color):
        self.colorscheme[textType] = color

    def setColors(self, colors):
        self.colorscheme.update(colors)

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
        elif mode == "all":
            for key in self.keybindings:
                self.addKeybinding(key, sequence, action)
            return

        if isinstance(sequence, list):
            for seq in sequence:
                self.addKeybinding(modes, seq, action)
            return

        if mode not in self.keybindings:
            self.keybindings[mode] = {}

        currentBinding = self.keybindings[mode]
        previousBinding = currentBinding
        for key in sequence.split(" "):
            if key not in currentBinding:
                currentBinding[key] = {}
            previousBinding = currentBinding
            currentBinding = currentBinding[key]
        previousBinding[key] = action

    def newBuffer(self, name="untitled"):
        self.previousBufferIndex = self.currentBufferIndex
        self.currentBufferIndex = len(self.buffers)
        self.buffers.append(Buffer(self.terminal.width, self.bufferHeight, self.settings["visualTabWidth"], 
            self.settings["softTabWidth"], self.currentBufferIndex, name))
        self.mode = "edit"
        self.needsRedraw = True

    def openInPlace(self, filePath):
        if self.buffers:
            self.currentBuffer.open(filePath)
        else:
            self.newBuffer()
            self.currentBuffer.open(filePath)
        self.currentBuffer.name = filePath
        self.needsRedraw = True

    def open(self, *filePaths):
        for path in filePaths:
            self.newBuffer()
            self.openInPlace(path)

    def switchToBuffer(self, bufferIndex):
        if bufferIndex != self.currentBufferIndex:
            self.previousBufferIndex = self.currentBufferIndex
            self.currentBufferIndex = bufferIndex
            self.needsRedraw = True

    def saveBuffer(self, key=None):
        if self.currentBuffer.hasUnsavedChanges:
            self.currentBuffer.write(self.workingDirectory + self.currentBuffer.name)
            self.satusLine = f"{self.currentBuffer.name} saved."
            self.needsRedraw = True
            self.clearStatusLine = True

    def saveAllBuffers(self, key=None):
        for buffer in self.buffers:
            if buffer.hasUnsavedChanges:
                buffer.write(self.workingDirectory + self.currentBuffer.name)
                self.statusLine = "All buffers saved."
                self.needsRedraw = True
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
        self.needsRedraw = True

    def closeBuffer(self, key=None):
        if self.currentBuffer.hasUnsavedChanges:
            self.statusLine = "This buffer has unsaved changes. Press Ctrl x to kill the buffer without saving."
            self.needsRedraw = True
            self.clearStatusLine = True
        else:
            self.killBuffer(key)

    def switchToPreviousBuffer(self, key=None):
        if self.currentBufferIndex != self.previousBufferIndex:
            self.previousBufferIndex, self.previousBufferIndex = self.currentBufferIndex, self.currentBufferIndex
            self.needsRedraw = True

    def bufferForward(self, key=None):
        if self.currentBufferIndex < len(self.buffers) - 1:
            self.currentBufferIndex += 1
            self.needsRedraw = True
            if self.mode == "findBuffer":
                self.listBuffer.cursorLineDown()

    def bufferBackward(self, key=None):
        if self.currentBufferIndex > 0:
            self.currentBufferIndex -= 1
            self.needsRedraw = True
            if self.mode == "findBuffer":
               self.listBuffer.cursorLineUp()

    def cursorCharacterRight(self, key=None):
        self.needsRedraw = self.focusedBuffer.cursorY < self.focusedBuffer.numberOfLines or self.focusedBuffer.cursorX < self.focusedBuffer.currentLine.length() \
            or self.focusedBuffer.scrollY < self.focusedBuffer.numberOfLines - 1
        self.focusedBuffer.cursorCharacterRight()

    def cursorCharacterLeft(self, key=None):
        self.needsRedraw = self.focusedBuffer.cursorY > 0 or self.focusedBuffer.cursorX > 0
        self.focusedBuffer.cursorCharacterLeft()

    def cursorLineUp(self, key=None):
        self.needsRedraw = self.focusedBuffer.cursorY > 0 or self.focusedBuffer.cursorX > 0
        self.focusedBuffer.cursorLineUp()

    def cursorLineDown(self, key=None):
        self.needsRedraw = self.focusedBuffer.cursorY < self.focusedBuffer.numberOfLines or self.focusedBuffer.cursorX < self.focusedBuffer.currentLine.length() \
            or self.focusedBuffer.scrollY < self.focusedBuffer.numberOfLines - 1
        self.focusedBuffer.cursorLineDown()

    def cursorLineStart(self, key=None):
        self.needsRedraw = self.focusedBuffer.cursorX > 0 or self.focusedBuffer.cursorY > 0
        self.focusedBuffer.cursorLineStart()

    def cursorLineEnd(self, key=None):
        self.needsRedraw = self.focusedBuffer.cursorX < self.focusedBuffer.currentLine.length() or self.focusedBuffer.cursorY < self.focusedBuffer.numberOfLines - 1
        self.focusedBuffer.cursorLineEnd()

    def insertLineAbove(self, key=None):
        self.focusedBuffer.insertLineAbove()
        self.needsRedraw = True

    def insertLineBelow(self, key=None):
        self.focusedBuffer.insertLineBelow()
        self.needsRedraw = True

    def insertCharacter(self, key):
        if key == "Space":
            self.focusedBuffer.insert(1, " ")
        else:
            self.focusedBuffer.insert(1, key)

        if self.mode == "findBuffer":
            self.fillBufferList()
        self.needsRedraw = True

    def delete(self, key=None):
        self.focusedBuffer.delete()
        self.needsRedraw = True

    def deleteCharacterLeft(self, key=None):
        self.focusedBuffer.deleteCharacterLeft()
        self.needsRedraw = True

    def deleteCharacterRight(self, key=None):
        self.focusedBuffer.deleteCharacterRight()
        self.needsRedraw = True

    def deleteLine(self, key=None):
        self.focusedBuffer.deleteLine()
        self.needsRedraw = True

    def quit(self, key=None):
        for i, buffer in enumerate(self.buffers):
            if buffer.hasUnsavedChanges:
                self.statusLine = "A buffer has unsaved changes. Press Ctrl e to exit without saving."
                self.needsRedraw = True
                self.clearStatusLine = True
                return
        self.keepRunning = False
        
    def exit(self, key=None):
        self.keepRunning = False

    def chooseBuffer(self, key=None):
        self.setMode("edit")(key)
        self.bufferIndexBeforeSearch = self.currentBufferIndex

    def cancelBufferSearch(self, key=None):
        self.currentBufferIndex = self.bufferIndexBeforeSearch
        self.setMode("edit")(key)

    def fillBufferList(self):
        self.listBuffer.clear()
        search = self.promptBuffer.currentLine.text
        numberOfResults = 0
        for i, buffer in enumerate(self.buffers):
            if search in buffer.name:
                self.listBuffer.insert(1, f"{buffer.fullName}")
                if i < len(self.buffers) - 1:
                    self.listBuffer.insertLineBelow()
                numberOfResults += 1
        self.listBuffer.pageHeight = min(numberOfResults, self.getSetting("maximumListSize"))
        self.listBuffer.cursorBufferStart()
        self.listBuffer.cursorLineDown(self.currentBufferIndex)

    def setMode(self, mode):
        def process(key):
            self.mode = mode
            self.needsRedraw = True
            if mode == "findBuffer":
                self.promptBuffer.clear()
                self.fillBufferList()
        return process

    def print(self, color, text, end="\r\n"):
        colorCode = self.colorscheme[color]
        if isinstance(colorCode, str):
            print(colorCode + text, end=end)
        else:
            print(colorCode(text), end=end)
        print(self.terminal.normal, end="")

    def drawStatusLine(self):
        if self.statusLine:
            self.print("statusLine", self.terminal.ljust(self.statusLine), end="\r")
        elif self.currentKeySequence:
            self.print("statusLine", self.terminal.ljust(self.currentKeySequence), end="\r")
        elif self.mode == "findBuffer":
            self.print("statusLine", self.terminal.ljust(self.buffers[self.bufferIndexBeforeSearch].fullName), end="\r")
        else:
            self.print("statusLine", self.terminal.ljust(self.currentBuffer.fullName), end="\r")

    def drawPrompt(self, text):
        self.print("prompt", text, end="")
        self.promptBuffer.draw(self, 1, len(text), self.terminal.height,
            showLineNumbers=False, relativeLineNumbers=False,
            showEmptyLineFill=False, showCursor=True,
            activeCursor=True, highlightCurrentLine=False)

    def draw(self):
        if self.needsRedraw:
            self.needsRedraw = False
            print(self.terminal.home + self.terminal.clear + self.terminal.home, end="")

            # Draw the current buffer.
            self.currentBuffer.draw(self, self.bufferHeight, 0, 0,
                showLineNumbers=self.getSetting("showLineNumbers"), relativeLineNumbers=self.getSetting("relativeLineNumbers"),
                showEmptyLineFill=self.getSetting("showEmptyLineFill"), showCursor=True,
                activeCursor=self.mode == "edit", highlightCurrentLine=True)

            # Draw the status line.
            if self.getSetting("showStatusLine") or self.statusLine:
                print("", end="\n")
                self.drawStatusLine()

            # Draw the buffer list.
            if self.mode == "findBuffer":
                print("", end="\n")
                self.listBuffer.draw(self, self.listBuffer.pageHeight, 0, 0,
                    showLineNumbers=True, relativeLineNumbers=False,
                    showEmptyLineFill=False, showCursor=False,
                    activeCursor=False, highlightCurrentLine=True)
                print("", end="\r\n")
                self.drawPrompt("Find buffer: ")

    def registerKeypress(self, key):
        self.currentKeybindings = self.currentKeybindings.get(key, self.currentKeybindings.get("Printable" if len(key) == 1 else "Unbound", self.currentKeybindings.get(
            "Unbound", None)))

        if self.currentKeybindings is None:
            self.currentKeybindings = self.keybindings[self.mode]
            self.currentKeySequence = ""
        elif isinstance(self.currentKeybindings, dict):
            self.currentKeySequence += key + " "
        else:
            self.currentKeybindings(key)
            self.currentKeybindings = self.keybindings[self.mode]
            self.currentKeySequence = ""
        self.needsRedraw = True

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

        if self.currentBuffer.pageWidth != self.terminal.width or self.currentBuffer.pageHeight != self.bufferHeight:
            self.currentBuffer.pageWidth = self.terminal.width
            self.currentBuffer.pageHeight = self.bufferHeight
            self.needsRedraw = True

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

    def run(self, filePaths=[]):
        self.setup()
        for path in filePaths:
            self.open(path)
        self.open("notes.txt")
        self.open("example.txt")
        self.newBuffer("untitled 1")
        self.newBuffer("untitled 2")
        self.newBuffer("untitled 3")
        self.newBuffer("untitled 4")
        self.newBuffer("penispenispnesip")
        self.newBuffer("untitled 5")
        self.switchToBuffer(0)

        with self.terminal.raw(), self.terminal.keypad(), self.terminal.hidden_cursor():
            while self.keepRunning:
                if self.needsRedraw:
                    self.draw()
                    self.needsRedraw = False
                self.update()
        print(self.terminal.home + self.terminal.clear, end="")

