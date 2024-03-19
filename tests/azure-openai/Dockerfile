FROM purefish/docker-fish

USER 0

RUN apk add python3 py3-pip
RUN pip install --break-system-packages openai

USER nemo

WORKDIR /home/nemo

COPY tests/azure-openai/fish-ai.ini .config
COPY . .

SHELL ["/usr/bin/fish", "-c"]

RUN fisher install .

RUN fishtape tests/azure-openai/tapes/codify.fish
RUN fishtape tests/azure-openai/tapes/explain.fish
RUN fishtape tests/azure-openai/tapes/autocomplete.fish
RUN fishtape tests/azure-openai/tapes/fix.fish
