FROM python:3.6.1

RUN apt-get update
RUN apt-get -y install wget \
    cmake \
    gcc \
    git

RUN wget https://github.com/libgit2/libgit2/archive/v0.26.0.tar.gz && \
tar xzf v0.26.0.tar.gz && \
cd libgit2-0.26.0/ && \
cmake . && \
make && \
make install

RUN ldconfig

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements (to leverage Docker cache)
ADD ./requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip install -r requirements.txt

# add app
ADD . /usr/src/app

# run worker
CMD python worker.py