from pathlib import Path
import blessed


class Line:
    def __init__(self, text="", previous=None, next=None):
        self.previous = previous
        self.next = next
        self.text = text

    def insertText(self, pos, string):
        assert pos <= len(self.text)
        assert string is not None
        self.text = self.text[:pos] + string + self.text[pos:]

    def deleteText(self, start, numberOfCharacters=1):
        assert start >= 0
        assert start + numberOfCharacters <= len(self.text)
        self.text = self.text[:start] + self.text[start + numberOfCharacters:]


class Buffer:
    def __init__(self, screenWidth, pageSize):
        self.clear(screenWidth, pageSize)

    def clear(self, screenWidth, pageSize):
        self.screenWidth = screenWidth
        self.pageSize = pageSize
        self.numberOfLines = 0
        self.firstLine = None
        self.lastLine = None
        self.currentLine = None
        self.topLine = None
        self.scrollY, self.scrollX = 0, 0
        self.cursorY, self.cursorX = 0, 0

    def readFromFilePath(self, filePath):
        assert filePath is not None
        file = open(filePath, "r")
        self.readFromFile(file)
        file.close()

    def writeToFilePath(self, filePath):
        assert filePath is not None
        file = open(filePath, "w")
        self.writeToFile(file)
        file.close()

    def readFromFile(self, file):
        assert file is not None
        assert file.readable()
        self.numberOfLines = 0
        self.firstLine = self.lastLine = self.currentLine = None
        for line in file.readlines():
            # If this is not the first line, append it to the last line.
            if self.firstLine:
                self.lastLine.next = Line(text=line[:-1], previous=self.lastLine)
                self.lastLine = self.lastLine.next
            # If this is the first line, make the last and current line point to it.
            else:
                self.firstLine = self.lastLine = self.currentLine = self.topLine = Line(text=line[:-1])
            self.numberOfLines += 1

    def writeToFile(self, file):
        assert file is not None
        assert file.writable()
        # Make sure we are at the beginning of the file and that it is empty.
        file.seek(0)
        file.truncate()
        if self.lines:
            currentline = self.firstline
            while currentline:
                file.write(currentline.text + "\n")
                currentline = currentline.next
    
    def scrollUpLine(self, amount=1):
        for i in range(amount):
            if self.topLine.previous is None:
                break
            self.topLine = self.topLine.previous
            self.scrollY -= 1

    def scrollDownLine(self, amount=1):
        for i in range(amount):
            if self.topLine.next is None:
                break
            self.topLine = self.topLine.next
            self.scrollY += 1
    
    def cursorUpLine(self, amount=1):
        for i in range(amount): 
            if self.currentLine.previous is None:
                self.cursorX = 0
                break
            self.currentLine = self.currentLine.previous
            self.cursorY -= 1
            self.cursorX = min(self.cursorX, len(self.currentLine.text))
            if self.cursorY < self.scrollY:
                self.scrollUpLine()

    def cursorDownLine(self, amount=1):
        for i in range(amount):
            if self.cursorY == self.numberOfLines - 1 and self.cursorX == len(self.currentLine.text):
                self.scrollDownLine()
            if self.currentLine.next:
                self.currentLine = self.currentLine.next
                self.cursorY += 1
                self.cursorX = min(self.cursorX, len(self.currentLine.text))
            else:
                self.cursorX = len(self.currentLine.text)
            
            if self.cursorY >= self.scrollY + self.pageSize:
                self.scrollDownLine()
                #break

    def cursorBeginLine(self, amount=1):
        for i in range(amount):
            if self.cursorX == 0:
                if self.cursorY != 0:
                    self.cursorUpLine()
                else:
                    break
            self.cursorX = 0
            self.scrollX = 0

    def cursorEndLine(self, amount=1):
        for i in range(amount):
            if self.cursorX == len(self.currentLine.text):
                if self.cursorY != self.numberOfLines - 1:
                    self.cursorDownLine()
                else:
                    break
            self.cursorX = len(self.currentLine.text)
            #self.scrollX = max(len(self.currentLine.text) - self.pageSize, 0)

    def cursorLeftCharacter(self, amount=1):
        for i in range(amount):
            if self.cursorX == 0:
                if self.cursorY == 0:
                    break
                self.cursorUpLine()
                self.cursorX = len(self.currentLine.text)
            else:
                self.cursorX -= 1
                if self.cursorX < self.scrollX:
                    self.scrollX -= 1

    def cursorRightCharacter(self, amount=1):
        for i in range(amount):
            if self.cursorX == len(self.currentLine.text):
                if self.cursorY != self.numberOfLines - 1:
                    self.cursorDownLine()
                    self.cursorX = 0
                    self.scrollX = 0
                else:
                    break
            else:
                self.cursorX += 1
                #if self.cursorX > self.scrollX + self.screenWidth:
                #    self.scrollX += 1

    def insertText(self, text):
        assert text is not None
        self.currentLine.text = self.currentLine.text[:self.cursorX] + text + self.currentLine.text[self.cursorX:]
        self.cursorX += 1

    def insertLine(self, amount=1):
        for i in range(amount):
            nextLine = Line(self.currentLine.text[self.cursorX:], next=self.currentLine.next, previous=self.currentLine)
            if self.currentLine.next is not None:
                self.currentLine.next.previous = nextLine
            self.currentLine.next = nextLine
            self.currentLine.text = self.currentLine.text[:self.cursorX]
            #self.currentLine = nextLine
            self.cursorX = 0
            self.scrollX = 0
            self.numberOfLines += 1
            self.cursorDownLine()

    def insertLineAbove(self, text=""):
        assert text is not None
        if self.firstLine is None:
            self.firstLine = self.lastLine = self.currentLine = self.topLine = Line(text)
        elif self.currentLine.previous is None:
            self.currentLine.previous = Line(text, next=self.currentLine)
            self.firstLine = self.currentLine.previous
        else:
            newLine = Line(text, previous=self.currentLine.previous, next=self.currentLine)
            self.currentLine.previous.next = newLine
            self.currentLine.previous = newLine

    def deleteCharacter(self, amount=1):
        for i in range(amount):
            length = len(self.currentLine.text)
            if length == 0:
                self.deleteLine()
            elif self.cursorX == 0:
                length = len(self.currentLine.previous.text)
                if self.currentLine.previous is not None:
                    self.currentLine.previous.text += self.currentLine.text
                    self.currentLine.previous.next = self.currentLine.next
                    self.currentLine.next.previous = self.currentLine.previous
                    self.cursorUpLine()
                    self.cursorX = length
            else:
                self.currentLine.text = self.currentLine.text[:self.cursorX - amount] + self.currentLine.text[self.cursorX:]
                self.cursorLeftCharacter()

    def deleteLine(self, amount=1):
        for i in range(amount):
            if self.currentLine.previous is not None:
                self.currentLine.previous.next = self.currentLine.next
                self.cursorUpLine()
            elif self.currentLine.next is not None:
                self.currentLine.next.previous = None


