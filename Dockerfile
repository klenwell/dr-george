FROM python:3.9-alpine
LABEL MAINTAINER="Tom Atwell <klenwell@gmail.com>"
ENV PS1="\[\e[0;33m\]|> dr_george <| \[\e[1;35m\]\W\[\e[0m\] \[\e[0m\]# "

WORKDIR /src
COPY . /src
RUN pip install --no-cache-dir -r requirements.txt \
    && python setup.py install
WORKDIR /
ENTRYPOINT ["dr_george"]
