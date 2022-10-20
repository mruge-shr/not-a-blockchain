FROM python:3

ADD requirements.txt /
RUN pip install -r /requirements.txt

COPY not_a_blockchain/ /not_a_blockchain/
RUN pip install /not_a_blockchain/

ADD app.py /

CMD ["python3","/app.py"]