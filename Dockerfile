FROM purefish/docker-fish

USER 0:0

RUN apk add python3 py3-pip
RUN pip install --break-system-packages openai

USER nemo
WORKDIR /home/nemo

COPY test/config.ini .config/fish-ai.ini
COPY . .

SHELL ["/usr/bin/fish", "-c"]
RUN fisher install .
RUN fishtape test/tape.fish