FROM purefish/docker-fish:3.7.0

USER 0

RUN apk add python3 py3-pip

USER nemo

WORKDIR /home/nemo

COPY tests/azure-openai/fish-ai.ini .config
COPY . .

SHELL ["/usr/bin/fish", "-c"]

RUN fisher install .

RUN fishtape tests/azure-openai/tape.fish
