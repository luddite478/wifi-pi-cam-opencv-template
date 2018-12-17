#!/bin/bash

# 1. create named pipe

if [ -p fifo264 ]
then
        rm fifo264
fi
mkfifo fifo264

# 2. redirect data from port to pipe

nc -l -v -p 5777 > fifo264 &

# 3. run script which reads pipe

python main.py &

# 4. start camera remotely on pi using pass file with password

sshpass -f pass ssh -o StrictHostKeychecking=no pi@192.168.0.104 "cd scripts && ./3-stream.sh"
