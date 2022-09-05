import os


class Line:
    # A node that stores a line of text. Chained together by `Buffer` to form a linked list.
    def __init__(self, text="", previous=None, next=None):
        self.previous = previous
        self.next = next
        self.text = text

    def length(self):
        # Returns the length of the line.
        return len(self.text)

    def hasText(self):
        # Returns True if the line has at least 1 character of text.
        return len(self.text) > 0

    def clearText(self):
        # Empties the line's text.
        self.text = ""

    def insertText(self, pos, string):
        # Inserts `string` at position `pos` in the line.
        assert pos <= self.length()
        self.text = self.text[:pos] + string + self.text[pos:]

    def deleteText(self, start, numberOfCharacters=1):
        # Deletes `numberOfCharacters` characters from the line starting at position `start`.
        assert start >= 0
        assert start + numberOfCharacters <= self.length()
        self.text = self.text[:start] + self.text[start + numberOfCharacters:]

    def append(self, next):
        # Appends the given Line to the end of this line.
        self.next = next
        next.previous = self

    def remove(self):
        # Removes this line from between its neighbors.
        if self.previous is not None:
            self.previous.next = self.next

        if self.next is not None:
            self.next.previous = self.previous


class Buffer:
    # Represents a piece of text split into lines. A buffer has a linked list of lines and a cursor. The cursor represents the user's
    # position in the text and can be moved around the buffer in various ways. All edits to the buffer take place at the position of 
    # the cursor. The buffer can view one page of text at a time. The width and height of the page determine how many lines
    # the buffer can display at once and how long of a line the buffer can display, respectively. The buffer will scroll automatically 
    # when the cursor is moved out of the page, but it can also be scrolled manually.
    def __init__(self, pageWidth, pageHeight, visualTabWidth, softTabWidth):
        self.pageWidth = pageWidth
        self.pageHeight = pageHeight
        self.visualTabWidth = visualTabWidth
        self.softTabWidth = softTabWidth
        self.close()

    def close(self):
        # Wipes the buffer and resets it.
        self.filePath = None
        self.isReadOnly = False
        self.hasUnsavedChanges = False
        self.scanningRight = True
        self.selecting = False
        self.scrollX = self.scrollY = 0
        self.cursorX = self.cursorY = self.maxCursorX = 0
        self.markerX = self.markerY = 0
        self.numberOfLines = 1
        self.firstLine = self.lastLine = self.topLine = self.currentLine = Line()
    
    def open(self, filePath, readOnly=False):
        # Opens the given file and reads it into the buffer. Closes the buffer first.
        self.close()
        self.filePath = filePath
        self.isReadOnly = readOnly
        file = open(filePath, "r")
        assert file.readable()
        for i, line in enumerate(file.readlines()):
            if i == 0:
                self.firstLine.text = line[:-1]
            else:
                self.lastLine.append(Line(line[:-1]))
                self.lastLine = self.lastLine.next
                self.numberOfLines += 1

    def write(self, create=False):
        # Write the buffer to the file it is currently editing.
        # The buffer must be editing a file.
        assert self.filePath is not None
        assert not self.readOnly
        file = open(self.filePath, "w+" if create else "w")
        assert file.writable()
        # Make sure the file is empty before writing.
        file.seek(0)
        file.truncate()
        currentLine = self.firstLine
        while currentLine is not None:
            file.write(currentLine.text + "\n")
            currentLine = currentLine.next
        self.unsavedChanges = False

    def scrollLineUp(self, amount=1):
        for i in range(amount):
            if self.scrollY > 0:
                self.topLine = self.topLine.previous
                self.scrollY -= 1
            else:
                break

    def scrollLineDown(self, amount=1):
        for i in range(amount):
            if self.scrollY < self.numberOfLines - 1:
                self.topLine = self.topLine.next
                self.scrollY += 1
            else:
                break

    def cursorLineUp(self, amount=1):
        for i in range(amount):
            if self.cursorY > 0:
                self.currentLine = self.currentLine.previous
                self.cursorY -= 1
                self.cursorX = min(self.cursorX, self.currentLine.length())
                if self.cursorY < self.scrollY:
                    self.scrollLineUp()
            else:
                break

    def cursorLineDown(self, amount=1):
        for i in range(amount):
            if self.cursorY < self.numberOfLines - 1:
                self.currentLine = self.currentLine.next
                self.cursorY += 1
                self.cursorX = min(self.cursorX, self.currentLine.length())
                if self.cursorY > self.scrollY + self.pageHeight:
                    self.scrollLineDown()
            elif self.scrollY < self.numberOfLines - 1:
                self.scrollLineDown()
            else:
                break

    def cursorCharacterLeft(self, amount=1):
        for i in range(amount):
            if self.cursorX > 0:
                self.cursorX -= 1
            elif self.cursorY > 0:
                self.cursorLineUp()
                self.cursorX = self.currentLine.length()
            else:
                break

    def cursorCharacterRight(self, amount=1):
        for i in range(amount):
            if self.cursorX < self.currentLine.length():
                self.cursorX += 1
            elif self.cursorY < self.numberOfLines - 1:
                self.cursorLineDown()
                self.cursorX = 0
            elif self.scrollY < self.numberOfLines - 1:
                self.scrollLineDown()
            else:
                break

    def insertLineAbove(self, amount=1):
        for i in range(amount):
            newLine = Line()
            if self.cursorY > 0:
                self.currentLine.previous.append(newLine)
            else:
                if self.topLine is self.firstLine:
                    self.topLine = newLine
                
                if self.numberOfLines == 1:
                    self.lastLine = self.newLine
                self.firstLine = newLine
                self.currentLine.previous = newLine
            newLine.append(self.currentLine)
            self.numberOfLines += 1
            self.currentLine = newLine
            self.cursorX = min(self.cursorX, self.currentLine.length())

    def insert(self, amount=1, text=""):
        for i in range(amount):
            self.currentLine.insertText(self.cursorX, text)
            self.cursorCharacterRight(len(text))

    def deleteCharacterRight(self, amount=1):
        for i in range(amount):
            if self.currentLine.hasText() and self.cursorX < self.currentLine.length():
                self.currentLine.deleteText(self.cursorX)
            elif self.cursorY < self.numberOfLines - 1:
                self.deleteLine()
            else:
                break


