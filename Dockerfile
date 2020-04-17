FROM ubuntu:latest

RUN apt-get update && \
  apt-get install -y software-properties-common && \
  add-apt-repository ppa:deadsnakes/ppa && \
  apt-get update -y && \
  apt-get install -y \
  build-essential \
  cmake \
  libopenblas-dev \
  liblapack-dev \
  python3.6 \
  python3.6-dev \
  python3-pip && \
  python3.6 -m pip install pip --upgrade && \
  python3.6 -m pip install wheel

RUN apt-get install -y libsm6 libxext6 libxrender-dev git

RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.19' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install

WORKDIR /app

COPY . /app

RUN python3.6 -m pip --no-cache-dir install -r requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python3" ]
CMD ["app.py"]