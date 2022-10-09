#!/usr/bin/env python3
import sys
from editor import Editor


if __name__ == "__main__":
    editor = Editor()
    if len(sys.argv) > 1:
        editor.run(sys.argv[1:])
    else:
        editor.run()

"""
if __name__ == "__main__":
    editor = Editor()

    editor.addMode("homeMenu", {
        "draw": editor.homeMenuDraw,
    })
    editor.addMode("edit", {
        "begin": editor.editBegin,
        "end": editor.editEnd,
    })
    editor.addMode("findBuffer", {
        "begin": editor.findBufferBegin,
        "end": editor.findBufferEnd,
        "draw": editor.findBufferDraw,
        "refreshSearchResults": editor.findBufferRefreshSearchResults,
        "chooseSearchResult": editor.findBufferChooseSearchResult,
        "nextSearchResult": editor.findBufferNextSearchResult,
        "previousSearchResult": editor.findBufferPreviousSearchResult,
        "overlap": editor.findBufferOverlap,
        "highlight": editor.highlightMatches,
    })
    editor.addMode("findFile", {
        "begin": editor.findFileBegin,
        "end": editor.findFileEnd,
        "draw": editor.findFileDraw,
        "refreshSearchResults": editor.findFileRefreshSearchResults,
        "chooseSearchResult": editor.findFileChooseSearchResult,
        "nextSearchResult": editor.findFileNextSearchResult,
        "previousSearchResult": editor.findFilePreviousSearchResult,
        "overlap": editor.findFileOverlap,
        "highlight": editor.highlightMatches,
    })

    editor.setSettings("all", {
        "defaultMode": "edit",
        "showLineNumbers": True,
        "relativeLineNumbers": False,
        "showStatusLine": True,
    })
    editor.setSettings(["findBuffer", "findFile"], {
        "fullscreen": False,
    })

    editor.setColors("all", {
        "lineNumber": editor.terminal.gray40,
        "emptyLineFill": editor.terminal.gray40,
        "currentLine": editor.terminal.on_gray17,
        "currentSelection": editor.terminal.normal,
        "statusLine": editor.terminal.on_gray22,
        "tabList": editor.terminal.gray60_on_gray22,
        "currentTab": editor.terminal.bold,
        "inactiveCursor": editor.terminal.on_slategray,
        "file": editor.terminal.default,
        "directory": editor.terminal.lightsteelblue2,
        "workingDirectory": editor.terminal.italic_gray60,
        "match": editor.terminal.khaki3,
    })

    leader = "Space"
    editor.addKeybinding("all", ["Ctrl q", f"Alt {leader} q"], editor.quit)
    editor.addKeybinding("all", ["Ctrl e", f"Alt {leader} e"], editor.exit)
    editor.addKeybinding(["edit"], ["Ctrl s", f"Alt {leader} s"], editor.saveBuffer)
    editor.addKeybinding(["edit"], ["Ctrl a", f"Alt {leader} a"], editor.saveAllBuffers)
    editor.addKeybinding(["edit"], ["Ctrl c", f"Alt {leader} c"], editor.closeBuffer)
    editor.addKeybinding(["edit"], ["Ctrl x", f"Alt {leader} x"], editor.killBuffer)
    editor.addKeybinding("!findBuffer", ["Ctrl f", f"Alt {leader} f"], editor.setMode("findBuffer"))
    editor.addKeybinding("!findFile", ["Ctrl o", f"Alt {leader} o"], editor.setMode("findFile"))

    editor.addKeybinding(["edit", "findBuffer", "findFile"], ["Printable", "Space"], editor.insertCharacter)
    editor.addKeybinding(["edit"], ["Up", "Alt i"], editor.cursorLineUp)
    editor.addKeybinding(["edit"], ["Down", "Alt k"], editor.cursorLineDown)
    editor.addKeybinding(["edit"], ["Alt a"], editor.insertLineAbove)
    editor.addKeybinding(["edit"], ["Alt b"], editor.insertLineBelow)
    editor.addKeybinding(["edit", "findBuffer", "findFile"], ["Left", "Alt j"], editor.cursorCharacterLeft)
    editor.addKeybinding(["edit", "findBuffer", "findFile"], ["Right", "Alt l"], editor.cursorCharacterRight)
    editor.addKeybinding(["edit", "findBuffer", "findFile"], ["Alt s"], editor.cursorLineStart)
    editor.addKeybinding(["edit", "findBuffer", "findFile"], ["Alt e"], editor.cursorLineEnd)
    editor.addKeybinding(["edit", "findBuffer", "findFile"], ["Backspace"], editor.deleteCharacterLeft)
    editor.addKeybinding(["edit", "findBuffer", "findFile"], ["Delete", "Alt d"], editor.deleteCharacterRight)
    editor.addKeybinding(["edit", "findBuffer", "findFile"], ["Alt D"], editor.deleteLine)

    editor.addKeybinding(["findBuffer", "findFile"], ["Up", "Alt i"], editor.previousSearchResult)
    editor.addKeybinding(["findBuffer", "findFile"], ["Down", "Alt k"], editor.nextSearchResult)
    editor.addKeybinding(["findBuffer", "findFile"], ["Enter"], editor.chooseSearchResult)
    editor.addKeybinding(["findBuffer", "findFile"], ["Tab"], editor.copySearchResult)
    editor.addKeybinding(["findBuffer", "findFile"], ["Alt q"], editor.setMode("edit"))

    if len(sys.argv) > 1:
        editor.run(sys.argv[1:])
    else:
        editor.run()
"""
