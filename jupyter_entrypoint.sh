#!/bin/bash

# Check if the password environment variable is set
if [ -z "$JUPYTER_PASSWORD" ]; then
    echo "No password provided, check docker logs to obtain the auth token."
else
    # Generate the hashed password and update the Jupyter config
    hashed_password=$(python -c "from jupyter_server.auth import passwd; print(passwd('$JUPYTER_PASSWORD'))")
    mkdir -p  ~/.jupyter
    echo "{\"IdentityProvider\": {\"hashed_password\": \"$hashed_password\"}}" > ~/.jupyter/jupyter_server_config.json
    echo "Jupyter password is set."
fi

# Source ROS environment 
source /rbs_ws/devel/setup.bash

if [ -z "$NOTEBOOK_ROOT_DIR" ]; then 
    export DIR=/rbs_ws/src
else
    export DIR=$NOTEBOOK_ROOT_DIR
fi

# if ADDITIONAL_COMMAND=0 then any input here is passed as argv for jupyter
# if ADDITIONAL_COMMAND=1 then jupyter runs in the background and an additional command can be started

# Default ADDITIONAL_COMMAND to 0 if it's not set or empty
: "${ADDITIONAL_COMMAND:=0}"


if [ "$ADDITIONAL_COMMAND" -eq 1 ]; then
    # Run jupyter in background
    nohup jupyter-lab --collaborative --allow-root --NotebookApp.ip='0.0.0.0' --NotebookApp.port=8888 --no-browser --notebook-dir $DIR &
    
    # Execute other commands
    exec "$@"
else 
    jupyter-lab --collaborative --allow-root --NotebookApp.ip='0.0.0.0' --NotebookApp.port=8888 --no-browser --notebook-dir $DIR "$@"
fi
