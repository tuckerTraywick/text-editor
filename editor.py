import blessed
from pathlib import Path


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
    def __init__(self, pageWidth, pageHeight):
        self.clear(pageWidth, pageHeight)

    def clear(self, pageWidth, pageHeight):
        assert pageWidth > 0
        assert pageHeight > 0
        self.pageWidth = pageWidth
        self.pageHeight = pageHeight
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
        assert file.readable()
        self.readFromFile(file)
        file.close()

    def writeToFilePath(self, filePath):
        assert filePath is not None
        file = open(filePath, "w")
        assert file.writeable()
        self.writeToFile(file)
        file.close()

    def readFromFile(self, file):
        assert file is not None
        assert file.readable()
        self.numberOfLines = 0
        self.scrollX = self.scrollY = self.cursorX = self.cursorY = 0
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
            currentLine = self.firstLine
            while currentLine:
                file.write(currentLine.text + "" if currentLine.next is None else "\n")
                currentLine = currentLine.next

    def hasLine(self):
        return self.currentLine is not None
    
    def canScrollUpLine(self):
        return self.topLine is not None and self.topLine.previous is not None

    def canScrollDownLine(self):
        return self.topLine is not None and self.topLine.next is not None

    def canMoveUpLine(self):
        return self.currentLine is not None and self.currentLine.previous is not None

    def canMoveDownLine(self):
        return self.currentLine is not None and self.currentLine.next is not None

    def canMoveLeftCharacter(self):
        return self.currentLine is not None and self.cursorX > 0

    def canMoveRightCharacter(self):
        return self.currentLine is not None and self.cursorX < len(self.currentLine.text)

    def scrollUpLine(self, amount=1):
        for i in range(amount):
            if self.canScrollUpLine():
                self.topLine = self.topLine.previous
                self.scrollY -= 1
            else:
                break

    def scrollDownLine(self, amount=1):
        for i in range(amount):
            if self.canScrollDownLine():
                self.topLine = self.topLine.next
                self.scrollY += 1
            else:
                break
    
    def cursorUpLine(self, amount=1):
        for i in range(amount): 
            if self.canMoveUpLine():
                self.currentLine = self.currentLine.previous
                self.cursorY -= 1
                self.cursorX = min(self.cursorX, len(self.currentLine.text))
                if self.cursorY < self.scrollY:
                    self.scrollUpLine()
            else:
                self.cursorX = 0
                break

    def cursorDownLine(self, amount=1):
        for i in range(amount):
            if self.canMoveDownLine():
                self.currentLine = self.currentLine.next
                self.cursorY += 1
                self.cursorX = min(self.cursorX, len(self.currentLine.text))
                if self.cursorY >= self.scrollY + self.pageHeight:
                    self.scrollDownLine()
            elif self.canMoveRightCharacter():
                self.cursorX = len(self.currentLine.text)
            elif self.canScrollDownLine():
                self.scrollDownLine()
            else:
                break

    def cursorUpHalfPage(self, amount=1):
        self.cursorUpLine(amount*self.pageHeight//2)

    def cursorDownHalfPage(self, amount=1):
        self.cursorDownLine(amount*self.pageHeight//2)

    def cursorBeginLine(self, amount=1):
        for i in range(amount):
            if self.canMoveLeftCharacter():
                self.cursorX = 0
            elif self.canMoveUpLine():
                self.cursorUpLine()
                self.cursorX = 0
            else:
                break

    def cursorEndLine(self, amount=1):
        for i in range(amount):
            if self.canMoveRightCharacter():
                self.cursorX = len(self.currentLine.text)
            elif self.canMoveDownLine():
                self.cursorDownLine()
                self.cursorX = len(self.currentLine.text)
            elif self.canScrollDownLine():
                self.scrollDownLine()
            else:
                break

    def cursorLeftCharacter(self, amount=1):
        for i in range(amount):
            if self.canMoveLeftCharacter():
                self.cursorX -= 1
            elif self.canMoveUpLine():
                self.cursorUpLine()
                self.cursorX = len(self.currentLine.text)
            else:
                break

    def cursorRightCharacter(self, amount=1):
        for i in range(amount):
            if self.canMoveRightCharacter():
                self.cursorX += 1
            elif self.canMoveDownLine():
                self.cursorDownLine()
                self.cursorX = 0
            else:
                break

    def insertText(self, text):
        assert text is not None
        self.currentLine.text = self.currentLine.text[:self.cursorX] + text + self.currentLine.text[self.cursorX:]
        self.cursorX += 1

    def insertLineAbove(self, text=""):
        assert text is not None
        newLine = Line(text, previous=self.currentLine.previous if self.currentLine is not None else None, next=self.currentLine)
        if self.canMoveUpLine():
            self.currentLine.previous.next = newLine
            self.currentLine.previous = newLine
            self.cursorUpLine()
            self.cursorY += 1  # Correct the y position.
        else:
            self.firstLine = newLine
            if self.currentLine is not None:
                self.currentLine.previous = newLine
            self.currentLine = self.topLine = newLine
        self.numberOfLines += 1
        self.cursorX = 0

    def insertLineBelow(self, text=""):
        assert text is not None
        newLine = Line(text, previous=self.currentLine, next=self.currentLine.next if self.currentLine is not None else None)
        if self.canMoveDownLine():
            self.currentLine.next.previous = newLine
            self.currentLine.next = newLine
            self.cursorDownLine()
        else:
            self.lastLine = newLine
            if self.currentLine is not None:
                self.currentLine.next = newLine
            self.cursorDownLine()
        self.numberOfLines += 1
        self.cursorX = 0

    def insertLine(self, amount=1):
        for i in range(amount):
            if self.hasLine():
                if self.cursorX == 0:
                    self.insertLineAbove()
                    self.cursorDownLine()
                else:
                    text = self.currentLine.text[self.cursorX:]
                    self.currentLine.text = self.currentLine.text[:self.cursorX]
                    self.insertLineBelow(text)
            else:
                self.currentLine = self.firstLine = self.topLine = Line()

    def deleteLine(self, amount=1):
        if self.hasLine():
            for i in range(amount):
                if self.numberOfLines == 1:
                    self.currentLine.text = ""
                    self.cursorX = 0
                    break
                elif self.canMoveDownLine():
                    if self.topLine is self.currentLine:
                        self.topLine = self.currentLine.next
                    self.currentLine.next.previous = self.currentLine.previous
                    if self.canMoveUpLine():
                        self.currentLine.previous.next = self.currentLine.next
                    else:
                        self.firstLine = self.currentLine.next
                    self.currentLine = self.currentLine.next
                else:
                    self.currentLine.previous.next = None
                    self.lastLine = self.currentLine.previous
                    self.cursorUpLine()
                self.numberOfLines -= 1
    
    def deleteCharacter(self, amount=1):
        if self.hasLine():
            for i in range(amount):
                if not self.canMoveRightCharacter() and self.canMoveDownLine():
                    self.currentLine.next.text = self.currentLine.text + self.currentLine.next.text
                    self.deleteLine()
                elif self.currentLine.text:
                    self.currentLine.text = self.currentLine.text[:self.cursorX]  + self.currentLine.text[self.cursorX + 1:]
    
    def deleteCharacterLeft(self, amount=1):
        if self.hasLine():
            for i in range(amount):
                if self.canMoveLeftCharacter() or self.canMoveUpLine():
                    self.cursorLeftCharacter()
                    self.deleteCharacter()
                else:
                    break


class Editor:
    def __init__(self, terminal=None):
        self.setup(terminal)

    def setup(self, terminal=None):
        self.terminal = blessed.Terminal() if terminal is None else terminal
        self.filePath = None
        self.documentBuffer = Buffer(self.terminal.width - 5, self.terminal.height - 1)
        self.commandBuffer = Buffer(self.terminal.width - 5, 1)
        #self.commandBuffer.insertLine()
        self.commandMode = False  # True = focused on command bar, False = focused on document.
        self.keepRunning = True
        self.needsRedraw = True
        self.readingSequence = False

    def readFromFilePath(self, filePath):
        self.filePath = filePath
        self.documentBuffer.readFromFilePath(self.filePath)

    def writeToFile(self):
        assert self.filePath
        self.document.writeToFilePath(self.filePath)

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
            elif key.name == "KEY_BACKSPACE":
                self.documentBuffer.deleteCharacterLeft()
                self.needsRedraw = True
        elif key and self.readingSequence:
            if key == "i":
                self.documentBuffer.cursorUpLine()
                self.needsRedraw = True
            elif key == "k":
                self.documentBuffer.cursorDownLine()
                self.needsRedraw = True
            elif key == "j":
                self.documentBuffer.cursorLeftCharacter()
                self.needsRedraw = True
            elif key == "l":
                self.documentBuffer.cursorRightCharacter()
                self.needsRedraw = True
            elif key == "y":
                self.documentBuffer.cursorUpHalfPage()
                self.needsRedraw = True
            elif key == "h":
                self.documentBuffer.cursorDownHalfPage()
                self.needsRedraw = True
            elif key == "s":
                self.documentBuffer.cursorBeginLine()
                self.needsRedraw = True
            elif key == "e":
                self.documentBuffer.cursorEndLine()
                self.needsRedraw = True
            elif key == "a":
                self.documentBuffer.insertLineAbove()
                self.needsRedraw = True
            elif key == "b":
                self.documentBuffer.insertLineBelow()
                self.needsRedraw = True
            elif key == "d":
                self.documentBuffer.deleteCharacter()
                self.needsRedraw = True
            elif key == "D":
                self.documentBuffer.deleteLine()
                self.needsRedraw = True
            self.readingSequence = False
        elif key == "\x11":
            self.keepRunning = False
        elif key and str(key).isascii() and str(key).isprintable():
            self.documentBuffer.insertText(str(key))
            self.needsRedraw = True

    def draw(self):
        print(self.terminal.home + self.terminal.clear, end="")
        currentLine = self.documentBuffer.topLine
        for i in range(self.terminal.height - 1):
            if currentLine is not None:
                text = currentLine.text[:self.terminal.width - 5] if len(currentLine.text) > self.terminal.width - 5 else currentLine.text
                print(f"{self.documentBuffer.scrollY + i + 1:>4} {text}", end="\r\n")
                currentLine = currentLine.next
            else:
                print("~", end="\r\n")
        
        print(self.filePath, end="\r")
        print(self.terminal.move_xy(self.documentBuffer.cursorX - self.documentBuffer.scrollX + 5, self.documentBuffer.cursorY - self.documentBuffer.scrollY), end="")
        print(self.terminal.reverse(self.documentBuffer.currentLine.text[self.documentBuffer.cursorX] \
            if self.documentBuffer.cursorX < len(self.documentBuffer.currentLine.text) else " "), end="\r")

    def run(self):
        self.setup()
        with self.terminal.raw(), self.terminal.keypad(), self.terminal.hidden_cursor():
            self.readFromFilePath(str(Path.home()) + "/Documents/code/text-editor/example.txt")
            while self.keepRunning:
                if self.needsRedraw:
                    self.draw()
                    self.needsRedraw = False
                self.update()
        print(self.terminal.home + self.terminal.clear, end="")


if __name__ == "__main__":
    editor = Editor()
    editor.run()
