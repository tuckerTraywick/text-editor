import os


class Selection:
    def __init__(self, startX, startY, endX=None, endY=None):
        self.startX, self.startY = startX, startY
        self.endX = startX if endX is None else endX
        self.endY = startY if endY is None else endY

    def __repr__(self):
        return repr(vars(self))

    @property
    def width(self):
        # Returns the horizontal size of the selection.
        return abs(self.endX - self.startX) + 1

    @property
    def height(self):
        # Returns the vertical size of the selection.
        return abs(self.endY - self.startY) + 1

    @property
    def minX(self):
        return min(self.startX, self.endX)

    @property
    def minY(self):
        return min(self.startY, self.endY)

    @property
    def maxX(self):
        return max(self.startX, self.endX)

    @property
    def maxY(self):
        return max(self.startY, self.endY)


class Buffer:
    WHITESPACE = "\n\r\t "
    BRACKETS = "()[]{}"
    SYMBOLS = "`~!@#$%^&*-_=+\\|;:'\",<.>/?"

    def __init__(self, name):
        self.name = name
        self.clear()

    def __repr__(self):
        return repr(vars(self))

    @property
    def numberOfLines(self):
        return len(self.lines)

    @property
    def activeSelection(self):
        return self.selections[self.activeSelectionIndex]

    @property
    def cursorX(self):
        return self.activeSelection.startX

    @cursorX.setter
    def cursorX(self, cursorX):
        self.activeSelection.startX = cursorX
        if not self.isSelecting:
            self.activeSelection.endX = cursorX

    @property
    def cursorY(self):
        return self.activeSelection.startY

    @cursorY.setter
    def cursorY(self, cursorY):
        self.activeSelection.startY = cursorY
        if not self.isSelecting:
            self.activeSelection.endY = cursorY

    @property
    def currentLine(self):
        return self.lines[self.cursorY]

    @currentLine.setter
    def currentLine(self, currentLine):
        self.lines[self.cursorY] = currentLine

    @property
    def currentCharacter(self):
        return "\n" if self.cursorX == len(self.currentLine) else self.currentLine[self.cursorX]

    @property
    def previousCharacter(self):
        self.cursorCharacterLeft()
        ch = self.currentCharacter
        self.cursorCharacterRight()
        return ch

    @property
    def notAtBeginning(self):
        return self.cursorX > 0 or self.cursorY > 0

    @property
    def notAtEnd(self):
        return self.cursorX < len(self.currentLine) or self.cursorY < self.numberOfLines - 1

    def clear(self):
        self.lines = [""]
        self.selections = [Selection(0, 0)]
        self.activeSelectionIndex = 0
        self.maxCursorX = 0
        self.isReadonly = False
        self.isSelecting = False
        self.hasUnsavedChanges = False

    def readFromFile(self, file):
        # Reads the given file into the buffer.
        if isinstance(file, str):
            fileObject = open(file, "r")
            self.readFromFile(fileObject)
            fileObject.close()
        else:
            assert file.readable()
            self.clear()
            self.lines = [line.strip("\r\n") for line in file.readlines()]
            self.isReadonly = not os.access(file.name, os.W_OK)

    def writeToFile(self, file):
        # Writes the buffer to the given file.
        if isinstance(file, string):
            fileObject = open(file, "w")
            self.writeToFile(file)
            fileObject.close()
        else:
            assert file.writable()
            file.writeLines(self.lines)
            self.hasUnsavedChanges = False

    def _insertLine(self, lineNumber):
        # Inserts a new line at the given line number.
        self.lines.insert(lineNumber, "")

    def _insertTextInLine(self, text, lineNumber, index):
        # Inserts the given text in the given line at the given index.
        self.lines[lineNumber] = self.lines[lineNumber][:index] + text + self.lines[lineNumber][index:]

    def _deleteLine(self, lineNumber):
        # Deletes the given line.
        if len(self.lines) > 1:
            self.lines.pop(lineNumber)

    def _deleteTextInLine(self, lineNumber, startIndex, endIndex):
        # Deletes the text in the given range at the given line number.
        self.lines[lineNumber] = self.lines[lineNumber][:startIndex] + self.lines[lineNumber][endIndex:]
        if not self.lines[lineNumber]:
            self._deleteLine(lineNumber)

    def startSelecting(self):
        # Starts selecting text.
        self.isSelecting = True

    def stopSelecting(self):
        # Stops selecting text.
        self.isSelecting = False
        self.activeSelection.endX, self.activeSelection.endY = self.cursorX, self.cursorY

    def cursorBufferBegin(self, amount=1):
        # Moves the cursor to the beginning of the buffer.
        self.cursorX = 0
        self.cursorY = 0

    def cursorBufferEnd(self, amount=1):
        # Moves the cursor to the end of the buffer.
        self.cursorY = self.numberOfLines - 1
        self.cursorX = len(self.currentLine)

    def cursorLineBegin(self, amount=1):
        # Moves the cursor to the beginning of the current/previous line.
        for i in range(amount):
            if self.cursorX > 0:
                self.cursorX = 0
            elif self.cursorY > 0:
                self.cursorY -= 1
                self.cursorX = 0
            else:
                break

    def cursorLineEnd(self, amount=1):
        # Moves the cursor to the end of the current/next line.
        for i in range(amount):
            if self.cursorX < len(self.currentLine):
                self.cursorX = len(self.currentLine)
            elif self.cursorY < self.numberOfLines:
                self.cursorY += 1
                self.cursorX = len(self.currentLine)
            else:
                break

    def cursorLineUp(self, amount=1):
        # Moves the cursor up a line.
        for i in range(amount):
            if self.cursorY > 0:
                self.cursorY -= 1
                self.cursorX = min(self.cursorX, len(self.currentLine))
            else:
                break

    def cursorLineDown(self, amount=1):
        # Moves the cursor down a line.
        for i in range(amount):
            if self.cursorY < self.numberOfLines - 1:
                self.cursorY += 1
                self.cursorX = min(self.cursorX, len(self.currentLine))
            else:
                break

    def cursorCharacterLeft(self, amount=1):
        # Moves the cursor right one character.
        for i in range(amount):
            if self.cursorX > 0:
                self.cursorX -= 1
            elif self.cursorY > 0:
                self.cursorY -= 1
                self.cursorX = len(self.currentLine)
            else:
                break

    def cursorCharacterRight(self, amount=1):
        # Moves the cursor left one character.
        for i in range(amount):
            if self.cursorX < len(self.currentLine):
                self.cursorX += 1
            elif self.cursorY < self.numberOfLines - 1:
                self.cursorY += 1
                self.cursorX = 0
            else:
                break

    def cursorWORDEnd(self, amount=1):
        # Moves the cursor to the end of the current/next WORD.
        for i in range(amount):
            if self.notAtEnd:
                # Skip whitespace.
                while self.currentCharacter in Buffer.WHITESPACE and self.notAtEnd:
                    self.cursorCharacterRight()

                # Move to the end of the word.
                while self.currentCharacter not in Buffer.WHITESPACE and self.notAtEnd:
                    self.cursorCharacterRight()

    def cursorWORDLeft(self, amount=1):
        # Moves the cursor left one WORD.
        for i in range(amount):
            if self.notAtBeginning:
                #self.cursorCharacterLeft()

                # Skip whitespace.
                while self.notAtBeginning and self.previousCharacter not in Buffer.WHITESPACE:
                    self.cursorCharacterLeft()

                # Move to the beginning of the WORD.
                while self.previousCharacter not in Buffer.WHITESPACE and self.notAtBeginning:
                    self.cursorCharacterLeft()
            else:
                break

    def cursorWORDRight(self, amount=1):
        # Moves the cursor right one WORD.
        for i in range(amount):
            if self.notAtEnd:
                # Move to the end of the WORD.
                while self.currentCharacter not in Buffer.WHITESPACE and self.notAtEnd:
                    self.cursorCharacterRight()

                # Skip whitespace.
                while self.currentCharacter in Buffer.WHITESPACE and self.notAtEnd:
                    self.cursorCharacterRight()
            else:
                break

    def delete(self, amount=1):
        # Deletes the text in the active selection.
        for i in range(amount):
            if self.isSelecting and self.activeSelection.width > 0:
                if self.activeSelection.height > 1:
                    self._deleteTextInLine(self.activeSelection.minY, self.activeSelection.minX, len(self.lines[self.activeSelection.minY]))
                    for i in range(self.activeSelection.minY + 1, self.activeSelection.maxY):
                        self._deleteLine(self.activeSelection.minY)
                    self._deleteTextInLine(self.activeSelection.minY, 0, self.activeSelection.maxX)
                else:
                    self._deleteTextInLine(self.activeSelection.minY, 0, self.activeSelection.maxX)

                self.cursorX, self.cursorY = self.activeSelection.minX, self.activeSelection.minY
                self.stopSelecting()
            else:
                break

    def deleteLine(self, amount=1):
        # Deletes the current line.
        for i in range(amount):
            self.stopSelecting()
            if self.numberOfLines > 1:
                self._deleteLine(self.cursorY)
            elif self.currentLine:
                self.currentLine = ""
                self.cursorX = 0
            else:
                break

    def insert(self, text, amount=1):
        # Inserts the given text at the cursor.
        for i in range(amount):
            self.delete()
            self._insertTextInLine(text, self.cursorY, self.cursorX)
            self.cursorCharacterRight(len(text))

    def insertLineAbove(self, amount=1):
        # Inserts a line above the cursor.
        for i in range(amount):
            self.stopSelecting()
            self._insertLine(self.cursorY)

    def insertLineBelow(self, amount=1):
        # Inserts a line below the cursor.
        for i in range(amount):
            self.stopSelecting()
            self.cursorY += 1
            self._insertLine(self.cursorY)

