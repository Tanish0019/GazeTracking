# GazeTracking

Samsung Labs Gaze Tracking Application
Backend for the focus calculation android app.

## Getting Started
This application uses Dlib. You need to install some system level dependencies to use dlib before running the application.
- Windows

  You can follow this [tutorial](https://www.youtube.com/watch?v=HqjcqpCNiZg) to see instructions on getting Dlib on windows.

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
pip install -r requirements.txt
```

### Starting the server

```bash
python app.py
```

Your server should now start running on `http://0.0.0.0:8080/`


## Deploying to Google Cloud App Engine
1. Download the [gcloud sdk](https://cloud.google.com/sdk/docs/downloads-versioned-archives#installation_instructions)

2. `gcloud init`

3. If you're deploying the app for the first time you need to increase the default build timeout - `gcloud config set app/cloud_build_timeout 1500`

4. `gcloud app deploy`
