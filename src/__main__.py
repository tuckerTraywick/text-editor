#!/usr/bin/env python3
import sys
from editor import Editor


if __name__ == "__main__":
    editor = Editor()
    
    editor.addKeybinding(["insert"], "Alt ' r", editor.cursorCharacterRight)

    editor.addKeybinding(["insert"], "Ctrl q", editor.quit)
    editor.addKeybinding(["insert"], "Ctrl e", editor.exit)
    editor.addKeybinding(["insert"], ["Left", "Alt j"], editor.cursorCharacterLeft)
    editor.addKeybinding(["insert"], ["Right", "Alt l"], editor.cursorCharacterRight)
    editor.addKeybinding(["insert"], ["Up", "Alt i"], editor.cursorLineUp)
    editor.addKeybinding(["insert"], ["Down", "Alt k"], editor.cursorLineDown)
    editor.addKeybinding(["insert"], ["Printable", "Space"], editor.insertCharacter)
    editor.addKeybinding(["insert"], ["Alt N"], editor.insertLineAbove)
    editor.addKeybinding(["insert"], ["Delete", "Alt d"], editor.delete)
    editor.addKeybinding(["insert"], ["Alt D"], editor.deleteLine)
    editor.addKeybinding(["insert"], ["Backspace"], editor.deleteLeft)
    editor.addKeybinding(["!insert"], ["Ctrl q", "Enter", "Backspace"], editor.setMode("insert"))
    editor.addKeybinding(["!switchBuffer", "!number"], "Ctrl b", editor.setMode("switchBuffer"))
    editor.addKeybinding(["!openFile", "!number"], "Ctrl o", editor.commandBufferPrompt("File path to open: ", "openFile"))

    editor.addKeybinding(["openFile"], "Printable", editor.commandBufferInsert)
    editor.addKeybinding(["openFile"], "Enter", editor.openFileFromCommandBuffer(len("File path to open: ")))
    editor.addKeybinding(["openFile"], "Backspace", editor.commandBufferDeleteLeft(len("File path to open: ")))
    editor.addKeybinding(["openFile"], ["Left", "Alt j"], editor.commandBufferCursorLeft(len("File path to open: ")))
    editor.addKeybinding(["openFile"], ["Right", "Alt l"], editor.commandBufferCursorRight)


    editor.addKeybinding(["switchBuffer"], ["Up", "Alt i", "i"], editor.bufferBackward)
    editor.addKeybinding(["switchBuffer"], ["Down", "Alt k", "k"], editor.bufferForward)

    if len(sys.argv) > 1:
        editor.run(sys.argv[1])
    else:
        editor.run()
