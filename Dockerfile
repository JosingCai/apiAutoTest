FROM centos
COPY . /home
RUN yum -y install net-tools && \
    yum -y install epel-release && \
    yum -y install python36 && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    pip3 install gunicorn gevent && \
    pip3 install selenium && \
    pip3 install bs4 && \
    pip3 install -r /home/tools/requirements.txt
WORKDIR /home
CMD ["gunicorn", "app:app", "-c", "./gunicorn.conf.py"]