"""
    def cursorBeginLine(self, amount=1):
        for i in range(amount):
            if self.canMoveLeftCharacter():
                self.cursorX = 0
            elif self.canMoveLineUp():
                self.cursorLineUp()
                self.cursorX = 0
            else:
                break

    def cursorEndLine(self, amount=1):
        for i in range(amount):
            if self.canMoveRightCharacter():
                self.cursorX = self.currentLine.length
            elif self.canMoveLineDown():
                self.cursorLineDown()
                self.cursorX = self.currentLine.length
            elif self.canScrollLineDown():
                self.scrollLineDown()
            else:
                break

    def cursorLeftCharacter(self, amount=1):
        for i in range(amount):
            if self.canMoveLeftCharacter():
                self.cursorX -= 1
            elif self.canMoveLineUp():
                self.cursorLineUp()
                self.cursorX = self.currentLine.length
            else:
                break

    def cursorRightCharacter(self, amount=1):
        for i in range(amount):
            if self.canMoveRightCharacter():
                self.cursorX += 1
            elif self.canMoveLineDown():
                self.cursorLineDown()
                self.cursorX = 0
            else:
                break

    def cursorLeftWord(self, amount=1):
        for i in range(amount):
            if self.isAtBeginning():
                break

            if self.currentCharacter() not in "\n\r\t ":
                self.cursorLeftCharacter()

            while not self.isAtBeginning() and self.currentCharacter() in "\n\r\t ":
                self.cursorLeftCharacter()

            if not self.isAtBeginning() and self.currentCharacter().isalnum() or self.currentCharacter() == "_":
                while not self.isAtBeginning() and (self.currentCharacter().isalnum() or self.currentCharacter() == "_"):
                    self.cursorLeftCharacter()
                self.cursorRightCharacter()

    def cursorRightWord(self, amount=1):
        self.turnRight()
        for i in self.repeat(amount):
            if not self.scanOverAlphaNum():
                self.scanForward()
            self.scanOverWhitespace()
        for i in range(amount):
            if self.isAtEnd():
                break
            
            if self.currentCharacter().isalnum() or self.currentCharacter() == "_":
                while not self.isAtEnd() and (self.currentCharacter().isalnum() or self.currentCharacter() == "_"):
                    self.cursorRightCharacter()
            else:
                self.cursorRightCharacter()

            while not self.isAtEnd() and self.currentCharacter() in "\n\r\t ":
                self.cursorRightCharacter()

    def cursorWordEnd(self, amount=1):
        for i in range(amount):
            if self.isAtEnd():
                break
            
            while not self.isAtEnd() and self.currentCharacter() in "\n\r\t ":
                self.cursorRightCharacter()

            if self.currentCharacter().isalnum() or self.currentCharacter() == "_":
                while not self.isAtEnd() and (self.currentCharacter().isalnum() or self.currentCharacter() == "_"):
                    self.cursorRightCharacter()
            else:
                self.cursorRightCharacter()

    def cursorWordEndLeft(self, amount=1):
        for i in range(amount):
            if self.isAtBeginning():
                break
            
            if self.currentCharacter().isalnum() or self.currentCharacter() == "_":
                while not self.isAtBeginning() and (self.currentCharacter().isalnum() or self.currentCharacter() == "_"):
                    self.cursorLeftCharacter()

            while not self.isAtBeginning() and self.currentCharacter() in "\n\r\t ":
                self.cursorLeftCharacter()

    def cursorLeftWORD(self, amount=1):
        for i in range(amount):
            if self.isAtBeginning():
                break
            
            if self.currentCharacter() not in "\n\r\t ":
                self.cursorLeftCharacter()

            while not self.isAtBeginning() and self.currentCharacter() in "\n\r\t ":
                self.cursorLeftCharacter()

            while not self.isAtBeginning() and self.currentCharacter() not in "\n\r\t ":
                self.cursorLeftCharacter()

            if not self.isAtBeginning():
                self.cursorRightCharacter()

    def cursorRightWORD(self, amount=1):
        for i in range(amount):
            if self.isAtEnd():
                break
            
            while not self.isAtEnd() and self.currentCharacter() not in "\n\r\t ":
                self.cursorRightCharacter()

            while not self.isAtEnd() and self.currentCharacter() in "\n\r\t ":
                self.cursorRightCharacter()

    def insertText(self, text):
        assert text is not None
        self.currentLine.setText(self.currentLine.text[:self.cursorX] + text + self.currentLine.text[self.cursorX:])
        self.cursorX += len(text)

    def insertLineAbove(self, amount=1, text=""):
        assert text is not None
        for i in range(amount):
            newLine = Line(text, previous=self.currentLine.previous if self.currentLine is not None else None, next=self.currentLine)
            if self.canMoveLineUp():
                self.currentLine.previous.next = newLine
                self.currentLine.previous = newLine
                self.cursorLineUp()
                self.cursorY += 1  # Correct the y position.
            else:
                self.firstLine = newLine
                if self.currentLine is not None:
                    self.currentLine.previous = newLine
                self.currentLine = self.topLine = newLine
            self.numberOfLines += 1
            self.cursorX = 0

    def insertLineBelow(self, amount=1, text=""):
        assert text is not None
        for i in range(amount):
            newLine = Line(text, previous=self.currentLine, next=self.currentLine.next if self.currentLine is not None else None)
            if self.canMoveLineDown():
                self.currentLine.next.previous = newLine
                self.currentLine.next = newLine
                self.cursorLineDown()
            else:
                self.lastLine = newLine
                if self.currentLine is not None:
                    self.currentLine.next = newLine
                self.cursorLineDown()
            self.numberOfLines += 1
            self.cursorX = 0

    def insertLine(self, amount=1):
        for i in range(amount):
            if self.hasLine():
                if self.cursorX == 0:
                    self.insertLineAbove()
                    self.cursorLineDown()
                else:
                    text = self.currentLine.text[self.cursorX:]
                    self.currentLine.setText(self.currentLine.text[:self.cursorX])
                    self.insertLineBelow(1, text)
            else:
                self.currentLine = self.firstLine = self.topLine = Line()

    def deleteLine(self, amount=1):
        if self.hasLine():
            for i in range(amount):
                if self.numberOfLines == 1:
                    self.currentLine.setText("")
                    self.cursorX = 0
                    break
                elif self.canMoveLineDown():
                    if self.topLine is self.currentLine:
                        self.topLine = self.currentLine.next
                    self.currentLine.next.previous = self.currentLine.previous
                    if self.canMoveLineUp():
                        self.currentLine.previous.next = self.currentLine.next
                    else:
                        self.firstLine = self.currentLine.next
                    self.currentLine = self.currentLine.next
                else:
                    self.currentLine.previous.next = None
                    self.lastLine = self.currentLine.previous
                    self.cursorLineUp()
                self.numberOfLines -= 1
    
    def deleteCharacter(self, amount=1):
        if self.hasLine():
            for i in range(amount):
                if not self.canMoveRightCharacter() and self.canMoveLineDown():
                    self.currentLine.next.text = self.currentLine.text + self.currentLine.next.text
                    self.deleteLine()
                elif self.currentLine.text:
                    self.currentLine.setText(self.currentLine.text[:self.cursorX]  + self.currentLine.text[self.cursorX + 1:])
    
    def deleteCharacterLeft(self, amount=1):
        if self.hasLine():
            for i in range(amount):
                if self.canMoveLeftCharacter() or self.canMoveLineUp():
                    self.cursorLeftCharacter()
                    self.deleteCharacter()
                else:
                    break
"""

