from linkedlist import Node, LinkedList


class Piece:
    def __init__(self, isOriginal, startIndex, length):
        self.isOriginal = isOriginal
        self.startIndex = startIndex
        self.length = length


class PieceTable:
    def __init__(self, originalString="", appendString="", pieces=None):
        self.originalString = originalString
        self.appendString = appendString
        self.pieces = LinkedList() if pieces is None else pieces

    @property
    def numberOfPieces(self):
        # Returns how many pieces the piecetable has.
        return self.pieces.length

    def clear(self):
        # Empties the piecetable.
        self.originalString = ""
        self.appendString = ""
        self.pieces = LinkedList()

    def getPieceText(self, piece):
        # Returns the string described by the given piece.
        if piece.isOriginal:
            return self.originalString[piece.startIndex:piece.length]
        else:
            return self.appendString[piece.startIndex:piece.length]

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
        self.pieces.isnertBefore(pieceNode, Piece(isOriginal, startIndex, length))

    def insertPieceAfter(self, pieceNode, piece):
        # Inserts `piece` after `pieceNode`.
        self.pieces.insertafter(pieceNode, piece)

    def insertPieceAfter(self, pieceNode, isOriginal, startIndex, length):
        # Inserts a piece with the given attributes after `pieceNode`.
        self.pieces.isnertafter(pieceNode, Piece(isOriginal, startIndex, length))

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

    def readFromFile(self, file):
        # Reads the contents of the given file into the piecetable.
        assert file.readable()
        self.clear()
        self.originalString = file.read()
        self.appendPiece(True, 0, len(self.originalString))

    def writeToFile(self, file):
        # Write the contents of the piecetable to the given file.
        assert file.writable()
        file.write("".join(self.getPieceText(piece) for piece in self.pieces))



table = PieceTable()
table.appendText("asdf")

file = open("/home/tucker/Documents/code/text-editor/example.txt", "w")
table.writeToFile(file)
file.close()


file = open("/home/tucker/Documents/code/text-editor/example.txt", "r")
print(file.read())
file.close()


