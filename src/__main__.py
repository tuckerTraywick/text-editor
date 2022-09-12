#!/usr/bin/env python3
import sys
from editor import Editor


if __name__ == "__main__":
    editor = Editor()

    editor.setSettings({
        "showLineNumbers": True,
        "relativeLineNumbers": False,
        "showStatusLine": False,
    })

    editor.setColors({
        "lineNumber": editor.terminal.gray50,
    })

    leader = "Space"
    editor.addKeybinding("all", ["Ctrl q", f"Alt {leader} q"], editor.quit)
    editor.addKeybinding("all", ["Ctrl e", f"Alt {leader} e"], editor.exit)
    editor.addKeybinding("all", ["Ctrl b", f"Alt {leader} b"], editor.setMode("findBuffer"))

    editor.addKeybinding(["edit"], ["Printable", "Space"], editor.insertCharacter)
    editor.addKeybinding(["edit"], ["Up", "Alt i"], editor.cursorLineUp)
    editor.addKeybinding(["edit"], ["Down", "Alt k"], editor.cursorLineDown)
    editor.addKeybinding(["edit"], ["Left", "Alt j"], editor.cursorCharacterLeft)
    editor.addKeybinding(["edit"], ["Right", "Alt l"], editor.cursorCharacterRight)

    editor.addKeybinding(["findBuffer"], ["Down", "Alt k"], editor.bufferForward)
    editor.addKeybinding(["findBuffer"], ["Up", "Alt i"], editor.bufferBackward)
    editor.addKeybinding(["findBuffer"], ["Enter"], editor.setMode("edit"))

    if len(sys.argv) > 1:
        editor.run(sys.argv[1:])
    else:
        editor.run()