class EditorModel:
    def __init__(self, screenWidth, pageSize):
        self.filePath = None
        self.documentBuffer = Buffer(screenWidth, pageSize)
        self.commandBuffer = Buffer(screenWidth, pageSize)
        self.commandBuffer.insertLineAbove()
        self.currentBuffer = self.documentBuffer

    def openFile(self, filePath):
        self.documentBuffer.readFromFilePath(filePath)
        self.filePath = filePath


class EditorView:
    def __init__(self, terminal=None):
        self.terminal = blessed.Terminal() if terminal is None else terminal

    def drawWelcomeMessage(self):
        message = [
            "Text Editor",
            "Version 0",
            "",
            "Basic keybindings",
            "ctrl-q: quit                ctrl-o: open file        ",
            "ctrl-h: show keybindings    ctrl-n: create new file  ",
            "                            ctrl-s: save current file",
            "",
            "",
            "Press any key to continue",
        ]
        print(self.terminal.home + self.terminal.clear + self.terminal.move_down(self.terminal.height//2 - len(message)), end="")
        for line in message:
            print(self.terminal.center(line), end="\r\n")
        self.terminal.inkey()

    def drawDocument(self, documentBuffer):
        currentLine = documentBuffer.topLine
        lineNumber = documentBuffer.scrollY + 1
        while currentLine is not None and lineNumber - documentBuffer.scrollY < self.terminal.height:
            if currentLine is documentBuffer.currentLine:
                print(f"{lineNumber:<4} ", end="")
            else:
                print(self.terminal.gray43(f"{abs(documentBuffer.cursorY - lineNumber + 1):4} "), end="")

            if len(currentLine.text) < self.terminal.width - 5:
                print(currentLine.text, end="\r\n")
            else:
                print(currentLine.text[:self.terminal.width-5], end="\r\n")
            lineNumber += 1
            currentLine = currentLine.next

        #while lineNumber - documentBuffer.scrollY <= self.terminal.height - 1:
        #    print(self.terminal.gray43("~"), end="\r\n")
        #    lineNumber += 1

    def drawCommandBar(self, documentBuffer, commandBuffer, focus, filePath):
        print(self.terminal.move_xy(0, self.terminal.height), end="")
        if focus == "commandbar" or commandBuffer.currentLine.text:
            print(commandBuffer.currentLine.text, end="\r")
        else:
            print(self.terminal.rjust(self.terminal.gray43(str(documentBuffer.cursorY+1) + ", " + str(documentBuffer.cursorX+1))), end="\r")
            print(self.terminal.move_xy(0, self.terminal.height) + self.terminal.gray43("[+] " + filePath), end="\r")

    def draw(self, documentBuffer, commandBuffer, focus, filePath):
        print(self.terminal.home + self.terminal.clear, end="")
        self.drawDocument(documentBuffer)
        self.drawCommandBar(documentBuffer, commandBuffer, focus, filePath)

        if focus == "document":
            print(self.terminal.move_xy(documentBuffer.cursorX - documentBuffer.scrollX + 5, documentBuffer.cursorY - documentBuffer.scrollY), end="")
            print(self.terminal.reverse + (documentBuffer.currentLine.text[documentBuffer.cursorX] \
                if documentBuffer.cursorX < len(documentBuffer.currentLine.text) else " ") + self.terminal.normal, end="\r")
        elif focus == "commandbar":
            print(self.terminal.move_xy(commandBuffer.cursorX, self.terminal.height), end="")
            print(self.terminal.reverse + commandBuffer.currentLine.text[commandBuffer.cursorX] + self.terminal.normal, end="\r")

    def getKeypress(self):
        return self.terminal.inkey(0)


class Editor:
    def __init__(self, model=None, view=None):
        self.view = EditorView() if view is None else view
        self.model = EditorModel(self.view.terminal.width - 5, self.view.terminal.height - 1) if model is None else model
        self.keepRunning = True
        self.readingSequence = False
        self.needsRedraw = True
        self.focus = "document"  # "document" or "commandbar".

    def processKeypress(self):
        key = self.view.getKeypress()
        # Update the model and view accordingly.
        if key.is_sequence:
            if key.name == "KEY_ESCAPE":
                self.readingSequence = not self.readingSequence
            elif key.name == "KEY_UP":
                self.model.documentBuffer.cursorUpLine()
                self.needsRedraw = True
            elif key.name == "KEY_DOWN":
                self.model.documentBuffer.cursorDownLine()
                self.needsRedraw = True
            elif key.name == "KEY_LEFT":
                self.model.documentBuffer.cursorLeftCharacter()
                self.needsRedraw = True
            elif key.name == "KEY_RIGHT":
                self.model.documentBuffer.cursorRightCharacter()
                self.needsRedraw = True
            elif key.name == "KEY_ENTER":
                self.model.documentBuffer.insertLine()
                self.needsRedraw = True
            elif key.name == "KEY_BACKSPACE":
                self.model.documentBuffer.deleteCharacter()
                self.needsRedraw = True
            else:
                self.model.commandBuffer.currentLine.text = key.name + ", " + str(key.code)
                self.needsRedraw = True
        elif self.readingSequence:
            #if key == "q":
            #    self.keepRunning = False
            if key == "i":
                self.model.documentBuffer.cursorUpLine()
                self.needsRedraw = True
            elif key == "k":
                self.model.documentBuffer.cursorDownLine()
                self.needsRedraw = True
            elif key == "j":
                self.model.documentBuffer.cursorLeftCharacter()
                self.needsRedraw = True
            elif key == "l":
                self.model.documentBuffer.cursorRightCharacter()
                self.needsRedraw = True
            elif key == "b":
                self.model.documentBuffer.cursorBeginLine()
                self.needsRedraw = True
            elif key == "e":
                self.model.documentBuffer.cursorEndLine()
                self.needsRedraw = True
            self.readingSequence = False
        elif key and str(key).isascii() and str(key).isprintable():
            self.model.documentBuffer.insertText(str(key))
            self.needsRedraw = True
        elif key == "\x11":
            self.keepRunning = False
        elif key:
            self.model.commandBuffer.currentLine.text = repr(key)
            self.needsRedraw = True

    def run(self):
        self.keepRunning = True
        with self.view.terminal.raw(), self.view.terminal.keypad(), self.view.terminal.hidden_cursor():
            self.model.openFile(str(Path.home()) + "/Documents/code/text-editor/example.txt")
            self.view.drawWelcomeMessage()
            while self.keepRunning:
                if self.needsRedraw:
                    self.view.draw(self.model.documentBuffer, self.model.commandBuffer, self.focus, self.model.filePath)
                    self.needsRedraw = False
                self.processKeypress()
        print(self.view.terminal.clear(), end="")


if __name__ == "__main__":
    editor = Editor()
    editor.run()

