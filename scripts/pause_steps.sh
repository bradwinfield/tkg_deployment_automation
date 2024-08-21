#!/usr/bin/env bash

# Pauses the deployment and waits for <RETURN>
echo $*
echo ">>>>>>> Deployment Paused. See instructions above. Enter "y" then ENTER/RETURN to unpause. <<<<<<<"
while true; do
    read ANS
    if [[ $ANS == "y" ]]; then
        echo "Deployment proceeding."
        exit 0
    fi
done

