#!/bin/bash

# This script is designed to help when skimming multiple datasets with grid-control.
# Running it will create a screen session and run grid-control in a separate tab
# within the screen session for each skimming config present in the current directory.
# Files ending in "_gc.conf" are assumed to be skimming configs, as long as the
# filename does not contain the substring "base".

# create the session name from the current directory name
SESSION="XkappaSkim_$(pwd | rev | cut -d"/" -f1,2 | rev | tr \"/\" \"_\")"

screen -list | grep -q "$SESSION" && echo "Failed: session named '$SESSION' already exists.\n\nTo reattach, run: screen -r $SESSION"

# open a new named screen session (collection of "tabs") in the background
screen -dmS "$SESSION"

echo "New screen session created: $SESSION"

# create multiple "tabs" in the screen session (one for each grid-control config)
for skimConfig in *_gc.conf; do
    if echo "$skimConfig" | grep -q "base"; then
        # some configs are only meant to be included in others
        echo "Skipping config '$skimConfig' because file contains 'base'..."
    else
        # in every tab, source the user's bashrc, the scram environment and run grid-control with the respective skim config
        screen -S "$SESSION" -X screen bash -c "exec bash --init-file <(echo \"source \"$HOME/.bashrc\"; export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch; source $VO_CMS_SW_DIR/cmsset_default.sh; eval \\\`scramv1 runtime -sh\\\`; echo go.py $skimConfig\")"
        echo "Opened grid-control with config '$skimConfig' in new screen tab in session '$SESSION'"
    fi
done

# close the first "tab", which is just an empty shell session
screen -S "$SESSION" -p 0 -X stuff $'exit\n'

# attach to the screen session (showing the "tab" overview with '-p =')
screen -r "$SESSION" -p =

