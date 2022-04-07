FROM mcr.microsoft.com/playwright
LABEL maintainer="https://github.com/SK-415/HarukaBot"
RUN sed -i s@/archive.ubuntu.com/@/mirrors.aliyun.com/@g /etc/apt/sources.list && apt update && pip install haruka-bot -i https://mirrors.aliyun.com/pypi/simple/
EXPOSE 8080
WORKDIR /data
COPY .env.prod /data/.env.prod
ENV TZ=Asia/Shanghai LANG=zh_CN.UTF-8 HOST=0.0.0.0
CMD ["hb" ,"run"]
