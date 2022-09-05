import blessed
from buffer import Buffer


def untitledFileName(directory):
    # TODO: Make this append a number to the end of the file name if one already exists.
    return "example.txt"


class Editor:
    def __init__(self):
        self.keybindings = {
            "insert": {},
            "command": {},
            "number": {},
            "switchBuffer": {},
            "openFile": {},
        }
        self.settings = {
            "defaultMode": "insert",
            "visualTabWidth": 4,
            "softTabWidth": 4,
            "softTabs": False,
            "showLineNumbers": True,
            "relativeLineNumbers": False,
            "minimumGutterWidth": 2,
            "emptyLineFill": "~",
            "colorscheme": "monochrome",
        }
        self.colorschemes = {}
        self.mode = self.settings["defaultMode"]
        self.currentBindings = self.keybindings[self.mode]
        self.workingDirectory = None
        self.buffers = []
        self.currentBufferIndex = 0
        self.previousBufferIndex = 0
        self.registers = []
        self.terminal = blessed.Terminal()
        self.keepRunning = True
        self.needsRedraw = True
        self.clearCommandBuffer = False
        self.gutterWidth = self.settings["minimumGutterWidth"]
        self.pageWidth = self.terminal.width - self.gutterWidth
        self.pageHeight = self.terminal.height - 1
        self.commandBuffer = Buffer(self.pageWidth, self.pageHeight, self.settings["visualTabWidth"], self.settings["softTabWidth"])
        self.scratchBuffer = Buffer(self.pageWidth, self.pageHeight, self.settings["visualTabWidth"], self.settings["softTabWidth"])
        self.commandInProgress = ""

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

        if mode == "all":
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

    def currentBuffer(self):
        if self.buffers:
            return self.buffers[self.currentBufferIndex]
        else:
            return None

    def bufferName(self, bufferIndex):
        buffer = self.buffers[bufferIndex]
        name = str(bufferIndex) + " "
        name += "[ro] " if buffer.isReadOnly else "[+] " if buffer.hasUnsavedChanges else ""
        path = buffer.filePath
        if len(path) + len(name) > self.pageWidth:
            return name + "..." + path[self.pageWidth - len(path) - len("..."):]
        return name + path

    def newBuffer(self):
        self.buffers.insert(self.currentBufferIndex, Buffer(self.pageWidth, self.pageHeight, self.settings["visualTabWidth"], 
            self.settings["softTabWidth"]))
        self.currentBuffer().open(untitledFileName(self.workingDirectory))
        if len(self.buffers) > 1:
            self.previousBufferIndex += 1
        self.mode = self.settings["defaultMode"]
        self.needsRedraw = True

    def openInPlace(self, filePath):
        if self.buffers:
            self.currentBuffer().open(filePath)
        else:
            self.newBuffer()
            self.currentBuffer().open(filePath)
        self.needsRedraw = True

    def open(self, filePaths):
        if isinstance(filePaths, list):
            for path in filePaths:
                self.open(path)
        else:
            for buffer in self.buffers:
                if buffer.filePath == filePaths:
                    return
            self.newBuffer()
            self.openInPlace(filePaths)
        self.needsRedraw = True

    def switchToBuffer(self, bufferIndex):
        if bufferIndex != self.currentBufferIndex:
            self.previousBufferIndex = self.currentBufferIndex
            self.currentBufferIndex = bufferIndex
            self.needsRedraw = True

    def switchToPreviousBuffer(self):
        if self.currentBufferIndex != self.previousBufferIndex:
            self.currentBufferIndex = self.previousBufferIndex
            self.needsRedraw = True

    def bufferForward(self, key=None):
        if self.currentBufferIndex < len(self.buffers) - 1:
            self.currentBufferIndex += 1
            self.needsRedraw = True

    def bufferBackward(self, key=None):
        if self.currentBufferIndex > 0:
            self.currentBufferIndex -= 1
            self.needsRedraw = True

    def commandBufferPrompt(self, prompt, mode=None):
        def process(key=None):
            self.commandBuffer.close()
            self.commandBuffer.insert(prompt)
            if mode is not None:
                self.mode = mode
            else:
                self.mode = "command"
            self.needsRedraw = True
        return process

    def commandBufferInsert(self, key):
        self.commandBuffer.insert(key)
        self.needsRedraw = True

    def commandBufferDelete(self, limit=0):
        def process(key=None):
            if not (self.commandBuffer.cursorAtEnd() and self.commandBuffer.cursorX >= limit):
                self.commandBuffer.delete()
                self.needsRedraw = True
        return process

    def commandBufferDeleteLeft(self, limit=0):
        def process(key=None):
            if not (self.commandBuffer.cursorAtEnd() and self.commandBuffer.cursorX >= limit):
                self.commandBuffer.deleteCharacterLeft()
                self.needsRedraw = True
        return process

    def commandBufferCursorLeft(self, limit=0):
        def process(key=None):
            if self.commandBuffer.cursorX > limit:
                self.commandBuffer.cursorCharacterLeft()
                self.needsRedraw = True
        return process
    
    def commandBufferCursorRight(self, key=None):
        self.commandBuffer.cursorCharacterRight()
        self.needsRedraw = True

    def openFileFromCommandBuffer(self, start=0):
        def process(key=None):
            self.open(self.commandBuffer.currentLine.text[start:])
            self.mode = self.settings["defaultMode"]
            self.needsRedraw = True
        return process

    def cursorCharacterRight(self, key=None):
        self.currentBuffer().cursorCharacterRight()
        self.needsRedraw = True

    def cursorCharacterLeft(self, key=None):
        self.currentBuffer().cursorCharacterLeft()
        self.needsRedraw = True

    def cursorLineUp(self, key=None):
        self.currentBuffer().cursorLineUp()
        self.needsRedraw = True

    def cursorLineDown(self, key=None):
        self.currentBuffer().cursorLineDown()
        self.needsRedraw = True

    def insertLineAbove(self, key=None):
        self.currentBuffer().insertLineAbove()
        self.needsRedraw = True

    def insertCharacter(self, key):
        if key == "Space":
            self.currentBuffer().insert(1, " ")
        else:
            self.currentBuffer().insert(1, key)
        self.needsRedraw = True

    def delete(self, key=None):
        self.currentBuffer().delete()
        self.needsRedraw = True

    def deleteLeft(self, key=None):
        self.currentBuffer().deleteLeft()
        self.needsRedraw = True

    def deleteLine(self, key=None):
        self.currentBuffer().deleteLine()
        self.needsRedraw = True
    
    def quit(self, key=None):
        for i, buffer in enumerate(self.buffers):
            if buffer.hasUnsavedChanges:
                self.commandBuffer.close()
                self.commandBuffer.insert("A file has unsaved changes. Press Ctrl e to exit without saving.")
                self.needsRedraw = True
                self.clearCommandBuffer = True
                return
        self.keepRunning = False
        
    def exit(self, key=None):
        self.keepRunning = False

    def setMode(self, mode):
        def process(key):
            self.mode = mode
            self.commandBuffer.close()
            self.needsRedraw = True
        return process

    def draw(self):
        print(self.terminal.home + self.terminal.clear, end="")
        
        # Draw the current buffer.
        currentLine = self.currentBuffer().topLine
        self.gutterWidth = max(len(str(self.currentBuffer().numberOfLines)), self.settings["minimumGutterWidth"])
        for i in range(self.terminal.height - 1):
            if currentLine is not None:
                text = currentLine.text[self.currentBuffer().scrollX:]
                if self.settings["showLineNumbers"]:
                    print(f"{self.currentBuffer().scrollY + i + 1:>{self.gutterWidth}} ", end="")
                print(f"{text}", end="\r\n")
                currentLine = currentLine.next
            else:
                print(self.settings["emptyLineFill"], end="\r\n")

        # Draw the current key sequence.
        if self.commandInProgress:
            print(self.terminal.rjust("  " + self.commandInProgress[:-1]), end="\r")
        
        # Draw the command bar.
        if self.commandBuffer.currentLine.text:
            print(self.commandBuffer.currentLine.text, end="\r")
        else:
            print(self.bufferName(self.currentBufferIndex), end="\r")

        # Draw the command cursor.
        if self.mode in ["command", "number", "openFile"]:
            print(self.terminal.move_xy(self.commandBuffer.cursorX, self.terminal.height), end="")
            print(self.terminal.reverse(self.commandBuffer.currentLine.text[self.commandBuffer.cursorX] \
                if self.commandBuffer.cursorX < len(self.commandBuffer.currentLine.text) else " "), end="\r")
        # Draw the list of open buffers.
        elif self.mode == "switchBuffer":
            print(self.terminal.move_xy(0, self.terminal.height - len(self.buffers) - 1) + self.terminal.clear_eos, end="")
            print("-"*self.terminal.width, end="\r\n")
            # List the currentBuffers.
            for i, buffer in enumerate(self.buffers):
                if i == self.currentBufferIndex:
                    print(self.terminal.reverse, end="")
                print(f"{self.bufferName(i)}", end="\r\n" if i < len(self.buffers) - 1 else "\r")
                print(self.terminal.normal, end="")
        # Draw the buffer cursor.
        else:
            print(self.terminal.move_xy(self.currentBuffer().cursorX - self.currentBuffer().scrollX + self.gutterWidth + 1, self.currentBuffer().cursorY - self.currentBuffer().scrollY), end="")
            print(self.terminal.reverse(self.currentBuffer().currentLine.text[self.currentBuffer().cursorX] \
                if self.currentBuffer().cursorX < len(self.currentBuffer().currentLine.text) else " "), end="\r")

    def registerKeypress(self, key):
        self.currentBindings = self.currentBindings.get(key, self.currentBindings.get("Printable" if len(key) == 1 else "Unbound", self.currentBindings.get(
            "Unbound", None)))
        if self.currentBindings is None:
            self.currentBindings = self.keybindings[self.mode]
            self.commandInProgress = ""
        elif isinstance(self.currentBindings, dict):
            self.commandInProgress += key + " "
        else:
            self.currentBindings(key)
            self.currentBindings = self.keybindings[self.mode]
            self.commandInProgress = ""
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
        }
        key = self.terminal.inkey(0)

        if key:
            if self.clearCommandBuffer:
                self.commandBuffer.close()
                self.needsRedraw = True
                self.clearCommandBuffer = False
            if key.is_sequence:
                self.registerKeypress(aliases[key.name])
            elif str(key).isascii() and 0 <= ord(key) <= 31:
                self.registerKeypress("Ctrl")
                self.registerKeypress(chr(ord(key)+96).lower())
            elif key == " ":
                self.registerKeypress("Space")
            elif len(str(key)) == 1 and str(key).isascii() and str(key).isprintable():
                self.registerKeypress(str(key))

    def run(self, filePaths=None):
        if filePaths is None:
            self.open(untitledFileName(self.workingDirectory))
        else:
            for path in filePaths:
                self.open(filePaths)
        
        with self.terminal.raw(), self.terminal.keypad(), self.terminal.hidden_cursor():
            while self.keepRunning:
                if self.needsRedraw:
                    self.draw()
                    self.needsRedraw = False
                self.update()

        print(self.terminal.home + self.terminal.clear, end="")





