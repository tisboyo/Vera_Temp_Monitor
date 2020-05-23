FROM python:3

USER root

WORKDIR /usr/src/app

ENV db_user mqtt_py
ENV db_password password
ENV database mqtt
ENV db_host 192.168.2.240
ENV db_port 5432
ENV machine=192.168.1.x
ENV machine_user=root
ENV machine_password=

RUN git clone https://github.com/tisboyo/Vera_Temp_Monitor.git && chmod +x ./Vera_Temp_Monitor/init.sh

ENTRYPOINT ["/usr/src/app/Vera_Temp_Monitor/init.sh"]
