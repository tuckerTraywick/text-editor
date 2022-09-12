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
    def __init__(self, pageWidth, pageHeight, visualTabWidth, softTabWidth, index, name=""):
        self.pageWidth = pageWidth
        self.pageHeight = pageHeight
        self.visualTabWidth = visualTabWidth
        self.softTabWidth = softTabWidth
        self.index = 0
        self.name = name
        self.clear()

    def clear(self):
        # Wipes the buffer and resets it.
        self.isReadOnly = False
        self.hasUnsavedChanges = False
        self.scrollX = self.scrollY = 0
        self.cursorX = self.cursorY = self.maxCursorX = 0
        self.markerX = self.markerY = -1
        self.numberOfLines = 1
        self.firstLine = self.lastLine = self.topLine = self.currentLine = Line()
    
    @property
    def status(self):
        if self.hasUnsavedChanges:
            return "[+] "
        elif self.isReadOnly:
            return "[ro] "
        else:
            return ""

    @property
    def coords(self):
        return f"({self.cursorY + 1}, {self.cursorX + 1})"

    @property
    def fullName(self):
        return self.status + self.name + " " + self.coords

    def open(self, filePath, readOnly=False):
        # Opens the given file and reads it into the buffer. Closes the buffer first.
        self.clear()
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

    def write(self, filePath):
        # Write the buffer to the given file.
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

    def hasSelection(self):
        return self.markerX != self.markerY != -1

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
    
    def startSelection(self):
        self.markerX, self.markerY = self.cursorX, self.cursorY

    def cancelSelection(self):
        self.markerX = self.markerY = -1

    def cursorLineUp(self, amount=1):
        for i in range(amount):
            if self.cursorY > 0:
                self.currentLine = self.currentLine.previous
                self.cursorY -= 1
                self.cursorX = min(self.cursorX, self.currentLine.length())
                if self.cursorY < self.scrollY:
                    self.scrollLineUp()
            elif self.cursorX > 0:
                self.cursorX = 0
            else:
                break

    def cursorLineDown(self, amount=1):
        for i in range(amount):
            if self.cursorY < self.numberOfLines - 1:
                self.currentLine = self.currentLine.next
                self.cursorY += 1
                self.cursorX = min(self.cursorX, self.currentLine.length())
                if self.cursorY > self.scrollY + self.pageHeight - 1:
                    self.scrollLineDown()
            elif self.cursorX < self.currentLine.length():
                self.cursorX = self.currentLine.length()
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

    def delete(self):
        if self.hasSelection():
            while abs(self.markerY - self.cursorY):
                self.deleteLine()
                if self.cursorY > self.markerY:
                    self.cursorUpLine()
                else:
                    self.cursorDownLine()
            self.currentLine.deleteText(min(self.markerX, self.cursorX), max(self.markerX, self.cursorX))
            self.cursorX = min(self.markerX, self.cursorX)

    def insert(self, amount=1, text=""):
        for i in range(amount):
            if self.hasSelection():
                self.delete()
            self.currentLine.insertText(self.cursorX, text)
            self.cursorCharacterRight(len(text))
        self.hasUnsavedChanges = True

    def insertLineAbove(self, amount=1):
        for i in range(amount):
            newLine = Line()
            if self.cursorY > 0:
                self.currentLine.previous.append(newLine)
            else:
                if self.topLine is self.firstLine:
                    self.topLine = newLine
                
                if self.numberOfLines == 1:
                    self.lastLine = newLine
                self.firstLine = newLine
                self.currentLine.previous = newLine
            newLine.append(self.currentLine)
            self.numberOfLines += 1
            self.currentLine = newLine
            self.cursorX = min(self.cursorX, self.currentLine.length())
        self.hasUnsavedChanges = True

    def insertLineBelow(self, amount=1):
        for i in range(amount):
            if self.numberOfLines == 1:
                self.insertLineAbove()
                self.cursorLineUp()
            else:
                self.cursorLineDown()
                self.insertLineAbove()
