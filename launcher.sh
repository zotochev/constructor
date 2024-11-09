#!/bin/bash

# Get the directory of the current script
script_directory="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
env_path="$script_directory/venv"
python_script="$script_directory/constructor/main.py"
requirements_file="$script_directory/requirements.txt"

# Check if the virtual environment folder exists
if [ ! -d "$env_path" ]; then
    echo "Virtual environment not found. Creating a new virtual environment in $script_directory..."
    python -m venv "$env_path"

    if [ $? -ne 0 ]; then
        echo "Failed to create the virtual environment."
        exit 1
    fi

    # Activate and install dependencies if requirements.txt exists
    echo "Activating the virtual environment and installing dependencies..."
    source "$env_path/bin/activate"
    if [ -f "$requirements_file" ]; then
        pip install -r "$requirements_file"
        if [ $? -ne 0 ]; then
            echo "Failed to install dependencies."
            exit 1
        fi
    else
        echo "No requirements.txt found. Skipping dependency installation."
    fi
else
    echo "Virtual environment found in $script_directory."
    source "$env_path/bin/activate"
fi

# Run the Python script
echo "Running the Python script..."
python3 "$python_script"

# Check the status after running the script
if [ $? -ne 0 ]; then
    echo "The Python script encountered an error."
else
    echo "Python script completed successfully."
fi
