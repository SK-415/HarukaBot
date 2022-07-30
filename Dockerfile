FROM mcr.microsoft.com/playwright/python:v1.22.0-focal

LABEL maintainer="https://github.com/SK-415/HarukaBot"

EXPOSE 8080

RUN pip install haruka-bot -i https://mirrors.aliyun.com/pypi/simple/

WORKDIR /haruka_bot

COPY .env.prod /haruka_bot/.env.prod

ENV TZ=Asia/Shanghai LANG=zh_CN.UTF-8 HOST=0.0.0.0

CMD ["hb" ,"run"]