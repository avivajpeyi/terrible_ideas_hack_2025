#!/bin/sh


#!/bin/bash

# Script to run in the first terminal
script1_path="/Users/avaj0001/Documents/personal/pygame_projects/ml_game_controller/RUN_CONTROLLER.sh"

# Script to run in the second terminal
script2_path="/Users/avaj0001/Documents/personal/pygame_projects/ml_game_controller/RUN_MAZE.sh.sh"

# Function to open a new Terminal window and run a script
run_in_new_terminal() {
  local script_path="$1"
  osascript -e 'tell application "Terminal" to do script "'"$script_path"'"' &
}

# Run the scripts in separate terminals
run_in_new_terminal "$script1_path"
run_in_new_terminal "$script2_path"

echo "Scripts launched in separate terminals."

#
#    /bin/sh -ec 'cd /Users/avaj0001/Documents/personal/pygame_projects/ml_game_controller && /Users/avaj0001/Documents/personal/pygame_projects/poseTetris/venv/bin/python pose_controller_v2.py &'
#    /bin/sh -ec 'cd /Users/avaj0001/Documents/personal/pygame_projects/ml_game_controller && /Users/avaj0001/Documents/personal/pygame_projects/poseTetris/venv/bin/python maze_game.py'