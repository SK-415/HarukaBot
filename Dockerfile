FROM mcr.microsoft.com/playwright
LABEL maintainer="https://github.com/SK-415/HarukaBot"
RUN pip install haruka-bot -i https://mirrors.aliyun.com/pypi/simple/
ENV TZ=Asia/Shanghai LANG=zh_CN.UTF-8 HARUKA_DIR=/data HOST=0.0.0.0 COMMAND_START=""
VOLUME /data
CMD ["hb" ,"run"]
