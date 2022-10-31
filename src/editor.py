import os
import pathlib
import blessed
from buffer import Buffer
from suggestionlist import SuggestionList


class Editor:
    def __init__(self):
        self.terminal = blessed.Terminal()
        self.actions = {
            "all": {
                "start": self.defaultStart,
                "end": self.defaultEnd,
                "draw": self.defaultDraw,
                "edit": self.defaultEdit,
            },
            "edit": {
                "start": self.editStart,
                "draw": self.editDraw,
            },
            "findBuffer": {
                "start": self.findBufferStart,
                "end": self.findBufferEnd,
                "draw": self.findBufferDraw,
                "edit": self.findBufferEdit,
            },
            "find": {
                "start": self.findStart,
                "end": self.findEnd,
                "draw": self.findDraw,
                "edit": self.findEdit,
            }
        }
        self.keybindings = {
            "all": {},
            "edit": {},
            "findBuffer": {},
            "find": {},
        }
        self.settings = {
            "all": {
                "visualTabWidth": 4,
                "softTabWidth": 4,
                "minimumGutterWidth": 2,
                "emptyLineFill": "~",
                "commandPromptText": "> ",
                "verticalBorder": " ",
                "horizontalBorder": " ",
                "terminalCarriageReturn": "\r",
                "terminalNewline": "\n",
                "terminalCarriageReturnNewline": "\r\n",
                "lineEnd": "unix",
                "softTabs": True,
                "showLineNumbers": True,
                "relativeLineNumbers": False,
                "showEmptyLineFill": False,
                "showTabList": True,
                "showStatusLine": True,
                "alwaysShowCommandLine": False,
                "syntaxHighlighting": False,
                "highlightCurrentLineNumber": True,
                "highlightCurrentLine": True,
            }
        }
        self.colors = {
            "all": {
                "default": self.terminal.normal,
                "lineNumber": self.terminal.gray50,
                "currentLineNumber": self.terminal.gray100_on_gray18,
                "currentLine": self.terminal.gray100_on_gray18,
                "noResults": self.terminal.gray50,
                "selection": self.terminal.on_gray25,
                "emptyLineFill": self.terminal.normal,
                "tabName": self.terminal.gray80_on_gray25,
                "currentTabName": self.terminal.gray100_on_gray40,
                "statusLine": self.terminal.gray60_on_gray25,
                "mode": self.terminal.black_on_lightblue,
                "bufferName": self.terminal.gray100_on_gray40,
                "coordinates": self.terminal.black_on_lightblue,
                "percentage": self.terminal.gray100_on_gray40,
                "commandLine": self.terminal.normal,
                "prompt": self.terminal.bold,
                "input": "",
                "message": "",
                "match": self.terminal.khaki_on_gray40,
                "cursor": self.terminal.reverse,
                "workingDirectory": self.terminal.italic,
            }
        }
        self.setup()

    #### Utility methods ####
    @property
    def currentBuffer(self):
        # Returns the current buffer being edited (if any).
        return self.buffers[self.currentBufferIndex] if self.currentBufferIndex < len(self.buffers) else None

    def getSetting(self, setting):
        # Returns the value of the given setting or None if it doesn't exist.
        return self.settings[self.profile].get(setting, self.settings["all"].get(setting, None))

    def runAction(self, action, *args):
        # Runs the action for the current mode with the given name with the given args.
        return self.actions[self.mode].get(action, self.actions["all"].get(action, None))(*args)

    def addKeybinding(self, modes, sequence, action):
        # Binds the given sequence to the given action in the given modes.
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

    def bufferName(self, buffer):
        # Returns the formatted full name of the given buffer.
        name = "ro " if buffer.isReadOnly else "+ " if buffer.hasUnsavedChanges else ""
        return f"{name}{buffer.name}"# ({buffer.cursorY+1}, {buffer.cursorX+1})"

    def openFile(self, path):
        # Opens a file with the given path in a new buffer.
        try:
            if self.buffers:
                self.currentBufferIndex += 1
            self.buffers.insert(self.currentBufferIndex, Buffer(os.path.relpath(path, self.workingDirectory)))
            self.buffers[self.currentBufferIndex].readFromFile(os.path.join(self.workingDirectory, path))
        except:
            self.commandPrompt = f"Error opening file '{path}'"

    def applyColor(self, color, text):
        # Applies the given color to the text.
        if color == "":
            return text
        else:
            color = self.colors[self.colorscheme][color]
            return color + text if isinstance(color, str) else color(text)

    def format(self, color, text, width=None, end="", clear=True):
        # Returns the given text in the given color with the given end type.
        end = {"r": self.getSetting("terminalCarriageReturn"), "n": self.getSetting("terminalNewline"), "rn": self.getSetting("terminalCarriageReturnNewline"), "": ""}[end]
        text = str(text)
        text = self.applyColor(color, text[:width] if width is not None and len(text) > width else text)
        return text + end + (self.terminal.normal if clear else "")

    def print(self, color, text, width=None, end="", clear=True):
        # Adds the given text to the editor's current frame to be printed.
        self.output.append(self.format(color, text, width, end, clear))
        return min(len(text), width or len(text))

    def move(self, x, y):
        # Adds the sequence to move the cursor to the given coordinates to the editor's display buffer.
        self.output.append(self.terminal.move_yx(y, x))

    def moveUp(self, amount=1):
        # Moves the terminal cursor up by `amount`.
        if amount:
            self.output.append(self.terminal.move_up(amount))
        
    def moveDown(self, amount=1):
        # Moves the terminal cursor down by `amount`.
        if amount:
            self.output.append(self.terminal.move_down(amount))

    def moveLeft(self, amount=1):
        # Moves the terminal cursor left by `amount`.
        if amount:
            self.output.append(self.terminal.move_left(amount))
        
    def moveRight(self, amount=1):
        # Moves the terminal cursor right by `amount`.
        if amount:
            self.output.append(self.terminal.move_right(amount))

    def adjustScroll(self, scrollX, scrollY, width, gutterWidth, height):
        if self.cursorX < self.scrollX:
            self.scrollX = self.cursorX
        elif self.cursorX >= self.scrollX + width - gutterWidth - 1:
            self.scrollX = self.cursorX - width + gutterWidth + 2

        if self.cursorY < self.scrollY:
            self.scrollY = self.cursorY
        elif self.cursorY >= self.scrollY + height - 1:
            self.scrollY = self.cursorY - height + 1

    def highlightMatches(self, text, searchTerm):
        # Returns the text with any matches of the search term highlighted.
        return text.replace(searchTerm, self.terminal.normal + self.applyColor("match", searchTerm) + self.terminal.normal)

    def drawTabLine(self, x, y, width):
        # Draws the list of open tabs.
        if self.getSetting("showTabList"):
            self.move(x, y)
            for i, buffer in enumerate(self.buffers):
                width -= self.print("currentTabName" if i == self.currentBufferIndex else "tabName", f" {i+1} {self.bufferName(buffer)} ", width)
            self.print("statusLine", "".ljust(width))
            return y + 1
        else:
            return y

    def drawBuffer(self, buffer, x, y, width, height, showCursor=True, showLineNumbers=True, relativeLineNumbers=False, showEmptyLineFill=False, \
    syntaxHighlighting=True, highlightCurrentLine=True, highlightMatches=False):
        # Draws the given buffer.
        endY = y + height
        self.move(x, y)
        gutterWidth = min(len(str(buffer.numberOfLines)), self.getSetting("minimumGutterWidth")) + 1
        buffer.adjustScroll(width, gutterWidth, height)
        for i, line in enumerate(buffer.lines[buffer.scrollY:]):
            if height == 0:
                break
            isCurrentLine = highlightCurrentLine and i == buffer.cursorY - buffer.scrollY
            lineWidth = width
            # Draw the line number if needed.
            if showLineNumbers:
                if relativeLineNumbers and not isCurrentLine:
                    lineNumber = abs(buffer.cursorY - buffer.scrollY - i)
                else:
                    lineNumber = buffer.scrollY + i + 1
                lineWidth = width - self.print("currentLineNumber" if isCurrentLine else "lineNumber", f"{lineNumber:>{gutterWidth}} ", width)
            # Draw the line itself.
            line = line[buffer.scrollX:].ljust(lineWidth)
            if highlightMatches and self.currentBuffer.searchTerm:
                line = self.highlightMatches(line, self.currentBuffer.searchTerm)
            self.print("", line, end="r")
            #self.print("currentLine" if isCurrentLine else "default", line, lineWidth, end="r")

            selectedRange = buffer.selectedRange(buffer.scrollY + i)
            if showCursor:
                # Draw the selection.
                if buffer.isSelecting and selectedRange is not None:
                    self.moveRight(x + (gutterWidth + 1 if showLineNumbers else 0) + selectedRange[0])
                    self.print("selection", buffer.lines[buffer.scrollY + i][selectedRange[0]:selectedRange[1]] or " ", lineWidth, end="r")
                # Draw the cursor.
                if buffer.scrollY + i == buffer.cursorY:
                    self.moveRight(x + buffer.cursorX - buffer.scrollX + (gutterWidth + 1 if showLineNumbers else 0))
                    self.print("cursor", buffer.currentCharacter or " ", end="r")

            # Advance to the next line.
            self.moveDown()
            height -= 1

        # Draw the empty line fill if needed.
        if showEmptyLineFill:
            while height > 0:
                self.print("emptyLineFill", self.getSetting("emptyLineFill"), width, end="r")
                self.moveDown()
                height -= 1
        return endY

    def drawStatusLine(self, buffer, x, y, width):
        # Draws the status bar describing the state of the buffer.
        self.move(x, y)
        # Print the background.
        self.print("statusLine", "".ljust(width), width, end="r")
        # Print the mode.
        self.print("mode", f" {self.mode} ", width)
        # Print the buffer name.
        self.print("bufferName", f" {self.bufferName(buffer)} ", width, end="r")
        # Print the coordinates.
        coordinates = f" {self.currentBuffer.cursorY+1}, {self.currentBuffer.cursorX+1} " 
        self.move(x + width - len(coordinates), y)
        self.print("coordinates", coordinates, width)
        # Print the percentage.
        percentage = f" {(self.currentBuffer.cursorY+1)/self.currentBuffer.numberOfLines:.0%}, {self.currentBuffer.numberOfLines}L "
        self.moveLeft(len(coordinates) + len(percentage) - 1)
        self.print("percentage", percentage, width)
        # Print the other info.
        info = self.currentKeySequence if self.currentKeySequence.count(" ") > 1 else ""
        info += f"     {self.language} | utf-8 | {self.getSetting('lineEnd')} "
        self.moveLeft(len(info) + len(percentage))
        self.print("statusLine", info, width, end="r")
        return y + 1

    def drawCommandLine(self, x, y, width):
        # Draws the command line.
        if self.commandPrompt or self.getSetting("alwaysShowCommandLine"):
            self.move(x, y)
            self.print("commandLine", self.commandPrompt, width)
            return y + 1
        else:
            return y

    def drawSuggestionList(self, suggestionList, x, y, width, height, showLineNumbers=True):
        # Draws a list of suggestions.
        self.move(x, y)
        if suggestionList.items:
            gutterWidth = min(len(str(len(suggestionList.items))), self.getSetting("minimumGutterWidth"))
            suggestionList.adjustScroll(height)
            for i, suggestion in enumerate(suggestionList.items[suggestionList.scrollY:]):
                if height == 0:
                    break
                number, name, value = suggestion
                isCurrentLine = i + suggestionList.scrollY == suggestionList.currentItemIndex

                # Print the number.
                if showLineNumbers:
                    lineWidth = width-self.print("currentLineNumber" if isCurrentLine else "lineNumber", f"{number+1:>{gutterWidth+1}} ", width)
                else:
                    lineWidth = width

                # Print the name of the suggestion.
                self.print("currentLine" if isCurrentLine else "default", name.ljust(lineWidth), end="r")

                # Advance to the next line.
                height -= 1
                y += 1
                self.moveDown()
        else:
            self.print("noResults", "No results")
        return y + 1

    def drawPrompt(self, prompt, buffer, x, y, width, showCursor=True):
        # Draws an interactive prompt.
        self.move(x, y)
        self.print("prompt", prompt)
        self.drawBuffer(buffer, x + len(prompt), y, width - len(prompt), 1, showCursor=showCursor, showLineNumbers=False,
        syntaxHighlighting=False, highlightCurrentLine=False)
        return y + 1

    #### Event loop methods ####
    def setup(self):
        # Sets the editor up before it runs.
        self.terminal = blessed.Terminal()
        self.languages = {}
        self.extensions = {}
        self.mode = "edit"
        self.profile = "all"
        self.colorscheme = "all"
        self.language = "text"
        self.buffers = []
        self.currentBufferIndex = self.previousBufferIndex = 0
        self.activeBuffer = self.currentBuffer
        self.findPrompt = ""
        self.findInput = Buffer()
        self.replaceInput = Buffer()
        self.commandInput = Buffer()
        self.searchResults = SuggestionList()
        #self.autocompleteSuggestions = SuggestionList()
        self.commandPrompt = ""
        self.output = []
        self.workingDirectory = os.getcwd()
        self.currentKeybindings = self.keybindings[self.mode]
        self.currentGlobalKeybindings = self.keybindings["all"]
        self.currentKeySequence = ""
        self.keepRunning = True
        self.redraw = True
        self.clearCommandPrompt = False

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
            if self.clearCommandPrompt:
                self.commandPrompt = ""
                self.clearCommandPrompt = False

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
            print("".join(self.output), end="", flush=True)
            self.output = []
            self.redraw = False

    def run(self, *args):
        # Runs the editor until the user quits.
        self.setup()
        self.openFile("example.txt")
        self.openFile("notes.txt")
        self.openFile("src/buffer.py")
        self.openFile("src/editor.py")
        self.openFile("src/__main__.py")
        self.openFile("src/suggestionlist.py")
        self.currentBufferIndex = 0
        self.setMode("edit")()
        with self.terminal.fullscreen(), self.terminal.raw(), self.terminal.hidden_cursor():
            while self.keepRunning:
                self.draw()
                self.update()
        print(self.terminal.home + self.terminal.clear, end="")

    #### Mode actions ####
    def defaultStart(self):
        pass

    def defaultEnd(self):
        pass

    def defaultDraw(self, x, y, width, height):
        pass

    def defaultEdit(self):
        pass

    def editStart(self):
        self.activeBuffer = self.currentBuffer

    def editDraw(self, x, y, width, height):
        offset = self.getSetting("showTabList") + self.getSetting("showStatusLine") + (len(self.commandPrompt) != 0 or self.getSetting("alwaysShowCommandLine")) \
            + int(self.currentBuffer.searchTerm != "")
        y = self.drawTabLine(x, y, width)
        y = self.drawBuffer(self.currentBuffer, x, y, width, height - offset, showLineNumbers=self.getSetting("showLineNumbers"), \
            relativeLineNumbers=self.getSetting("relativeLineNumbers"), showEmptyLineFill=self.getSetting("showEmptyLineFill"), \
            highlightMatches=True)
        if self.getSetting("showStatusLine"):
            y = self.drawStatusLine(self.currentBuffer, x, y, width)
        
        if self.findInput.currentLine:
            y = self.drawPrompt(self.findPrompt, self.findInput, x, y, width, showCursor=False)
        self.drawCommandLine(x, y, width)

    def findBufferStart(self):
        self.findPrompt = "Find buffer: "
        self.findInput.clear()
        self.activeBuffer = self.findInput
        self.oldBufferIndex = self.currentBufferIndex
        self.searchResults.clear()
        term = self.findInput.currentLine.strip()
        self.searchResults.items = [(i, f"{buffer.name} {buffer.coordinates}", buffer) for i, buffer in enumerate(self.buffers) if term in buffer.name]
        self.currentBufferIndex = self.searchResults.currentItem[0]

    def findBufferEnd(self):
        del self.oldBufferIndex
        self.findInput.clear()
        self.searchResults.clear()

    def findBufferDraw(self, x, y, width, height):
        y = self.drawTabLine(x, y, width)
        y = self.drawBuffer(self.currentBuffer, x, y, width, height*4//5 - 2, showLineNumbers=self.getSetting("showLineNumbers"), \
            relativeLineNumbers=self.getSetting("relativeLineNumbers"), showEmptyLineFill=self.getSetting("showEmptyLineFill"))
        y = self.drawStatusLine(self.currentBuffer, x, y, width)
        y = self.drawPrompt(self.findPrompt, self.findInput, x, y, width)
        self.drawSuggestionList(self.searchResults, x, y, width, height//5)

    def findBufferEdit(self):
        term = self.findInput.currentLine.strip()
        self.searchResults.clear()
        self.searchResults.items = [(i, f"{buffer.name} {buffer.coordinates}", buffer) for i, buffer in enumerate(self.buffers) if term in buffer.name]
        self.searchResults.currentItemIndex = self.searchResults.scrollY = 0
        self.currentBufferIndex = self.searchResults.currentItem[0] if self.searchResults.items else self.oldBufferIndex

    def findStart(self):
        self.findPrompt = "Find: "
        self.activeBuffer = self.findInput
        self.currentBuffer.find(self.activeBuffer.currentLine)
        self.redraw = True
        self.clearCommandPrompt = True
        
    def findEnd(self):
        pass

    def findDraw(self, x, y, width, height):
        offset = self.getSetting("showTabList") + self.getSetting("showStatusLine") + (len(self.commandPrompt) != 0 or self.getSetting("alwaysShowCommandLine"))
        y = self.drawTabLine(x, y, width)
        y = self.drawBuffer(self.currentBuffer, x, y, width, height - offset - 1, showLineNumbers=self.getSetting("showLineNumbers"), \
            relativeLineNumbers=self.getSetting("relativeLineNumbers"), showEmptyLineFill=self.getSetting("showEmptyLineFill"), \
            highlightMatches=True)
        if self.getSetting("showStatusLine"):
            y = self.drawStatusLine(self.currentBuffer, x, y, width)
        y = self.drawPrompt(self.findPrompt, self.findInput, x, y, width)
        self.drawCommandLine(x, y, width)

    def findEdit(self):
        self.currentBuffer.find(self.activeBuffer.currentLine)
        self.redraw = True

    #### Bindable actions ####
    def setMode(self, mode):
        # Returns a function that enters the given mode.
        def run(key=None):
            self.runAction("end")
            self.mode = mode
            self.currentKeybindings = self.keybindings[self.mode]
            self.currentGlobalKeybindings = self.keybindings["all"]
            self.runAction("start")
        return run

    def quit(self, key=None):
        # Exits the editor if no buffers have unsaved changes.
        if any(buffer.hasUnsavedChanges for buffer in self.buffers):
            self.commandPrompt = "A buffer has unsaved changes. Press Ctrl e to exit without saving."
            self.redraw = True
            self.clearCommandPrompt = True
        else:
            self.keepRunning = False

    def exit(self, key=None):
        # Exits the editor regardless of any unsaved changes.
        self.keepRunning = False

    def tabLeft(self, key=None):
        # Selects the tab to the left.
        if self.buffers:
            if self.currentBufferIndex:
                self.currentBufferIndex -= 1
            else:
                self.currentBufferIndex = len(self.buffers) - 1
            self.activeBuffer = self.currentBuffer
            self.redraw = True

    def tabRight(self, key=None):
        # Selects the tab to the right.
        if self.buffers:
            if self.currentBufferIndex < len(self.buffers) - 1:
                self.currentBufferIndex += 1
            else:
                self.currentBufferIndex = 0
            self.activeBuffer = self.currentBuffer
            self.redraw = True

    def selectNextSearchResult(self, key=None):
        # Selects the next search suggestion.
        if self.searchResults.isAtEnd and self.searchResults.scrollY < self.searchResults.numberOfItems - 1:
            self.searchResults.scrollY += 1

        if self.searchResults.items:
            self.searchResults.nextItem()
            self.redraw = True

    def selectPreviousSearchResult(self, key=None):
        # Selects the previous search suggestion.
        if self.searchResults.scrollY > 0 and self.searchResults.currentItemIndex > self.searchResults.scrollY:
            self.searchResults.scrollY -= 1

        if self.searchResults.items:
            self.searchResults.previousItem()
            self.redraw = True

    def nextBufferSearchResult(self, key=None):
        # Selectes the next search suggestion and switwches to the buffer described by it.
        self.selectNextSearchResult(key)
        self.currentBufferIndex = self.searchResults.currentItem[0]

    def previousBufferSearchResult(self, key=None):
        # Selects the previous search suggestion and switches to the buffer described by it.
        self.selectPreviousSearchResult(key)
        self.currentBufferIndex = self.searchResults.currentItem[0]

    def selectBufferSearchResult(self, key=None):
        # Switches to the buffer described by the current search result.
        if self.searchResults.numberOfItems:
            self.currentBufferIndex = self.searchResults.currentItem[0]
            self.setMode("edit")()

    def cancelBufferSearch(self, key=None):
        # Cancels searching for a buffer and goes back to the previous buffer.
        self.currentBufferIndex = self.oldBufferIndex
        self.activeBuffer = self.currentBuffer
        self.setMode("edit")()

    def cursorNextSearchResult(self, key=None):
        # Moves the cursor to the next occurrence of the pattern in the current buffer.
        self.currentBuffer.cursorNextOccurrenceRight()
        self.redraw = True

    def cursorPreviousSearchResult(self, key=None):
        # Moves the cursor to the previous occurrence of the pattern in the current buffer.
        self.currentBuffer.cursorNextOccurrenceLeft()
        self.redraw = True

    def confirmSearch(self, key=None):
        # Confirms the search pattern.
        self.currentBuffer.searchTerm = self.findInput.currentLine
        self.setMode("edit")()

    def cancelSearch(self, key=None):
        # Cancels searching for a pattern in the current buffer.
        self.activeBuffer = self.currentBuffer
        self.currentBuffer.cancelFind()
        self.findInput.clear()
        self.setMode("edit")()

    def cursorLineUp(self, key):
        # Moves the current cursor one line up.
        if self.activeBuffer.scrollY > 0 and self.activeBuffer.scrollY > self.activeBuffer.cursorY:
            self.activeBuffer.scrollY = self.activeBuffer.cursorY
        self.activeBuffer.cursorLineUp()
        self.redraw = True

    def cursorLineDown(self, key):
        # Moves the current cursor one line down.
        if self.activeBuffer.isAtEnd and self.activeBuffer.scrollY < self.activeBuffer.numberOfLines - 1:
            self.activeBuffer.scrollY += 1
        self.activeBuffer.cursorLineDown()
        self.redraw = True

    def cursorLineBegin(self, key):
        # Moves the cursor to the beginning of the line.
        self.activeBuffer.cursorLineBegin()
        self.redraw = True

    def cursorLineEnd(self, key):
        # Moves the cursor to the end of the line.
        self.activeBuffer.cursorLineEnd()
        self.redraw = True

    def cursorCharacterLeft(self, key):
        # Moves the current cursor one character left.
        self.activeBuffer.cursorCharacterLeft()
        self.redraw = True

    def cursorCharacterRight(self, key):
        # Moves the current cursor one character right.
        self.activeBuffer.cursorCharacterRight()
        self.redraw = True

    def cursorWORDLeft(self, key):
        # Moves the cursor one WORD left.
        self.activeBuffer.cursorWORDLeft()
        self.redraw = True

    def cursorWORDRight(self, key):
        # Moves the cursor one WORD right.
        self.activeBuffer.cursorWORDRight()
        self.redraw = True

    def cursorWORDEnd(self, key):
        # Moves the cursor to the end of the current WORD.
        self.activeBuffer.cursorWORDEnd()
        self.redraw = True

    def insertCharacter(self, key):
        # Inserts the given character into the current buffer.
        self.activeBuffer.insert(" " if key == "Space" else str(key))
        self.runAction("edit")
        self.redraw = True

    def insertLineAbove(self, key):
        # Inserts a new line above the cursor.
        self.activeBuffer.insertLineAbove()
        self.runAction("edit")
        self.redraw = True

    def insertLineBelow(self, key):
        # Inserts a new line above the cursor.
        self.activeBuffer.insertLineBelow()
        self.runAction("edit")
        self.redraw = True

    def deleteCharacterLeft(self, key):
        # Deletes one character left.
        self.activeBuffer.deleteCharacterLeft()
        self.runAction("edit")
        self.redraw = True

    def deleteCharacterRight(self, key):
        # Deletes one character right.
        self.activeBuffer.deleteCharacterRight()
        self.runAction("edit")
        self.redraw = True

    def deleteLine(self, key):
        # Delete the current line.
        self.activeBuffer.deleteLine()
        self.runAction("edit")
        self.redraw = True

    def splitLine(self, key):
        # Splits the current line.
        self.activeBuffer.splitLine()
        self.runAction("edit")
        self.redraw = True

    def toggleSelect(self, key):
        # Starts/stops selecting text.
        self.activeBuffer.toggleSelect()
        self.redraw = True

