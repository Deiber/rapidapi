FROM python:3.7
USER root
ENV PYTHONUNBUFFERED 1
RUN mkdir /src
WORKDIR /src
COPY . /src
RUN chmod 777 /src
RUN pip install -r deploy/requirements.txt
