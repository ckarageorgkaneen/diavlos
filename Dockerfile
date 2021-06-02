FROM python:3.6-buster

ENV NODE_VERSION 14

RUN \
  echo "deb https://deb.nodesource.com/node_${NODE_VERSION}.x buster main" > /etc/apt/sources.list.d/nodesource.list && \
  wget -qO- https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - && \
  echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list && \
  wget -qO- https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
  apt-get update && \
  apt-get install -yqq nodejs yarn && \
  pip install -U pip && pip install pipenv && \
  npm i -g npm@^6 && \
  npm install -g @apidevtools/swagger-cli && \
  rm -rf /var/lib/apt/lists/*

RUN useradd -m diavlos && echo "diavlos:diavlos" | chpasswd && adduser diavlos sudo
COPY . /app/
RUN chown -R diavlos:diavlos /app/
WORKDIR /app/
RUN pip install -e . 

WORKDIR /app/scripts
EXPOSE 5000

ENV PYTHONPATH "${PYTHONPATH}:/app"

CMD ["sh", "serve_api.sh", "--generate-new-schemas"]

