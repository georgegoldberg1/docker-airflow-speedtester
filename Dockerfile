FROM apache/airflow:2.1.2
USER root
RUN curl -s https://install.speedtest.net/app/cli/install.deb.sh | bash \
    && apt-get update \
    && apt-get install \
        speedtest
USER airflow
