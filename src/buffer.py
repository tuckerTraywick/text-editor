import os


class Line:
    # A node that stores a line of text. Chained together by `Buffer` to form a linked list.
    def __init__(self, text="", previous=None, next=None):
        self.previous = previous
        self.next = next
        self.text = text

    @property
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
        assert pos <= self.length
        self.text = self.text[:pos] + string + self.text[pos:]

    def deleteText(self, start, numberOfCharacters=1):
        # Deletes `numberOfCharacters` characters from the line starting at position `start`.
        assert start >= 0
        assert start + numberOfCharacters <= self.length
        self.text = self.text[:start] + self.text[start + numberOfCharacters:]

    def append(self, next):
        # Appends the given Line to the end of this line.
        self.next = next
        next.previous = self

    def insertBefore(self, previous):
        # Inserts the given line before this line.
        if self.previous is not None:
            self.previous.next = previous
            previous.previous = self.previous
        self.previous = previous
        previous.next = self

    def insertAfter(self, next):
        # Inserts the given line after this line.
        if self.next is not None:
            self.next.previous = next
            next.next = self.next
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
    def __init__(self, pageWidth, pageHeight, visualTabWidth, softTabWidth, name=""):
        self.pageWidth = pageWidth
        self.pageHeight = pageHeight
        self.visualTabWidth = visualTabWidth
        self.softTabWidth = softTabWidth
        self.name = name
        self.clear()
    
    @property
    def status(self):
        if self.hasUnsavedChanges:
            return " [+]"
        elif self.isReadOnly:
            return " [ro]"
        else:
            return ""

    @property
    def position(self):
        return (self.cursorY + 1, self.cursorX + 1)

    @property
    def fullName(self):
        return f"{self.name} {self.position}{self.status}"

    def clear(self):
        # Wipes the buffer and resets it.
        self.isReadOnly = False
        self.hasUnsavedChanges = False
        self.scrollX = self.scrollY = 0
        self.cursorX = self.cursorY = self.maxCursorX = 0
        self.markerX = self.markerY = -1
        self.numberOfLines = 1
        self.firstLine = self.lastLine = self.topLine = self.currentLine = Line()

    def draw(self, editor, height, x, y, showLineNumbers=True, relativeLineNumbers=False, showEmptyLineFill=True, showCursor=True, activeCursor=True, highlightCurrentLine=True):
        currentLine = self.topLine
        gutterWidth = max(editor.getSetting("minimumGutterWidth"), len(str(self.numberOfLines)))
        lineWidth = editor.terminal.width - gutterWidth - x - 1 if showLineNumbers else self.pageWidth - x
        for i in range(height):
            # If the loop hasn't gone past the last line, print the current line number and line. Else, print the empty line fill if necessary.
            if currentLine is not None:
                # If the loop is on the current line, highlight the line number and print it if needed. Else, just print the line number if needed.
                if currentLine is self.currentLine:
                    # Highlight the line number if necessary.
                    if highlightCurrentLine:
                        print(editor.getColor("currentLine"), end="")
                    # Print the line number if needed.
                    if showLineNumbers:
                        if relativeLineNumbers:
                            editor.print("currentLineNumber", f"{self.cursorY + 1:<{gutterWidth}} ", end="")
                        else:
                            editor.print("currentLineNumber", f"{self.scrollY + i + 1:>{gutterWidth}} ", end="")
                elif showLineNumbers:
                    # Print the line number if needed.
                    if relativeLineNumbers:
                        editor.print("lineNumber", f"{abs(self.cursorY - self.scrollY - i):>{gutterWidth}} ", end="")
                    else:
                        editor.print("lineNumber", f"{self.scrollY + i + 1:>{gutterWidth}} ", end="")
                
                # Print the current line.
                editor.print("default", (editor.getColor("currentLine") if highlightCurrentLine and currentLine is self.currentLine else "") + currentLine.text.ljust(lineWidth), end="\r")
                currentLine = currentLine.next
            elif showEmptyLineFill:
                editor.print("emptyLineFill", editor.getSetting("emptyLineFill"), end="\r")
            else:
                print("", end="\r")
            
            # Print the newline character if this isn't the last line.
            if i < height - 1 and i < editor.terminal.height:
                print("", end="\n")

        # Draw the cursor if necessary.
        if showCursor:
            with editor.terminal.location(x + (self.cursorX + gutterWidth + 1 if showLineNumbers else self.cursorX), y + self.cursorY - self.scrollY):
                character = self.currentLine.text[self.cursorX] if self.cursorX < self.currentLine.length else " "
                editor.print("activeCursor" if activeCursor else "inactiveCursor", character, end="")

    def open(self, filePath, readOnly=False):
        # Opens the given file and reads it into the buffer. Closes the buffer first.
        self.clear()
        self.isReadOnly = readOnly
        file = open(filePath, "r")
        assert file.readable()
        # Loop through each line in the file and append it to the buffer.
        for i, line in enumerate(file.readlines()):
            if i == 0:
                self.firstLine.text = line[:-1]
            else:
                self.lastLine.append(Line(line[:-1]))
                self.lastLine = self.lastLine.next
                self.numberOfLines += 1

    def write(self, filePath, createNewFiles=False):
        # Write the buffer to the given file.
        assert not self.isReadOnly
        file = open(filePath, "w+" if createNewFiles else "w")
        assert file.writable()
        # Make sure the file is empty before writing.
        file.seek(0)
        file.truncate()
        currentLine = self.firstLine
        while currentLine is not None:
            file.write(currentLine.text + "\n")
            currentLine = currentLine.next
        self.hasUnsavedChanges = False

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
                self.cursorX = min(self.cursorX, self.currentLine.length)
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
                self.cursorX = min(self.cursorX, self.currentLine.length)
                if self.cursorY > self.scrollY + self.pageHeight - 1:
                    self.scrollLineDown()
            elif self.cursorX < self.currentLine.length:
                self.cursorX = self.currentLine.length
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
                self.cursorX = self.currentLine.length
            else:
                break

    def cursorCharacterRight(self, amount=1):
        for i in range(amount):
            if self.cursorX < self.currentLine.length:
                self.cursorX += 1
            elif self.cursorY < self.numberOfLines - 1:
                self.cursorLineDown()
                self.cursorX = 0
            elif self.scrollY < self.numberOfLines - 1:
                self.scrollLineDown()
            else:
                break

    def cursorLineStart(self, amount=1):
        for i in range(amount):
            if self.cursorX > 0:
                self.cursorX = 0
            elif self.cursorY > 0:
                self.cursorLineUp()
                self.cursorX = 0
            else:
                break

    def cursorLineEnd(self, amount=1):
        for i in range(amount):
            if self.cursorX < self.currentLine.length:
                self.cursorX = self.currentLine.length
            elif self.cursorY < self.numberOfLines - 1:
                self.cursorLineDown()
                self.cursorX = self.currentLine.length
            else:
                break

    def cursorBufferStart(self):
        self.cursorX = self.cursorY = self.scrollY = 0
        self.currentLine = self.topLine = self.firstLine

    def deleteLine(self, amount=1):
        for i in range(amount):
            if self.numberOfLines == 1:
                if self.currentLine.hasText():
                    self.currentLine.clearText()
                    self.cursorX = 0
                else:
                    break
            else:
                lineToDelete = self.currentLine
                if lineToDelete is self.lastLine:
                    self.cursorLineUp()
                    self.lastLine = self.currentLine
                    if lineToDelete is self.topLine:
                        self.scrollLineUp()
                else:
                    self.cursorLineDown()
                    self.cursorY -= 1
                    if lineToDelete is self.firstLine:
                        self.firstLine = self.currentLine

                    if lineToDelete is self.topLine:
                        self.scrollLineDown()
                        self.scrollY -= 1
                lineToDelete.remove()
                self.numberOfLines -= 1
            self.hasUnsavedChanges = True

    def deleteCharacterLeft(self, amount=1):
        for i in range(amount):
            if self.cursorX > 0 or self.cursorY > 0:
                self.cursorCharacterLeft()
                self.deleteCharacterRight()
            else:
                break

    def deleteCharacterRight(self, amount=1):
        for i in range(amount):
            if self.cursorX < self.currentLine.length:
                self.currentLine.deleteText(self.cursorX, 1)
            elif self.cursorY < self.numberOfLines - 1:
                self.currentLine.text += self.currentLine.next.text
                if self.lastLine is self.currentLine.next:
                    self.lastLine = self.currentLine
                self.currentLine.next.remove()
                self.numberOfLines -= 1
            else:
                break

    def delete(self):
        pass

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
            if self.firstLine is self.currentLine:
                self.firstLine = newLine

            if self.topLine is self.currentLine:
                self.topLine = newLine
            self.currentLine.insertBefore(newLine)
            self.numberOfLines += 1
            self.currentLine = newLine
            self.cursorX = 0
            self.hasUnsavedChanges = True

    def insertLineBelow(self, amount=1):
        for i in range(amount):
            newLine = Line()
            if self.lastLine is self.currentLine:
                self.lastLine = newLine
            self.currentLine.insertAfter(newLine)
            self.numberOfLines += 1
            self.cursorLineDown()
            self.hasUnsavedChanges = True

