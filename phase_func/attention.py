import json
import os
from psychopy import visual, core, event

def attention_check(win):

    text = visual.TextStim(
        win,
        text="Attention check\n\nPress ENTER to continue",
        height=40,
        color="white"
    )

    while True:
        text.draw()
        win.flip()

        keys = event.getKeys()

        if "return" in keys:   # Enter key
            break