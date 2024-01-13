FROM purefish/docker-fish

USER 0:0

RUN apk add python3 py3-pip
RUN pip install --break-system-packages openai

USER nemo
WORKDIR /home/nemo

COPY test/fish-ai.ini .config
COPY . .

SHELL ["/usr/bin/fish", "-c"]

RUN fisher install .

RUN fishtape test/tapes/codify.fish
RUN fishtape test/tapes/explain.fish
RUN fishtape test/tapes/autocomplete.fish
RUN fishtape test/tapes/fix.fish