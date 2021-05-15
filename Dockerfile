FROM ubuntu:20.04

# python
RUN apt-get update -y && apt-get install -y --install-recommends \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# npm
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    nodejs npm \
    && rm -rf /var/lib/apt/lists/*

# sudo
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    sudo \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m diavlos && echo "diavlos:diavlos" | chpasswd && adduser diavlos sudo

# copy on folder
COPY . /diavlos/
RUN chown -R diavlos:diavlos /diavlos/
WORKDIR /diavlos/

# install
RUN sudo ./make

WORKDIR /diavlos/scripts/

EXPOSE 5000

CMD ["./serve_api.sh","--generate-new-schemas"]
