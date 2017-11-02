FROM python:3.6

WORKDIR /app

ADD . /app

EXPOSE 8989

ENV http_proxy http://www-proxy.scss.tcd.ie:8080/ 
ENV https_proxy https://www-proxy.scss.tcd.ie:8080/

CMD ["python", "-u", "server.py"]