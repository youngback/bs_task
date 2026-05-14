
import json
import os
from psychopy import visual, core, event

def attention_check(win):

    text = visual.TextStim(
        win,
        text="중간 확인\n\n계속하기위해 엔터키를 눌러주세요",
        height=40,
        color="white"
    )

    while True:
        text.draw()
        win.flip()

        keys = event.getKeys()

        if "return" in keys:   # Enter key
            break