"""
class Editor:
    def __init__(self, terminal=None):
        self.setup(terminal)

    def setup(self, terminal=None):
        self.terminal = blessed.Terminal() if terminal is None else terminal
        self.filePath = None
        self.documentBuffer = Buffer(self.terminal.width - 5, self.terminal.height - 1)
        self.commandBuffer = Buffer(self.terminal.width - 5, 1)
        self.commandBuffer.insertLineAbove()
        self.commandMode = False  # True = focused on command bar, False = focused on document.
        self.keepRunning = True
        self.needsRedraw = True
        self.readingSequence = False
        self.unsavedChanges = False
        self.readOnly = False

    def readFromFilePath(self, filePath):
        self.filePath = filePath
        if not self.documentBuffer.readFromFilePath(self.filePath):
            self.unsavedChanges = True

    def writeToFile(self):
        assert self.filePath
        self.document.writeToFilePath(self.filePath)

    def clearCommandBuffer(self):
        self.commandBuffer.deleteLine()
        self.commandMode = False

    def printToCommandBuffer(self, text):
        self.commandBuffer.insertText(text)

    def inputFromCommandBuffer(self):
        self.commandMode = True
        self.commandInput = ""

    def repeatAmount(self):
        if self.commandMode and self.commandBuffer.currentLine.text:
            return int(self.commandBuffer.currentLine.text)
        else:
            return 1

    def printCentered(self, lines):
        if len(lines) == 1:
            print(self.terminal.move_x((self.terminal.width - len(lines[0]))//2) + lines[0], end="\r\n")
        else:
            # Find the longest line length.
            maxLength = 0
            for line in lines:  
                maxLength = max(len(line), maxLength)

            print(self.terminal.move_y((self.terminal.height - len(lines))//2), end="")
            for line in lines:
                print(self.terminal.move_x((self.terminal.width - maxLength)//2) + line, end="\r\n")

    def update(self):
        key = self.terminal.inkey(0)
        if key.is_sequence:
            if key.name == "KEY_ESCAPE":
                self.readingSequence = not self.readingSequence
            elif key.name == "KEY_UP":
                self.documentBuffer.cursorUpLine()
                self.needsRedraw = True
            elif key.name == "KEY_DOWN":
                self.documentBuffer.cursorDownLine()
                self.needsRedraw = True
            elif key.name == "KEY_LEFT":
                self.documentBuffer.cursorLeftCharacter()
                self.needsRedraw = True
            elif key.name == "KEY_RIGHT":
                self.documentBuffer.cursorRightCharacter()
                self.needsRedraw = True
            elif key.name == "KEY_ENTER":
                self.documentBuffer.insertLine()
                self.needsRedraw = True
                self.unsavedChanges = True
            elif key.name == "KEY_BACKSPACE":
                if self.commandMode:
                    self.commandBuffer.deleteCharacterLeft()
                else:
                    self.documentBuffer.deleteCharacterLeft()
                    self.unsavedChanges = True
                self.needsRedraw = True
            elif key.name == "KEY_TAB":
                self.documentBuffer.insertText("    ")
                self.needsRedraw = True
                self.unsavedChanges = True
        elif key and self.readingSequence or self.commandMode:
            if key == "i":
                self.documentBuffer.cursorUpLine(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "k":
                self.documentBuffer.cursorDownLine(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "j":
                self.documentBuffer.cursorLeftCharacter(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "l":
                self.documentBuffer.cursorRightCharacter(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "u":
                self.documentBuffer.cursorLeftWord(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "U":
                self.documentBuffer.cursorLeftWORD(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "o":
                self.documentBuffer.cursorRightWord(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "O":
                self.documentBuffer.cursorRightWORD(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "p":
                self.documentBuffer.cursorWordEnd(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == ";":
                self.documentBuffer.cursorWordEndLeft(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "y":
                self.documentBuffer.cursorUpHalfPage(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "Y":
                self.documentBuffer.cursorUpPage(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "h":
                self.documentBuffer.cursorDownHalfPage(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "H":
                self.documentBuffer.cursorDownPage(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "s":
                self.documentBuffer.cursorBeginLine(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "e":
                self.documentBuffer.cursorEndLine(self.repeatAmount())
                self.needsRedraw = True
                self.clearCommandBuffer()
            elif key == "a":
                self.documentBuffer.insertLineAbove(self.repeatAmount())
                self.needsRedraw = True
                self.unsavedChanges = True
                self.clearCommandBuffer()
            elif key == "b":
                self.documentBuffer.insertLineBelow(self.repeatAmount())
                self.needsRedraw = True
                self.unsavedChanges = True
                self.clearCommandBuffer()
            elif key == "d":
                self.documentBuffer.deleteCharacter(self.repeatAmount())
                self.needsRedraw = True
                self.unsavedChanges = True
                self.clearCommandBuffer()
            elif key == "D":
                self.documentBuffer.deleteLine(self.repeatAmount())
                self.needsRedraw = True
                self.unsavedChanges = True
                self.clearCommandBuffer()
            elif key.isdigit():
                self.commandBuffer.insertText(key)
                self.commandMode = True
                self.needsRedraw = True
            elif key == "q":
                self.clearCommandBuffer()
                self.needsRedraw = True
            self.readingSequence = False
        elif key == "\x11":  # Ctrl-Q.
            if self.unsavedChanges:
                self.clearCommandBuffer()
                self.printToCommandBuffer("File has unsaved changes. Press Ctrl-E to exit without saving.")
                self.needsRedraw = True
            else:
                self.keepRunning = False
        elif key == "\x05":  # Ctrl-E.
            self.keepRunning = False
        elif key == "\x13":  # Ctrl-S.
            self.documentBuffer.writeToFilePath(self.filePath)
            self.clearCommandBuffer()
            self.unsavedChanges = False
            self.needsRedraw = True
        elif key == "\x03":  # Ctrl-C.
            self.clearCommandBuffer()
            self.needsRedraw = True
        elif key == "\x02":  # Ctrl-B.
            # Print help screen.
            print(self.terminal.home + self.terminal.clear, end="")
            print()
            print()
            self.printCentered(["KEYBINDINGS"])
            self.printCentered(["(press any key to hide)"])
            helpMessage = [
                "Basic Commands",
                "Ctrl-b: show keybindings",
                "Ctrl-s: save file",
                "Ctrl-q: quit",
                "Ctrl-e: exit without saving",
                "Ctrl-c: clear status bar",
                "",
                "Navigation",
                "Arrow keys: move cursor",
                "Alt-j: cursor left",
                "Alt-l: cursor right",
                "Alt-i: cursor up",
                "Alt-k: cursor down",
                "Alt-s: cursor to line start",
                "Alt-e: cursor to line end",
                "Alt-y: cursur up half page",
                "Alt-Y: cursor up whole page",
                "Alt-h: cursor down half page",
                "Alt-H: cursor down whole page",
                "",
                "Editing",
                "Alt-a: insert line above",
                "Alt-b: insert line below",
                "Alt-d: delete character under cursor",
                "Alt-D: delete line",
            ]
            self.printCentered(helpMessage)
            self.terminal.inkey(None)
            print(self.terminal.home + self.terminal.clear, end="")
            self.clearCommandBuffer()
            self.commandMode = False
            self.needsRedraw = True
        elif key and str(key).isascii() and str(key).isprintable():
            self.documentBuffer.insertText(str(key))
            self.clearCommandBuffer()
            self.needsRedraw = True
            self.unsavedChanges = True
        elif key:
            self.commandBuffer.currentLine.setText(repr(key))
            self.needsRedraw = True

    def draw(self):
        print(self.terminal.home + self.terminal.clear, end="")
        # Draw the document.
        currentLine = self.documentBuffer.topLine
        for i in range(self.terminal.height - 1):
            if currentLine is not None:
                text = currentLine.text[:self.terminal.width - 5] if len(currentLine.text) > self.terminal.width - 5 else currentLine.text
                print(f"{self.documentBuffer.scrollY + i + 1:>4} {text}", end="\r\n")
                currentLine = currentLine.next
            else:
                print("~", end="\r\n")
        
        # Draw the command bar.
        if self.commandBuffer.hasLine() and self.commandBuffer.currentLine.text or self.commandMode:
            print(self.commandBuffer.currentLine.text, end="\r")
        else:
            if self.unsavedChanges:
                print("[+] ", end="")
            elif self.readOnly:
                print("[RO] ", end="")
            maxPathLength = self.terminal.width - len("[RO] ...")
            print("..." + self.filePath[len(self.filePath)-maxPathLength:] if len(self.filePath) > maxPathLength else self.filePath, end="\r")
        
        # Draw the cursor.
        if self.commandMode:
            print(self.terminal.move_xy(self.commandBuffer.cursorX, self.terminal.height), end="")
            print(self.terminal.reverse(self.commandBuffer.currentLine.text[self.commandBuffer.cursorX] \
                if self.commandBuffer.cursorX < len(self.commandBuffer.currentLine.text) else " "), end="\r")
        else:
            print(self.terminal.move_xy(self.documentBuffer.cursorX - self.documentBuffer.scrollX + 5, self.documentBuffer.cursorY - self.documentBuffer.scrollY), end="")
            print(self.terminal.reverse(self.documentBuffer.currentLine.text[self.documentBuffer.cursorX] \
                if self.documentBuffer.cursorX < len(self.documentBuffer.currentLine.text) else " "), end="\r")

    def run(self, filePath=None):
        self.setup()
        with self.terminal.raw(), self.terminal.keypad(), self.terminal.hidden_cursor():
            if filePath is None:
                self.readFromFilePath("untitled.txt")
            else:
                self.readFromFilePath(filePath)

            while self.keepRunning:
                if self.needsRedraw:
                    self.draw()
                    self.needsRedraw = False
                self.update()
        print(self.terminal.home + self.terminal.clear, end="")
"""
