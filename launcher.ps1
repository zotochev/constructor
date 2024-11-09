# Get the directory of the current PowerShell script
$scriptDirectory = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent
$envPath = "$scriptDirectory\venv"
$pythonScript = "$scriptDirectory\constructor\main.py"
$requirementsFile = "$scriptDirectory\requirements.txt"

# Check if the virtual environment folder exists
if (-Not (Test-Path $envPath)) {
    Write-Host "Virtual environment not found. Creating a new virtual environment in $scriptDirectory..."
    try {
        python -m venv $envPath
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create the virtual environment."
        }
    } catch {
        Write-Error "Error: $($_.Exception.Message)"
        exit 1
    }

    # Activate and install dependencies if requirements.txt exists
    Write-Host "Activating the virtual environment and installing dependencies..."
    & "$envPath\Scripts\Activate.ps1"
    if (Test-Path $requirementsFile) {
        pip install --upgrade pip
        pip install -r $requirementsFile
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Failed to install dependencies."
            exit 1
        }
    } else {
        Write-Host "No requirements.txt found. Skipping dependency installation."
    }
} else {
    Write-Host "Virtual environment found in $scriptDirectory."
    & "$envPath\Scripts\Activate.ps1"
}

# Run the Python script
Write-Host "Running the Python script..."
python $pythonScript

# Check the status after running the script
if ($LASTEXITCODE -ne 0) {
    Write-Error "The Python script encountered an error."
} else {
    Write-Host "Python script completed successfully."
}
