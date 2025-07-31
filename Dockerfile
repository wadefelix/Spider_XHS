FROM registry.home.renwei.net:5000/python:3.11-slim-bookworm

WORKDIR /app
RUN sed -i "s#deb.debian.org#mirrors.tuna.tsinghua.edu.cn#g" /etc/apt/sources.list.d/debian.sources \
 && sed -i "s#security.debian.org#mirrors.tuna.tsinghua.edu.cn#g" /etc/apt/sources.list.d/debian.sources

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

COPY package.json .
COPY package-lock.json .

RUN apt-get update \
 && apt-get install -yq --no-install-recommends \
    vim \
    curl \
 && curl -sL https://deb.nodesource.com/setup_20.x | bash - \
 && apt-get install -yq --no-install-recommends \
    nodejs \
 && npm install \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN python --version && node --version && npm --version


EXPOSE 5000

ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

COPY . .
# docker build -t spider_xhs .
# docker run -it spider_xhs bash
EXPOSE 8000
CMD ["python", "server.py"] 
