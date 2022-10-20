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
        }
        self.keybindings = {
            "all": {},
            "edit": {},
            "findBuffer": {},
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
                "mode": self.terminal.black_on_skyblue,
                "bufferName": self.terminal.gray100_on_gray40,
                "coordinates": self.terminal.black_on_skyblue,
                "percentage": self.terminal.gray100_on_gray40,
                "commandLine": self.terminal.normal,
                "prompt": self.terminal.bold,
                "input": "",
                "message": "",
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
            self.commandPrompt = "error"

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
    syntaxHighlighting=True, highlightCurrentLine=True):
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
            self.print("currentLine" if isCurrentLine else "default", line[buffer.scrollX:].ljust(lineWidth), lineWidth, end="r")

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
        self.print("mode", f" {self.mode.upper()} ", width)
        # Print the buffer name.
        self.print("bufferName", f" {self.bufferName(buffer)} ", width, end="r")
        # Print the coordinates.
        coordinates = f" {self.currentBuffer.cursorY+1}, {self.currentBuffer.cursorX+1} " 
        self.move(x + width - len(coordinates), y)
        self.print("coordinates", coordinates, width)
        # Print the percentage.
        percentage = f" {self.currentBuffer.cursorY/self.currentBuffer.numberOfLines:.0%}, {self.currentBuffer.numberOfLines}L "
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
                    lineWidth = width-self.print("currentLineNumber" if isCurrentLine else "lineNumber", f"{number:>{gutterWidth+1}} ", width)
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

    def drawPrompt(self, prompt, buffer, x, y, width, height, showCursor=True):
        # Draws an interactive prompt.
        self.move(x, y)
        self.print("prompt", prompt)
        self.drawBuffer(buffer, x + len(prompt), y, width - len(prompt), height, showCursor=showCursor, showLineNumbers=False,
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
        self.currentBufferIndex = 1
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
        offset = self.getSetting("showTabList") + self.getSetting("showStatusLine") + (len(self.commandPrompt) != 0 or self.getSetting("alwaysShowCommandLine"))
        y = self.drawTabLine(x, y, width)
        y = self.drawBuffer(self.currentBuffer, x, y, width, height - offset, showLineNumbers=self.getSetting("showLineNumbers"), \
            relativeLineNumbers=self.getSetting("relativeLineNumbers"), showEmptyLineFill=self.getSetting("showEmptyLineFill"))
        if self.getSetting("showStatusLine"):
            y = self.drawStatusLine(self.currentBuffer, x, y, width)
        self.drawCommandLine(x, y, width)

    def findBufferStart(self):
        self.findInput.clear()
        self.activeBuffer = self.findInput
        self.oldBufferIndex = self.currentBufferIndex
        self.searchResults.clear()
        term = self.findInput.currentLine.strip()
        self.searchResults.items = [(i, buffer.name, buffer) for i, buffer in enumerate(self.buffers) if term in buffer.name]
        self.currentBufferIndex = self.searchResults.currentItem[0]

    def findBufferEnd(self):
        del self.oldBufferIndex
        self.findInput.clear()
        self.searchResults.clear()

    def findBufferDraw(self, x, y, width, height):
        y = self.drawBuffer(self.currentBuffer, x, y, width, height*4//5 - 2, showLineNumbers=self.getSetting("showLineNumbers"), \
            relativeLineNumbers=self.getSetting("relativeLineNumbers"), showEmptyLineFill=self.getSetting("showEmptyLineFill"))
        y = self.drawStatusLine(self.currentBuffer, x, y, width)
        y = self.drawPrompt("Find buffer: ", self.findInput, x, y, width, height)
        self.drawSuggestionList(self.searchResults, x, y, width, height//5)

    def findBufferEdit(self):
        term = self.findInput.currentLine.strip()
        self.searchResults.clear()
        self.searchResults.items = [(i, buffer.name, buffer) for i, buffer in enumerate(self.buffers) if term in buffer.name]
        self.searchResults.currentItemIndex = self.searchResults.scrollY = 0
        self.currentBufferIndex = self.searchResults.currentItem[0] if self.searchResults.items else self.oldBufferIndex

    #### Bindable actions ####
    def setMode(self, mode):
        # Returns a function that enters the given mode.
        def run(key=None):
            self.runAction("end")
            self.mode = mode
            self.runAction("start")
        return run

    def quit(self, key=None):
        # Exits the editor if no buffers have unsaved changes.
        if any(buffer.hasUnsavedChanges for buffer in self.buffers):
            self.commandPrompt = "A buffer has unsaved changes. Press Ctrl e to exit without saving."
            self.redraw = True
            self.clearCommandPrompt = True

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
            self.redraw = True

    def tabRight(self, key=None):
        # Selects the tab to the right.
        if self.buffers:
            if self.currentBufferIndex < len(self.buffers) - 1:
                self.currentBufferIndex += 1
            else:
                self.currentBufferIndex = 0
            self.redraw = True

    def nextSearchResult(self, key=None):
        # Selects the next search suggestion.
        if self.searchResults.isAtEnd and self.searchResults.scrollY < self.searchResults.numberOfItems - 1:
            self.searchResults.scrollY += 1

        if self.searchResults.items:
            self.searchResults.nextItem()
            self.redraw = True

    def previousSearchResult(self, key=None):
        # Selects the previous search suggestion.
        if self.searchResults.scrollY > 0 and self.searchResults.currentItemIndex > self.searchResults.scrollY:
            self.searchResults.scrollY = self.searchResults.currentItemIndex

        if self.searchResults.items:
            self.searchResults.previousItem()
            self.redraw = True

    def nextBufferSearchResult(self, key=None):
        # Selectes the next search suggestion and switwches to the buffer described by it.
        self.nextSearchResult(key)
        self.currentBufferIndex = self.searchResults.currentItem[0]

    def previousBufferSearchResult(self, key=None):
        # Selects the previous search suggestion and switches to the buffer described by it.
        self.previousSearchResult(key)
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





"""
class VerticalSplitView:
    def __init__(self, children, parent=None, widths=None):
        self.children = children
        self.parent = parent
        self.widths = [] if widths is None else widths

    @property
    def name(self):
        return f"{self.children[0].name}"

    def drawVerticalLine(self, editor, x, y, height):
        border = editor.getSetting("verticalBorder")
        for i in range(y, y + height):
            editor.print("verticalBorder", border, x, i, width=len(border))

    def draw(self, editor, x, y, width, height):
        if self.widths:
            for i, child in enumerate(self.children):
                child.draw(editor, x, y, self.widths[i], height)
                if i < len(self.children) - 1:
                    self.drawVerticalLine(editor, x + self.widths[i], y, height)
                x += self.widths[i] + 1
        else:
            childWidth = width//len(self.children)
            for i, child in enumerate(self.children[:-1]):
                child.draw(editor, x + childWidth*i, y, childWidth - 1, height)
                self.drawVerticalLine(editor, x + childWidth*(i + 1) - 1, y, height)
            self.children[-1].draw(editor, x + childWidth*(len(self.children) - 1), y, width - childWidth*(len(self.children) - 1), height)


class HorizontalSplitView:
    def __init__(self, children, parent=None, heights=None):
        self.children = children
        self.parent = parent
        self.heights = [] if heights is None else heights

    @property
    def name(self):
        return f"{self.children[0].name}"

    def draw(self, editor, x, y, width, height):
        if self.heights:
            for i, child in enumerate(self.children):
                child.draw(editor, x, y, width, self.heights[i])
                y += self.heights[i]
        else:
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
        return f"{self.children[0].name}"

    def draw(self, editor, x, y, width, height):
        if editor.getSetting("showTabList"):
            tabX = x
            for i, child in enumerate(self.children):
                tab = f"  {child.name}  "
                editor.print("currentTabName" if self.currentTab == i else "tabName", tab, tabX, y, width)
                tabX += len(tab)
            editor.print("tabName", "".ljust(width - tabX + x), tabX, y, width - tabX + x)
        self.children[self.currentTab].draw(editor, x, y + 1, width, height - 1)


class BufferView:
    def __init__(self, buffer, parent=None):
        self.buffer = buffer
        self.parent = parent
        self.isActive = False
        self.showCursor = False
        self.clear()

    @property
    def name(self):
        return self.prefix + self.buffer.name

    @property
    def prefix(self):
        return "+ " if self.buffer.hasUnsavedChanges else "ro " if self.buffer.isReadonly else ""

    @property
    def statusLine(self):
        return f"{self.prefix}{self.buffer.name} ({self.buffer.cursorY + 1}, {self.buffer.cursorX + 1})"

    def clear(self):
        self.scrollX, self.scrollY = 0, 0
        self.gutterWidth = -1

    def adjustScroll(self, width, height):
        if self.buffer.cursorX < self.scrollX:
            self.scrollX = self.buffer.cursorX
        elif self.buffer.cursorX >= self.scrollX + width - self.gutterWidth - 1:
            self.scrollX = self.buffer.cursorX - width + self.gutterWidth + 2

        if self.buffer.cursorY < self.scrollY:
            self.scrollY = self.buffer.cursorY
        elif self.buffer.cursorY >= self.scrollY + height - 1:
            self.scrollY = self.buffer.cursorY - height + 2

    def drawBuffer(self, editor, x, y, width, height):
        self.gutterWidth = max(editor.getSetting("minimumGutterWidth"), len(str(self.buffer.numberOfLines)))
        self.adjustScroll(width, height)
        originalY = y

        # Draw the lines and line numbers.
        for i, line in enumerate(self.buffer.lines[self.scrollY:]):
            if height <= 1:
                break

            # Draw the line number if needed.
            if editor.getSetting("showLineNumbers"):
                lineNumber = abs(self.buffer.cursorY - self.scrollY - i) if editor.getSetting("relativeLineNumbers") and i != self.buffer.cursorY - self.scrollY else self.scrollY + i + 1
                editor.print("currentLineNumber" if self.scrollY + i == self.buffer.cursorY else "lineNumber", f"{lineNumber:<{self.gutterWidth}} " \
                        if i == self.buffer.cursorY - self.scrollY else f"{lineNumber:>{self.gutterWidth}}", x, y, width)

            # Draw the line.
            line = line[self.scrollX:].ljust(width-self.gutterWidth-1)
            editor.print("currentLine" if self.scrollY + i == self.buffer.cursorY else "", line, x+self.gutterWidth+1, y, width-self.gutterWidth-1)
            if self.showCursor and self.buffer.selectedRange(self.scrollY + i) is not None:
                start, end = self.buffer.selectedRange(self.scrollY + i)
                editor.print("selection", line[start:end] if line[start:end] else " ", x + self.gutterWidth + 1 + start, y, width - self.gutterWidth - 1)
            
            # Progress to the next line.
            y += 1
            height -= 1

        # Draw the empty lines.
        while height > 1:
            editor.print("emptyLineFill", editor.getSetting("emptyLineFill"), x, y, width)
            y += 1
            height -= 1

        # Draw the statusline.
        editor.print("currentStatusLine" if self.isActive or self.showCursor else "statusLine", self.statusLine.ljust(width), x, y, width)

        # Draw the cursor.
        if self.showCursor:
            editor.print("cursor" if self.isActive else "inactiveCursor", self.buffer.currentCharacter or " ", x + self.gutterWidth + 1 + self.buffer.cursorX - self.scrollX, originalY + self.buffer.cursorY - self.scrollY, 1)


class Prompt:
    def __init__(self, prompt, parent=None):
        self.prompt = prompt
        self.parent = parent
        self.input = Buffer("*prompt*", allowNewLines=False)
        self.isActive = False
        self.scrollX = 0
        self.clear()

    @property
    def name(self):
        return self.input.name

    def clear(self):
        self.input.clear()

    def adjustScroll(self, width):
        if self.input.cursorX < self.scrollX:
            self.scrollX = self.input.cursorX
        elif self.input.cursorX >= self.scrollX + width - len(self.prompt):
            self.scrollX = self.input.cursorX - width + len(self.prompt) + 1
        
    def draw(self, editor, x, y, width, height):
        self.adjustScroll(width)
        editor.print("prompt", self.prompt, x, y, width, end="")
        editor.print("input", self.input.currentLine[self.scrollX:], x + len(self.prompt), y, width - len(self.prompt), end="r")
        if self.isActive:
            line = self.input.currentLine
            if self.input.selectedRange(0) is not None:
                start, end = self.input.selectedRange(0)
                editor.print("selection", line[start:end] if line[start:end] else " ", x - self.scrollX + start + len(self.prompt), y, width)
            editor.print("cursor", self.input.currentCharacter or " ", x - self.scrollX + len(self.prompt) + self.input.cursorX, y, 1)


class Message:
    def __init__(self, text, parent=None, format="message"):
        self.text = text
        self.parent = parent
        self.format = format

    def draw(self, editor, x, y, width, height):
        editor.print(self.format, self.text, x, y, width, end="r")


class ListView:
    def __init__(self, items=[], parent=None, emptyText="No results", showLineNumbers=False):
        self.items = [] if items is None else items
        self.parent = parent
        self.emptyText = emptyText
        self.showLineNumbers = showLineNumbers
        self.cursorY = 0
        self.scrollY = 0

    @property
    def numberOfItems(self):
        return len(self.items)

    @property
    def currentItem(self):
        return self.items[self.cursorY][1] if self.numberOfItems > 0 else None

    def clear(self):
        self.items = []
        self.cursorY = 0
        self.scrollY = 0

    def adjustScroll(self, height):
        if self.cursorY < self.scrollY:
            self.scrollY = self.cursorY
        elif self.cursorY >= self.scrollY + height - 1:
            self.scrollY = self.cursorY - height + 1

    def nextItem(self, amount=1):
        for i in range(amount):
            if self.cursorY < self.numberOfItems - 1:
                self.cursorY += 1
            elif self.scrollY < self.numberOfItems - 1:
                self.scrollY += 1
            else:
                break

    def previousItem(self, amount=1):
        for i in range(amount):
            if self.cursorY > 0:
                self.cursorY -= 1
            elif self.scrollY > 0:
                self.scrollY -= 1
            else:
                break

    def draw(self, editor, x, y, width, height):
        self.adjustScroll(height)
        if self.items:
            gutterWidth = max(editor.getSetting("minimumGutterWidth"), len(str(self.numberOfItems))) + 1 if self.showLineNumbers else 0
            for i, item in enumerate(self.items[self.scrollY:]):
                if height == 0:
                    break
                else:
                    if self.showLineNumbers:
                        editor.print("currentLineNumber" if self.scrollY + i == self.cursorY else "lineNumber", f"{self.scrollY + i + 1:>{gutterWidth - 1}} ", x, y + i, width)
                    editor.print("currentListItem" if self.scrollY + i == self.cursorY else "listItem", item[0].ljust(width - gutterWidth), x + gutterWidth, y + i, width - gutterWidth, end="r" if i < self.numberOfItems - 1 else "r")
                    height -= 1
        else:
            editor.print("emptyList", self.emptyText, x, y, width, end="r")


class FilePreview:
    def __init__(self, filePath=""):
        if filePath:
            self.loadFile(filePath)
        else:
            self.filePath = ""
            self.lines = []

    def readFile(self, filePath):
        if os.access(filePath, os.R_OK):
            try:
                self.filePath = filePath
                file = open(filePath, "r")
                self.lines = [line.strip("\r\n").replace("\t", "    ") for line in file.readlines()]
                file.close()
            except:
                self.filePath = ""
                self.lines = []

    def draw(self, editor, x, y, width, height):
        gutterWidth = max(editor.getSetting("minimumGutterWidth"), len(str(len(self.lines)))) + 1 if editor.getSetting("showLineNumbers") else 0
        # Draw the preview.
        for i, line in enumerate(self.lines):
            if height == 1:
                break
            else:
                if editor.getSetting("showLineNumbers"):
                    editor.print("lineNumber", f"{i + 1:>{gutterWidth - 1}} ", x, y, width)
                editor.print("default", line.ljust(width), x + gutterWidth, y, width - gutterWidth, end="rn" if i < len(self.lines) else "r")
                y += 1
                height -= 1

        # Draw the empty lines.
        while height > 1:
            editor.print("emptyLineFill", editor.getSetting("emptyLineFill"), x, y, width)
            y += 1
            height -= 1

        # Draw the bar.
        editor.print("currentStatusLine", self.filePath.ljust(width), x, y, width)


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
                "verticalBorder": " ",
                "horizontalBorder": " ",
                "terminalCarriageReturn": "\r",
                "terminalNewline": "\n",
                "terminalCarriageReturnNewline": "\r\n",
                "softTabs": True,
                "showLineNumbers": True,
                "relativeLineNumbers": True,
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
                "lineNumber": self.terminal.gray40,
                "currentLineNumber": self.terminal.gray80_on_gray16,
                "currentLine": self.terminal.on_gray16,
                "selection": self.terminal.on_gray40,
                "emptyLineFill": self.terminal.gray40,
                "tabName": self.terminal.underline,
                "currentTabName": self.terminal.reverse_bold,
                "statusLine": self.terminal.gray65_on_gray30,
                "currentStatusLine": self.terminal.bright_white_on_gray30,
                "verticalBorder": self.terminal.on_gray30,
                "horizontalBorder": "",
                "prompt": self.terminal.bold,
                "input": "",
                "message": "",
                "cursor": self.terminal.reverse,
                "inactiveCursor": self.terminal.on_slategray,
                "emptyList": self.terminal.gray50,
                "listItem": "",
                "currentListItem": self.terminal.on_gray16,
                "workingDirectory": self.terminal.lightblue,
            }
        }
        self.keybindings = {"all": {}}
        self.actions = {"all": {"draw": self.defaultDraw}}
        self.mode = "all"
        self.setup()

    def setup(self):
        # Sets up the state of the editor.
        self.mode = self.getSetting("defaultMode")
        self.workingDirectory = os.getcwd()
        self.currentKeybindings = self.keybindings[self.mode]
        self.currentGlobalKeybindings = self.keybindings["all"]
        self.currentKeySequence = ""
        self.buffers = 2*[Buffer("*untitled*")]
        #self.rootView = VerticalSplitView([HorizontalSplitView(2*[BufferView(self.buffers[0])]), HorizontalSplitView([VerticalSplitView([BufferView(self.buffers[0]), BufferView(self.buffers[0])]), BufferView(self.buffers[0]), BufferView(self.buffers[0])])])
        #self.rootView = VerticalSplitView([BufferView(self.buffers[0]), TabView(3*[BufferView(self.buffers[0], True)], currentTab=1)])
        #self.rootView = VerticalSplitView([self.rootView, HorizontalSplitView([BufferView(self.buffers[0], True), BufferView(self.buffers[0])])])
        #self.rootView = HorizontalSplitView([self.rootView, BufferView(self.buffers[0]), VerticalSplitView([TabView(2*[BufferView(self.buffers[0])]), BufferView(self.buffers[0], True)])])
        #self.rootView = VerticalSplitView([BufferView(self.buffers[0], True), BufferView(Buffer(self.buffers[0].name, lines=self.buffers[0].lines))])

        self.rootView = BufferView(self.buffers[0], True)
        self.rootView.isActive = self.rootView.showCursor = True
        self.currentView = self.rootView
        self.previousView = self.currentView
        self.currentBuffer = self.buffers[0]
        self.output = []
        self.keepRunning = True
        self.redraw = True
        self.clearMessage = False

    def addMode(self, name, actions={}):
        # Adds a new mode with the given name and actions.
        self.settings[name] = {}
        self.keybindings[name] = {}
        self.colors[name] = {}
        self.actions[name] = {
            "begin": self.defaultBegin,
            "end": self.defaultEnd,
            "draw": self.defaultDraw,
            "edit": self.defaultEdit,
        }
        self.actions[name].update(actions)

    def removeMode(self, *modes):
        # Removes the given mode and all of its settings, colors, and keybindings.
        for mode in modes:
            del self.settings[mode], self.keybindings[mode], self.colors[mode], self.actions[mode]

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

    def removeKeybinding(modes, *bindings):
        # Removes the given keybinding(s) from the given modes.
        pass

    def getSetting(self, *settings):
        # Returns the given setting(s).
        if len(settings) == 1:
            return self.settings[self.mode].get(settings[0], self.settings["all"].get(settings[0], None))
        else:
            return {setting: self.getSetting(setting) for setting in settings}

    def setSetting(self, mode, setting, value):
        # Sets the given setting to the given value in the given modes.
        if isinstance(mode, list):
            for m in mode:
                self.setSetting(m, setting, value)
            return
        self.settings[mode][setting] = value

    def setSettings(self, mode, settings):
        # Sets the given settings in the given modes.
        if isinstance(mode, list):
            for m in mode:
                self.setSettings(m, settings)
            return
        self.settings[mode].update(settings)

    def removeSetting(self, mode, *settings):
        # Removes the given setting(s).
        if isinstance(mode, list):
            for m in mode:
                self.removeSetting(m, settings)
            return

        for setting in settings:
            if setting in self.settings[mode]:
                del self.settings[mode][setting]

    def getColor(self, *colors):
        # Returns the given color(s).
        if len(colors) == 1:
            return self.colors[self.mode].get(colors[0], self.colors["all"].get(colors[0], None))
        else:
            return {color: self.getColor(color) for color in colors}

    def setColor(self, mode, textType, color):
        # Sets the given color.
        self.colors[mode][textType] = color

    def setColors(self, mode, colors):
        # Sets the given colors.
        self.colors[mode].update(colors)

    def removeColor(self, mode, *colors):
        # Removes the given color(s) from the editor.
        for color in colors:
            if color in self.colors[mode]:
                del self.colors[mode][color]

    def runAction(self, action, *args):
        # Runs the given action for this mode and returns the value if any.
        return self.actions[self.mode].get(action, self.actions["all"].get(action, None))(*args)

    def applyColor(self, color, text):
        # Applies the given color to the given text
        if color == "":
            return text
        else:
            color = self.getColor(color)
            return color + text if isinstance(color, str) else color(text)

    def format(self, color, text, x=None, y=None, width=None, end=""):
        # Returns the given text in the given color with the given end type.
        end = {"r": self.getSetting("terminalCarriageReturn"), "n": self.getSetting("terminalNewline"), "rn": self.getSetting("terminalCarriageReturnNewline"), "": ""}[end]
        text = str(text)
        text = self.applyColor(color, text[:width] if width is not None and width < len(text) else text)
        if x is not None:
            return self.terminal.move_yx(y, x) + text + end + self.terminal.normal
        else:
            return text + end + self.terminal.normal

    def print(self, color, text, x=None, y=None, width=None, end=""):
        # Adds the given text to the editor's current frame to be printed.
        self.output.append(self.format(color, text, x, y, width, end))

    def showMessage(self, text):
        # Shows the given message at the bottom of the screen.
        self.rootView = HorizontalSplitView([self.rootView, Message(text)], heights=[self.terminal.height - 1, 1])
        self.redraw = True
        self.clearMessage = True
        self.draw()

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
            if self.clearMessage:
                self.rootView = self.rootView.children[0]
                self.clearMessage = False

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
        # Starts the editor.
        self.setup()
        self.setMode("edit")()
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

    def defaultEdit(self):
        # The default behavior when an edit is made to the current buffer.
        pass

    def openFileBegin(self):
        # Called when openFile mode begins.
        self.openFileView = VerticalSplitView([HorizontalSplitView([Prompt("Find file: "), Message(self.workingDirectory, format="workingDirectory"), ListView([], showLineNumbers=False)], \
                heights=[1, 1, self.terminal.height - 2]), FilePreview()], widths=[self.terminal.width//3, self.terminal.width*2//3 - 0])
        prompt = self.openFileView.children[0].children[0]
        prompt.isActive = True
        self.currentBuffer = prompt.input
        self.openFileEdit()
        self.redraw = True
        self.draw()

    def openFileEnd(self):
        # Called when openFile mode ends.
        del self.openFileView
        self.redraw = True

    def openFileDraw(self, x, y, width, height):
        # Called when the screen is drawn in openFile mode.
        fileList = self.openFileView.children[0].children[2]
        prompt = self.openFileView.children[0].children[0]
        message = self.openFileView.children[0].children[1]
        message.text = "(" + str(fileList.cursorY + int(prompt.input.currentLine.strip() != "" and fileList.items != [])) + "/" + str(len(fileList.items) if prompt.input.currentLine.strip() else len(fileList.items) - 1) + ") " 
        message.text += self.workingDirectory[len(self.workingDirectory) - width:] if len(self.workingDirectory) > width else self.workingDirectory
        message.text += "/" if self.workingDirectory != "/" else ""
        self.openFileView.draw(self, x, y, width, height)

    def openFileGetSubdirectories(self, directory, depth=1):
        # Return a list of subdirectories of the given directory.
        directories = []
        for subdirectory in os.listdir(directory):
            fullPath = os.path.join(directory, subdirectory)
            relativePath = os.path.relpath(fullPath, self.workingDirectory)
            if os.path.isdir(fullPath):
                directories.append(["   " + relativePath + "/", relativePath + "/"])
                if depth and os.access(fullPath, os.R_OK):
                    directories += self.openFileGetSubdirectories(fullPath, depth-1)
            else:
                directories.append(["   " + relativePath, relativePath])
        return directories

    def openFileEdit(self):
        # Refresh the list of files.
        prompt = self.openFileView.children[0].children[0]
        fileList = self.openFileView.children[0].children[2]
        filePreview = self.openFileView.children[1]
        term = prompt.input.currentLine.strip()
        fileList.items = [] if term else [["   ..", ".."]]  
        fileList.scrollY = 0
        fileList.items += [dir for dir in self.openFileGetSubdirectories(self.workingDirectory, term.count("/")) if term in dir[0]]
        fileList.cursorY = 1 if not term and len(fileList.items) > 1 else 0
        if fileList.numberOfItems and os.path.isfile(os.path.join(self.workingDirectory, fileList.currentItem)):
            filePreview.readFile(os.path.join(self.workingDirectory, fileList.currentItem))
        elif fileList.numberOfItems and not os.path.isfile(os.path.join(self.workingDirectory, fileList.currentItem)):
            filePreview.lines = []#os.listdir(os.path.join(self.workingDirectory, fileList.currentItem))
            filePreview.filePath = ""#os.path.join(self.workingDirectory, fileList.currentItem)
        else:
            filePreview.lines = []
            filePreview.filePath = self.workingDirectory
        self.redraw = True

    def openFileNext(self, key):
        # Select the next file.
        fileList = self.openFileView.children[0].children[2]
        filePreview = self.openFileView.children[1]
        fileList.nextItem()
        if fileList.numberOfItems and os.path.isfile(os.path.join(self.workingDirectory, fileList.currentItem)):
            filePreview.readFile(os.path.join(self.workingDirectory, fileList.currentItem))
        elif fileList.numberOfItems and os.path.isdir(os.path.join(self.workingDirectory, fileList.currentItem)):
            filePreview.lines = []#os.listdir(os.path.join(self.workingDirectory, fileList.currentItem))
            filePreview.filePath = ""#os.path.join(self.workingDirectory, fileList.currentItem)
        else:
            filePreview.lines = []
            filePreview.filePath = self.workingDirectory
        self.redraw = True

    def openFilePrevious(self, key):
        # Select the previous file.
        fileList = self.openFileView.children[0].children[2]
        filePreview = self.openFileView.children[1]
        fileList.previousItem()
        if fileList.numberOfItems and os.path.isfile(os.path.join(self.workingDirectory, fileList.currentItem)):
            filePreview.readFile(os.path.join(self.workingDirectory, fileList.currentItem))
        elif fileList.numberOfItems and os.path.isdir(os.path.join(self.workingDirectory, fileList.currentItem)):
            filePreview.lines = []#os.listdir(os.path.join(self.workingDirectory, fileList.currentItem))
            filePreview.filePath = ""#os.path.join(self.workingDirectory, fileList.currentItem)
        else:
            filePreview.lines = []
            filePreview.filePath = self.workingDirectory
        self.redraw = True

    def openFileConfirm(self, key):
        # Opens the file selected.
        prompt = self.openFileView.children[0].children[0]
        fileList = self.openFileView.children[0].children[2]
        if fileList.numberOfItems:
            if fileList.currentItem == "..":
                self.workingDirectory = os.path.dirname(self.workingDirectory)
                prompt.input.clear()
                self.openFileEdit()
            elif os.path.isdir(os.path.join(self.workingDirectory, fileList.currentItem)):
                self.workingDirectory = os.path.normpath(os.path.join(self.workingDirectory, fileList.currentItem))
                prompt.input.clear()
                self.openFileEdit()
            elif os.path.isfile(os.path.join(self.workingDirectory, fileList.currentItem)):
                self.currentBuffer = self.rootView.buffer
                self.currentBuffer.readFromFile(os.path.join(self.workingDirectory, fileList.currentItem))
                self.currentBuffer.name = fileList.currentItem
                self.setMode("edit")(None)

    def openFileComplete(self, key):
        # Autocompletes the selected file.
        prompt = self.openFileView.children[0].children[0]
        fileList = self.openFileView.children[0].children[2]
        if fileList.currentItem is not None and fileList.currentItem != "..":
            prompt.input.stopSelecting()
            prompt.input.deleteLine()
            prompt.input.insert(fileList.currentItem)
            self.openFileEdit()

    def setMode(self, mode):
        # Returns a function that enters the given mode.
        def run(key=None):
            self.runAction("end")
            self.mode = mode
            self.runAction("begin")
        return run

    def quit(self, key):
        # Quits the editor.
        for buffer in self.buffers:
            if buffer.hasUnsavedChanges:
                self.showMessage("A buffer has unsaved changes. Press Ctrl e to exit without saving.")
                return
        self.keepRunning = False

    def exit(self, key):
        # Exit the editor without saving.
        self.keepRunning = False

    def cursorLineUp(self, key):
        # Moves the current cursor one line up.
        if self.currentView.scrollY > 0 and self.currentView.scrollY > self.currentBuffer.cursorY:
            self.currentView.scrollY = self.currentBuffer.cursorY
        self.currentBuffer.cursorLineUp()
        self.redraw = True

    def cursorLineDown(self, key):
        # Moves the current cursor one line down.
        if self.currentBuffer.isAtEnd and self.currentView.scrollY < self.currentBuffer.numberOfLines - 1:
            self.currentView.scrollY += 1
        self.currentBuffer.cursorLineDown()
        self.redraw = True

    def cursorLineBegin(self, key):
        # Moves the cursor to the beginning of the line.
        self.currentBuffer.cursorLineBegin()
        self.redraw = True

    def cursorLineEnd(self, key):
        # Moves the cursor to the end of the line.
        self.currentBuffer.cursorLineEnd()
        self.redraw = True

    def cursorCharacterLeft(self, key):
        # Moves the current cursor one character left.
        self.currentBuffer.cursorCharacterLeft()
        self.redraw = True

    def cursorCharacterRight(self, key):
        # Moves the current cursor one character right.
        self.currentBuffer.cursorCharacterRight()
        self.redraw = True

    def cursorWORDLeft(self, key):
        # Moves the cursor one WORD left.
        self.currentBuffer.cursorWORDLeft()
        self.redraw = True

    def cursorWORDRight(self, key):
        # Moves the cursor one WORD right.
        self.currentBuffer.cursorWORDRight()
        self.redraw = True

    def cursorWORDEnd(self, key):
        # Moves the cursor to the end of the current WORD.
        self.currentBuffer.cursorWORDEnd()
        self.redraw = True

    def insertCharacter(self, key):
        # Inserts the given character into the current buffer.
        self.currentBuffer.insert(" " if key == "Space" else str(key))
        self.runAction("edit")
        self.redraw = True

    def insertLineAbove(self, key):
        # Inserts a new line above the cursor.
        self.currentBuffer.insertLineAbove()
        self.runAction("edit")
        self.redraw = True

    def insertLineBelow(self, key):
        # Inserts a new line above the cursor.
        self.currentBuffer.insertLineBelow()
        self.runAction("edit")
        self.redraw = True

    def deleteCharacterLeft(self, key):
        # Deletes one character left.
        self.currentBuffer.deleteCharacterLeft()
        self.runAction("edit")
        self.redraw = True

    def deleteCharacterRight(self, key):
        # Deletes one character right.
        self.currentBuffer.deleteCharacterRight()
        self.runAction("edit")
        self.redraw = True

    def deleteLine(self, key):
        # Delete the current line.
        self.currentBuffer.deleteLine()
        self.runAction("edit")
        self.redraw = True

    def splitLine(self, key):
        # Splits the current line.
        self.currentBuffer.splitLine()
        self.runAction("edit")
        self.redraw = True

    def toggleSelect(self, key):
        # Starts/stops selecting text.
        self.currentBuffer.toggleSelect()
        self.redraw = True
"""
