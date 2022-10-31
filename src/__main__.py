#!/usr/bin/env python3
import sys
from editor import Editor


"""if __name__ == "__main__":
    editor = Editor()
    if len(sys.argv) > 1:
        editor.run(sys.argv[1:])
    else:
        editor.run()"""


if __name__ == "__main__":
    editor = Editor()

    leader = "Space"
    editor.addKeybinding("all", ["Ctrl q", f"Alt {leader} q"], editor.quit)
    editor.addKeybinding("all", ["Ctrl e", f"Alt {leader} e"], editor.exit)

    editor.addKeybinding(["edit"], ["Ctrl f"], editor.setMode("findBuffer"))
    editor.addKeybinding(["edit"], ["Alt /"], editor.setMode("find"))
    editor.addKeybinding(["edit"], ["Alt Space j", "Alt Space Alt j"], editor.tabLeft)
    editor.addKeybinding(["edit"], ["Alt Space l", "Alt Space Alt l"], editor.tabRight)
    editor.addKeybinding(["edit"], ["Ctrl o"], editor.setMode("findFile"))
    editor.addKeybinding(["edit", "findBuffer", "find"], ["Printable", "Space"], editor.insertCharacter)
    editor.addKeybinding(["edit"], ["Up", "Alt i"], editor.cursorLineUp)
    editor.addKeybinding(["edit"], ["Down", "Alt k"], editor.cursorLineDown)
    editor.addKeybinding(["edit", "find"], ["Alt n"], editor.cursorNextSearchResult)
    editor.addKeybinding(["edit", "find"], ["Alt p"], editor.cursorPreviousSearchResult)
    editor.addKeybinding(["edit", "findBuffer", "find"], ["Alt s"], editor.cursorLineBegin)
    editor.addKeybinding(["edit", "findBuffer", "find"], ["Alt e"], editor.cursorLineEnd)
    editor.addKeybinding(["edit", "findBuffer", "find"], ["Left", "Alt j"], editor.cursorCharacterLeft)
    editor.addKeybinding(["edit", "findBuffer", "find"], ["Right", "Alt l"], editor.cursorCharacterRight)
    editor.addKeybinding(["edit", "findBuffer", "find"], ["Alt U"], editor.cursorWORDLeft)
    editor.addKeybinding(["edit", "findBuffer", "find"], ["Alt O"], editor.cursorWORDRight)
    editor.addKeybinding(["edit", "findBuffer", "find"], ["Alt P"], editor.cursorWORDEnd)
    editor.addKeybinding(["edit", "findBuffer", "find"], ["Alt a"], editor.insertLineAbove)
    editor.addKeybinding(["edit"], ["Alt b"], editor.insertLineBelow)
    editor.addKeybinding(["edit"], ["Enter"], editor.splitLine)
    editor.addKeybinding(["edit", "findBuffer", "find"], ["Alt m"], editor.toggleSelect)
    editor.addKeybinding(["edit", "findBuffer", "find"], ["Backspace"], editor.deleteCharacterLeft)
    editor.addKeybinding(["edit", "findBuffer", "find"], ["Delete", "Alt d"], editor.deleteCharacterRight)
    editor.addKeybinding(["edit", "findBuffer", "find"], ["Alt D"], editor.deleteLine)

    editor.addKeybinding(["findBuffer"], ["Alt q", "Ctrl q"], editor.cancelBufferSearch)
    editor.addKeybinding(["findBuffer"], ["Up", "Alt i"], editor.previousBufferSearchResult)
    editor.addKeybinding(["findBuffer"], ["Down", "Alt k"], editor.nextBufferSearchResult)
    editor.addKeybinding(["findBuffer"], ["Enter"], editor.selectBufferSearchResult)

    editor.addKeybinding(["find"], ["Alt q", "Ctrl q"], editor.cancelSearch)
    editor.addKeybinding(["find"], ["Enter"], editor.confirmSearch)


    #editor.addKeybinding(["openFile"], ["Up", "Alt i"], editor.openFilePrevious)
    #editor.addKeybinding(["openFile"], ["Down", "Alt k"], editor.openFileNext)
    #editor.addKeybinding(["openFile"], ["Enter"], editor.openFileConfirm)
    #editor.addKeybinding(["openFile"], ["Tab"], editor.openFileComplete)

    if len(sys.argv) > 1:
        editor.run(sys.argv[1:])
    else:
        editor.run()

