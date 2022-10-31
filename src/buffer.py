import os


class Buffer:
    WHITESPACE = "\n\r\t "
    BRACKETS = "()[]{}"
    SYMBOLS = "`~!@#$%^&*-_=+\\|;:'\",<.>/?"

    def __init__(self, name="", lines=None, allowNewLines=True):
        self.name = name
        self.lines = [] if lines is None else lines
        self.allowNewLines = allowNewLines
        self.clear()

    def __repr__(self):
        return repr(vars(self))

    @property
    def numberOfLines(self):
        # Returns the number of lines in the buffer.
        return len(self.lines)

    @property
    def currentLine(self):
        # Returns the text of the line the cursor is on.
        return self.lines[self.cursorY]

    @currentLine.setter
    def currentLine(self, currentLine):
        # Sets the text of the line the cursor is on.
        self.lines[self.cursorY] = currentLine

    @property
    def currentCharacter(self):
        # Returns the character under the cursor.
        # Returns "" if the cursor is at the end of a line.
        return "" if self.cursorX == len(self.currentLine) else self.currentLine[self.cursorX]

    @property
    def previousCharacter(self):
        # Returns the character behind the cursor.
        self.cursorCharacterLeft()
        ch = self.currentCharacter
        self.cursorCharacterRight()
        return ch

    @property
    def cursorX(self):
        # Returns the x coordinate of the cursor.
        return self._cursorX

    @cursorX.setter
    def cursorX(self, cursorX):
        # Sets the y coordinate of the cursor.
        self._cursorX = cursorX
        if not self.isSelecting:
            self.startX = cursorX

    @property
    def cursorY(self):
        # Returns the y coordinate of the cursor.
        return self._cursorY

    @cursorY.setter
    def cursorY(self, cursorY):
        # Sets the y coordinate of the cursor.
        self._cursorY = cursorY
        if not self.isSelecting:
            self.startY = cursorY

    @property
    def firstX(self):
        # Returns the x coordinate of the start of the selection.
        if self.cursorY > self.startY:
            return self.startX
        elif self.cursorY < self.startY:
            return self.cursorX
        else:
            return min(self.startX, self.cursorX)

    @property
    def firstY(self):
        # Returns the y coordinate of the start of the selection.
        return min(self.startY, self.cursorY)

    @property
    def lastX(self):
        # Returns the x coordinate of the end of the selection.
        if self.cursorY > self.startY:
            return self.cursorX
        elif self.cursorY < self.startY:
            return self.startX
        else:
            return max(self.startX, self.cursorX)

    @property
    def lastY(self):
        # Returns the y coordinate of the end of the selection.
        return max(self.startY, self.cursorY)

    @property
    def selectionWidth(self):
        # Returns the width of the selection (including the cursor itself).
        return self.lastX - self.firstX + 1

    @property
    def selectionHeight(self):
        # Returns the height of the selection.
        return self.lastY - self.firstY + 1

    @property
    def isAtBeginning(self):
        # Returns True if the cursor is at the beginning of the buffer.
        return self.cursorX == 0 and self.cursorY == 0

    @property
    def isAtEnd(self):
        # Returns True if the cursor is at the end of the buffer.
        return self.cursorX == len(self.currentLine) and self.cursorY == self.numberOfLines - 1

    @property
    def coordinates(self):
        # Returns a string with the x and y coordinates of the buffer.
        return f"({self.cursorY+1}, {self.cursorX+1})"

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

    def clear(self):
        # Clears the contents of the buffer.
        self.lines.clear()
        self.lines += [""]
        self.searchTerm = ""
        self._cursorX, self._cursorY = 0, 0
        self.startX, self.startY = 0, 0
        self.scrollX, self.scrollY = 0, 0
        self.maxCursorX = 0
        self.isReadOnly = False
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
            self.lines.clear()
            self.lines += [line.strip("\r\n") for line in file.readlines()]
            self.isReadOnly = not os.access(file.name, os.W_OK)

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

    def adjustScroll(self, width, gutterWidth, height):
        if self.cursorX < self.scrollX:
            self.scrollX = self.cursorX
        elif self.cursorX >= self.scrollX + width - gutterWidth - 1:
            self.scrollX = self.cursorX - width + gutterWidth + 2

        if self.cursorY < self.scrollY:
            self.scrollY = self.cursorY
        elif self.cursorY >= self.scrollY + height - 1:
            self.scrollY = self.cursorY - height + 1

    def selectedRange(self, lineNumber):
        # Returns the range of characters (start, end + 1) in the given line that are selected.
        # Returns None if the line is not inside of the selection.
        if lineNumber == self.firstY:
            return (self.firstX, self.lastX if lineNumber == self.lastY else len(self.lines[lineNumber]))
        elif lineNumber == self.lastY:
            return (0, self.lastX)
        elif self.firstY < lineNumber < self.lastY:
            return (0, len(self.lines[lineNumber]))
        else:
            return None

    def nextOccurrence(self):
        # Returns the coordinates of the next occurrence of the search term.
        # Returns None if no occurrence is found.
        1
    def startSelecting(self):
        # Starts selecting text.
        self.isSelecting = True
        self.startX, self.startY = self.cursorX, self.cursorY

    def stopSelecting(self):
        # Stops selecting text.
        self.isSelecting = False
        self.startX, self.startY = self.cursorX, self.cursorY

    def toggleSelect(self):
        # Toggles whether the buffer is selecting text.
        self.isSelecting = not self.isSelecting
        if not self.isSelecting:
            self.startX, self.startY = self.cursorX, self.cursorY

    def find(self, term):
        # Changes the search pattern to the given term.
        self.stopSelecting()
        self.searchTerm = term
        self.previousX, self.previousY = self.cursorX, self.cursorY
        if self.currentLine.find(term, self.cursorX) != self.cursorX:
            self.cursorNextOccurrenceRight()

    def cancelFind(self):
        # Cancels the search.
        self.searchTerm = ""
        self.cursorX, self.cursorY = self.previousX, self.previousY

    def cursorNextOccurrenceLeft(self, amount=1):
        # Moves the cursor to the next occurrrence of the search term facing left.
        if self.searchTerm:
            for i in range(amount):
                startX, startY = self.cursorX, self.cursorY
                index = self.currentLine.rfind(self.searchTerm, 0, self.cursorX)
                # Search from the current position.
                while index == -1 and self.cursorY != 0:
                    self.cursorLineUp()
                    self.cursorX = len(self.currentLine)
                    index = self.currentLine.rfind(self.searchTerm, 0, self.cursorX)

                # Stop searching if the pattern was found.
                if index != -1:
                    self.cursorX = index
                    continue

                # Search from the end to the current position.
                self.cursorBufferEnd()
                index = self.currentLine.rfind(self.searchTerm)
                while index == -1 and self.cursorY != startY:
                    self.cursorLineUp()
                    self.cursorX = len(self.currentLine)
                    index = self.currentLine.find(self.searchTerm, 0, self.cursorX)

                if index != -1:
                    self.cursorX = index
                else:
                    self.cursorX, self.cursorY = startX, startY
                    break

    def cursorNextOccurrenceRight(self, amount=1):
        # Moves the cursor to the next occurrrence of the search term facing right.
        if self.searchTerm:
            for i in range(amount):
                startX, startY = self.cursorX, self.cursorY
                index = self.currentLine.find(self.searchTerm, self.cursorX + 1)
                # Search from the current position.
                while index == -1 and self.cursorY != self.numberOfLines - 1:
                    self.cursorLineDown()
                    self.cursorX = 0
                    index = self.currentLine.find(self.searchTerm, self.cursorX)

                # Stop searching if the pattern was found.
                if index != -1:
                    self.cursorX = index
                    continue

                # Search from the beginning to the current position.
                self.cursorBufferBegin()
                index = self.currentLine.find(self.searchTerm)
                while index == -1 and self.cursorY != startY:
                    self.cursorLineDown()
                    self.cursorX = 0
                    index = self.currentLine.find(self.searchTerm, self.cursorX)

                if index != -1:
                    self.cursorX = index
                else:
                    self.cursorX, self.cursorY = startX, startY
                    break

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
            elif self.cursorY < self.numberOfLines - 1:
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
            if not self.isAtEnd:
                # Skip whitespace.
                while self.currentCharacter in Buffer.WHITESPACE and not self.isAtEnd:
                    self.cursorCharacterRight()

                # Move to the end of the word.
                while self.currentCharacter not in Buffer.WHITESPACE and not self.isAtEnd:
                    self.cursorCharacterRight()

    def cursorWORDLeft(self, amount=1):
        # Moves the cursor left one WORD.
        for i in range(amount):
            if not self.isAtBeginning:
                self.cursorCharacterLeft()

                # Skip whitespace.
                while not self.isAtBeginning and self.currentCharacter in Buffer.WHITESPACE:
                    self.cursorCharacterLeft()

                # Move to the beginning of the WORD.
                while not self.isAtBeginning and self.previousCharacter not in Buffer.WHITESPACE and not self.isAtBeginning:
                    self.cursorCharacterLeft()
            else:
                break

    def cursorWORDRight(self, amount=1):
        # Moves the cursor right one WORD.
        for i in range(amount):
            if not self.isAtEnd:
                # Move to the end of the WORD.
                while self.currentCharacter not in Buffer.WHITESPACE and not self.isAtEnd:
                    self.cursorCharacterRight()

                # Skip whitespace.
                while self.currentCharacter in Buffer.WHITESPACE and not self.isAtEnd:
                    self.cursorCharacterRight()
            else:
                break

    def delete(self, amount=1):
        # Deletes the text in the selection.
        for i in range(amount):
            if self.isSelecting:
                if self.selectionHeight > 1:
                    lastLine = self.lines[self.lastY][self.lastX:]
                    self._deleteTextInLine(self.firstY, self.firstX, len(self.lines[self.firstY]))
                    self.lines[self.firstY] += lastLine
                    for i in range(self.firstY + 1, self.lastY + 1):
                        self._deleteLine(self.firstY + 1)
                else:
                    self._deleteTextInLine(self.firstY, self.firstX, self.lastX)

                self.cursorX, self.cursorY = self.firstX, min(self.firstY, self.numberOfLines - 1)
                self.stopSelecting()
                self.hasUnsavedChanges = True
            else:
                break

    def deleteCharacterLeft(self, amount=1):
        # Deletes one character to the left.
        for i in range(amount):
            if self.isSelecting:
                self.delete()
            elif not self.isAtBeginning:
                self.startSelecting()
                self.cursorCharacterLeft()
                self.delete()
            else:
                break

    def deleteCharacterRight(self, amount=1):
        # Deletes one character to the right.
        for i in range(amount):
            if self.isSelecting:
                self.delete()
            elif not self.isAtEnd:
                self.startSelecting()
                self.cursorCharacterRight()
                self.delete()
            else:
                break

    def deleteLine(self, amount=1):
        # Deletes the current line.
        for i in range(amount):
            if self.isSelecting:
                self.delete()
            elif self.numberOfLines > 1:
                if self.cursorY > 0 and self.cursorY == self.numberOfLines - 1:
                    self.cursorY -= 1
                self._deleteLine(self.cursorY)
                self.cursorX = 0
                self.hasUnsavedChanges = True
            elif self.currentLine:
                self.currentLine = ""
                self.cursorX = 0
                self.hasUnsavedChanges = True
            else:
                break

    def insert(self, text, amount=1):
        # Inserts the given text at the cursor.
        for i in range(amount):
            self.delete()
            self._insertTextInLine(text, self.cursorY, self.cursorX)
            self.cursorCharacterRight(len(text))
            self.hasUnsavedChanges = True

    def insertLineAbove(self, amount=1):
        # Inserts a line above the cursor.
        if self.allowNewLines:
            for i in range(amount):
                self.stopSelecting()
                self._insertLine(self.cursorY)
                self.cursorX = 0
                self.hasUnsavedChanges = True

    def insertLineBelow(self, amount=1):
        # Inserts a line below the cursor.
        if self.allowNewLines:
            for i in range(amount):
                self.stopSelecting()
                self.cursorX = 0
                self.cursorY += 1
                self._insertLine(self.cursorY)
                self.hasUnsavedChanges = True

    def splitLine(self, amount=1):
        # Splits the current line at the cursor.
        if self.allowNewLines:
            for i in range(amount):
                if self.isSelecting:
                    self.delete()
                text = self.currentLine[self.cursorX:] if self.cursorX < len(self.currentLine) else ""
                self.currentLine = self.currentLine[:self.cursorX]
                self.insertLineBelow()
                self.currentLine = text
                self.cursorX = 0
                self.uasUnsavedChanges = True

