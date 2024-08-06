FROM locustio/locust
USER root

COPY requirements.txt /tmp/custom-requirements.txt

RUN pip3 install --upgrade -r /tmp/custom-requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com