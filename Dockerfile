FROM python:3.12
WORKDIR /parser
COPY ./* /parser
RUN pip install -r requirements.txt
CMD python3 main.py
