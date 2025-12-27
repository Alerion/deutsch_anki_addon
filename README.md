# Mark Deutch with colors

## Hotkeys

- ``F1`` - generate Anki card for copied word. Use ``F12`` in Edit card window.
- ``F2`` - color translation and makes text bold.
- ``F3`` - insert "der".
- ``F4`` - insert "die".
- ``F5`` - insert "das".
- ``F6`` - insert "NOUN".
- ``F7`` - insert "VERB".
- ``F8`` - insert "ADJECTIVE".
- ``F9`` - insert "ADVERB".
- ``F10`` - insert "PRONOUN".

## Install

Run anki in console:

    cd "C:/Users/user/AppData/Local/Programs/Anki"
    export QTWEBENGINE_REMOTE_DEBUGGING=8080
    ./anki-console.bat

Create symlink to addons folder:

    mklink /D C:\Users\user\AppData\Roaming\Anki2\addons21\quickcolor <path to project>\anki-quick-color-addon\addon\

Install dependencies:

    source ./venv/Scripts/activate
    poetry install

Install dependencies into addon folder

    poetry export --only addon -f requirements.txt --output requirements.txt
    pip install -r requirements.txt -t ./addon/dependencies
