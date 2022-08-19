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


if __name__ == "__main__":
    pass
