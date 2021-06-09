FROM python:2.7
ENV PYTHONUNBUFFERED 1

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH
WORKDIR /tmp

RUN apt-get update --fix-missing && apt-get install -y wget bzip2 ca-certificates \
    libglib2.0-0 libxext6 libsm6 libxrender1 \
    git mercurial subversion gfortran r-base && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /code
WORKDIR /code

ADD . /code
# needs numpy first for whatever reason...
RUN pip install numpy cython
RUN pip install -r /code/requirements.txt


RUN chmod 775 utils/launch.sh
# uWSGI configuration (customize as needed):
# Start uWSGI
CMD ["utils/launch.sh"]
