FROM ubuntu:24.04 AS install-with-pip

ARG SOURCE=.

RUN apt update && \
    apt install -y curl git software-properties-common

RUN apt install -y python3 python3-pip python3-venv

RUN apt-add-repository ppa:fish-shell/release-3 && \
    apt update && \
    apt install -y fish

WORKDIR /workspace

COPY . .

SHELL ["/usr/bin/fish", "-c"]

RUN curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && \
    fisher install jorgebucaran/fisher

RUN fisher install $SOURCE

RUN fish_ai_bug_report

FROM ubuntu:24.04 AS install-with-uv

ARG SOURCE=.

RUN apt update && \
    apt install -y curl git software-properties-common

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    . $HOME/.local/bin/env

RUN apt-add-repository ppa:fish-shell/release-3 && \
    apt update && \
    apt install -y fish

WORKDIR /workspace

COPY . .

SHELL ["/usr/bin/fish", "-c"]

RUN curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && \
    fisher install jorgebucaran/fisher

RUN fisher install $SOURCE

RUN fish_ai_bug_report
