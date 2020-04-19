# GazeTracking

Samsung Labs Gaze Tracking Application
Backend for the focus calculation android app.

## Getting Started

You need to first install CMAKE to your system before installing the python dependencies.

- MacOS

  ```bash
  brew install cmake
  ```

- Linux

  ```bash
  sudo apt-get install build-essential cmake
  sudo apt-get install libopenblas-dev liblapack-dev
  ```

### Installling Python Dependencies

Recommended: Create a python virtual env for the project before proceeding with the following steps

```bash
pip install requirements.txt
```

### Starting the server

```bash
python app.py
```

Your server should now start running on `http://127.0.0.1:8080/`
