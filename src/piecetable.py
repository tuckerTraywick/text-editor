from linkedlist import Node, LinkedList


class Piece:
    # Represents an entry in a Piecetable. Stores whether the piece is from the original or append string,
    # and the indexes of span of text the piece points to.
    def __init__(self, isOriginal, startIndex, length):
        self.isOriginal = isOriginal
        self.startIndex = startIndex
        self.length = length

    def __repr__(self):
        return repr(vars(self))


class Mark:
    def __init__(self, pieceNode, index):
        self.pieceNode = pieceNode
        self.index = index

    def __repr__(self):
        return repr(vars(self))


class Selection:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __repr__(self):
        return str(vars(self))


class Piecetable:
    def __init__(self, originalString="", appendString="", pieces=None):
        self.originalString = originalString
        self.appendString = appendString
        self.pieces = LinkedList() if pieces is None else pieces

    def __repr__(self):
        return str(vars(self))

    @property
    def numberOfPieces(self):
        # Returns how many pieces the piecetable has.
        return self.pieces.length

    @property
    def text(self):
        # Returns the text the piecetable represents.
        return "".join([self.getPieceText(piece) for piece in self.pieces])

    @property
    def firstCharacterMark(self):
        # Returns a mark pointing to the first character of the piecetable.
        if self.pieces.isEmpty:
            return None
        else:
            return Mark(self.pieces.firstNode, 0)

    @property
    def firstCharacterSelection(self):
        # Returns a selection containing the first character of the piecetable.
        if self.pieces.isEmpty:
            return None
        else:
            return Selection(Mark(self.pieces.firstNode, 0), Mark(self.pieces.firstNode, 1))

    def clear(self):
        # Empties the piecetable.
        self.originalString = ""
        self.appendString = ""
        self.pieces = LinkedList()

    def getPieceText(self, piece):
        # Returns the string described by the given piece.
        if piece.isOriginal:
            return self.originalString[piece.startIndex:piece.startIndex + piece.length]
        else:
            return self.appendString[piece.startIndex:piece.startIndex + piece.length]

    def appendPiece(self, piece):
        # Appends the given piece to the piecetable.
        self.pieces.append(piece)

    def appendPiece(self, isOriginal, startIndex, length):
        # Appends a new piece with the given attributes to the piecetable.
        self.pieces.append(Piece(isOriginal, startIndex, length))

    def insertPieceBefore(self, pieceNode, piece):
        # Inserts `piece` before `pieceNode`.
        self.pieces.insertBefore(pieceNode, piece)

    def insertPieceBefore(self, pieceNode, isOriginal, startIndex, length):
        # Inserts a piece with the given attributes before `pieceNode`.
        self.pieces.insertBefore(pieceNode, Piece(isOriginal, startIndex, length))

    def insertPieceAfter(self, pieceNode, piece):
        # Inserts `piece` after `pieceNode`.
        self.pieces.insertafter(pieceNode, piece)

    def insertPieceAfter(self, pieceNode, isOriginal, startIndex, length):
        # Inserts a piece with the given attributes after `pieceNode`.
        self.pieces.isnertafter(pieceNode, Piece(isOriginal, startIndex, length))

    def removePiece(self, pieceNode):
        # Removes the piece pointed to by `pieceNode` from the piecetable.
        self.pieces.remove(pieceNode)

    def appendText(self, text):
        # Appends a new piece with the given text.
        self.appendString += text
        self.appendPiece(False, len(self.appendString) - len(text), len(text))

    def insertTextBefore(self, pieceNode, text):
        # Inserts a new piece with the given text before `pieceNode`.
        self.appendString += text
        self.insertPieceBefore(pieceNode, False, len(self.appendString) - len(text), len(text))

    def insertTextAfter(self, pieceNode, text):
        # Inserts a new piece with the given text after `pieceNode`.
        self.appendString += text
        self.insertPieceAfter(pieceNode, False, len(self.appendString) - len(text), len(text))

    def insertText(self, mark, text):
        # Inserts the given text at the given mark.
        if mark.index == 0:
            self.insertTextBefore(mark.pieceNode, text)
        else:
            self.insertTextAfter(mark.pieceNode, self.getPieceText(mark.pieceNode.data)[mark.index:] + text)
            mark.pieceNode.data.length -= mark.index
            #if mark.pieceNode.data.length == 0:
            #    self.removePiece(mark.pieceNode)

    def deleteText(self, selection):
        # Deletes the given selection and returns the node to the left of the selection.
        start, end = selection.start, selection.end
        # Shorten/remove the start node.
        start.pieceNode.data.length = start.index
        if start.pieceNode.data.length == 0:
            self.removePiece(start.pieceNode)
        # Delete middle nodes.
        currentPieceNode = start.pieceNode
        while currentPieceNode is not end.pieceNode:
            self.removePiece(currentPieceNode)
            currentPieceNode = currentPieceNode.next
        # Shorten/remove the end node.
        if end.pieceNode is not start.pieceNode:
            end.pieceNode.data.length = end.index - end.pieceNode.data.index
            if end.pieceNode.data.length == 0:
                self.removePiece(end.pieceNode)

    def readFromFile(self, file):
        # Reads the contents of the given file into the piecetable. Returns the number of lines in the file.
        assert file.readable()
        self.clear()
        lines = file.readlines()
        self.originalString = "".join(lines)
        self.appendPiece(True, 0, len(self.originalString))
        return len(lines)

    def writeToFile(self, file):
        # Write the contents of the piecetable to the given file.
        assert file.writable()
        file.write("".join(self.getPieceText(piece) for piece in self.pieces))

