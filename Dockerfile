FROM ubuntu:latest
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y python3 python3-pip

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

ENTRYPOINT [ "python3" ]

CMD [ "app.py" ]