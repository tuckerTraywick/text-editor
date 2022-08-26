import os
import sys
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
        self.tabWidth = 4

    def readFromFilePath(self, filePath):
        assert filePath is not None
        if os.path.exists(filePath):
            file = open(filePath, "r")
            assert file.readable()
            self.readFromFile(file)
            file.close()
            return True
        else:
            self.insertLineAbove()
            self.scrollX = self.scrollY = self.cursorX = self.cursorY = 0
            return False

    def writeToFilePath(self, filePath):
        assert filePath is not None
        file = open(filePath, "w+")
        assert file.writable()
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
            if self.firstLine is not None:
                self.lastLine.next = Line(text=line[:-1], previous=self.lastLine)
                self.lastLine = self.lastLine.next
            # If this is the first line, make the last and current line point to it.
            else:
                self.firstLine = self.lastLine = self.currentLine = self.topLine = Line(text=line[:-1])
            self.numberOfLines += 1
        if self.firstLine is None:
            self.insertLineAbove()

    def writeToFile(self, file):
        assert file is not None
        assert file.writable()
        # Make sure we are at the beginning of the file and that it is empty.
        file.seek(0)
        file.truncate()
        if self.firstLine is not None:
            currentLine = self.firstLine
            while currentLine is not None:
                file.write(currentLine.text + "\n")
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

    def cursorUpPage(self, amount=1):
        self.cursorUpLine(amount*self.pageHeight)

    def cursorDownHalfPage(self, amount=1):
        self.cursorDownLine(amount*self.pageHeight//2)

    def cursorDownPage(self, amount=1):
        self.cursorDownLine(amount*self.pageHeight)

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
        self.cursorX += len(text)

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
        self.commandBuffer.insertLineAbove()
        self.commandMode = False  # True = focused on command bar, False = focused on document.
        self.keepRunning = True
        self.needsRedraw = True
        self.readingSequence = False
        self.unsavedChanges = False
        self.readOnly = False
        self.commandInput = ""

    def readFromFilePath(self, filePath):
        self.filePath = filePath
        if not self.documentBuffer.readFromFilePath(self.filePath):
            self.unsavedChanges = True

    def writeToFile(self):
        assert self.filePath
        self.document.writeToFilePath(self.filePath)

    def clearCommandBuffer(self):
        self.commandBuffer.currentLine.text = ""
        self.commandMode = False

    def printToCommandBuffer(self, text):
        self.commandBuffer.insertText(text)

    def inputFromCommandBuffer(self):
        self.commandMode = True
        self.commandInput = ""

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
                self.documentBuffer.deleteCharacterLeft()
                self.needsRedraw = True
                self.unsavedChanges = True
            elif key.name == "KEY_TAB":
                self.documentBuffer.insertText("    ")
                self.needsRedraw = True
                self.unsavedChanges = True
            self.clearCommandBuffer()
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
            elif key == "Y":
                self.documentBuffer.cursorUpPage()
                self.needsRedraw = True
            elif key == "h":
                self.documentBuffer.cursorDownHalfPage()
                self.needsRedraw = True
            elif key == "H":
                self.documentBuffer.cursorDownPage()
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
                self.unsavedChanges = True
            elif key == "b":
                self.documentBuffer.insertLineBelow()
                self.needsRedraw = True
                self.unsavedChanges = True
            elif key == "d":
                self.documentBuffer.deleteCharacter()
                self.needsRedraw = True
                self.unsavedChanges = True
            elif key == "D":
                self.documentBuffer.deleteLine()
                self.needsRedraw = True
                self.unsavedChanges = True
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
            self.commandBuffer.currentLine.text = repr(key)
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
        if self.commandBuffer.hasLine() and self.commandBuffer.currentLine.text:
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
            print(self.terminal.move_xy(self.commandBuffer.cursorX, self.terminal.height))
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


if __name__ == "__main__":
    editor = Editor()
    editor.run(sys.argv[1] if len(sys.argv) > 1 else None)
