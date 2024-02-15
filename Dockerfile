FROM python:3.12-slim

ARG VERSION

RUN mkdir /house
COPY ./ /house/
RUN pip3 install -r /house/requirements.txt

ENV PYTHONPATH=/house

ENTRYPOINT ["python3", "/house/bin/server.py"]
CMD []
