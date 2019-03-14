# using 3.6 because of lxml
FROM    python:3-alpine3.9

WORKDIR /app
COPY    requirememts.txt /app/

# need to install a compiler and libraries for lxml :-/
RUN     apk add g++ libxml2-dev libxslt-dev \
          && pip install -r requirememts.txt
COPY    . /app/

ENTRYPOINT ["python", "/app/consumer.py"]
