  
FROM python:3.4

WORKDIR /project

ADD . /project

RUN pip install -r Requirements.txt

CMD ["/bin/bash", "-c", "sleep 120 && python3 mqttPublishF.py"]