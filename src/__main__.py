#!/usr/bin/env python3
import sys
from editor import Editor


if __name__ == "__main__":
    editor = Editor()

    editor.setSettings({
        "showLineNumbers": True,
        "relativeLineNumbers": False,
        "showStatusLine": True,
    })

    editor.setColors({
        "lineNumber": editor.terminal.gray40,
        "emptyLineFill": editor.terminal.gray40,
        "currentLine": editor.terminal.on_gray17,
        "currentSelection": editor.terminal.normal,
        "statusLine": editor.terminal.on_gray22,
        "inactiveCursor": editor.terminal.on_slategray,
    })

    leader = "Space"
    editor.addKeybinding("all", ["Ctrl q", f"Alt {leader} q"], editor.quit)
    editor.addKeybinding("all", ["Ctrl e", f"Alt {leader} e"], editor.exit)
    editor.addKeybinding(["edit"], ["Ctrl s", f"Alt {leader} s"], editor.saveBuffer)
    editor.addKeybinding(["edit"], ["Ctrl a", f"Alt {leader} a"], editor.saveAllBuffers)
    editor.addKeybinding(["edit"], ["Ctrl c", f"Alt {leader} c"], editor.closeBuffer)
    editor.addKeybinding(["edit"], ["Ctrl x", f"Alt {leader} x"], editor.killBuffer)
    editor.addKeybinding("!findBuffer", ["Ctrl b", f"Alt {leader} b"], editor.setMode("findBuffer"))

    editor.addKeybinding(["edit"], ["Printable", "Space"], editor.insertCharacter)
    editor.addKeybinding(["edit"], ["Up", "Alt i"], editor.cursorLineUp)
    editor.addKeybinding(["edit"], ["Down", "Alt k"], editor.cursorLineDown)
    editor.addKeybinding(["edit"], ["Alt a"], editor.insertLineAbove)
    editor.addKeybinding(["edit"], ["Alt b"], editor.insertLineBelow)
    editor.addKeybinding(["edit", "findBuffer"], ["Left", "Alt j"], editor.cursorCharacterLeft)
    editor.addKeybinding(["edit", "findBuffer"], ["Right", "Alt l"], editor.cursorCharacterRight)
    editor.addKeybinding(["edit", "findBuffer"], ["Alt s"], editor.cursorLineStart)
    editor.addKeybinding(["edit", "findBuffer"], ["Alt e"], editor.cursorLineEnd)
    editor.addKeybinding(["edit", "findBuffer"], ["Backspace"], editor.deleteCharacterLeft)
    editor.addKeybinding(["edit", "findBuffer"], ["Delete", "Alt d"], editor.deleteCharacterRight)
    editor.addKeybinding(["edit", "findBuffer"], ["Alt D"], editor.deleteLine)

    editor.addKeybinding(["findBuffer"], ["Printable", "Space"], editor.insertCharacter)
    editor.addKeybinding(["findBuffer"], ["Up", "Alt i"], editor.bufferBackward)
    editor.addKeybinding(["findBuffer"], ["Down", "Alt k"], editor.bufferForward)
    editor.addKeybinding(["findBuffer"], ["Enter"], editor.chooseBuffer)
    editor.addKeybinding(["findBuffer"], ["Alt q"], editor.cancelBufferSearch)

    if len(sys.argv) > 1:
        editor.run(sys.argv[1:])
    else:
        editor.run()
