FROM archlinux:base AS install-with-pip

ARG SOURCE=.

RUN pacman -Syu --noconfirm && \
    pacman -Sy --noconfirm fish python python-pip git

WORKDIR /workspace

COPY . .

SHELL ["/usr/bin/fish", "-c"]

RUN curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && \
    fisher install jorgebucaran/fisher

RUN fisher install $SOURCE

RUN fish_ai_bug_report

FROM archlinux:base AS install-with-uv

ARG SOURCE=.

RUN pacman -Syu --noconfirm && \
    pacman -Sy --noconfirm fish git

RUN pacman -Syu --noconfirm rust && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    . $HOME/.local/bin/env

WORKDIR /workspace

COPY . .

SHELL ["/usr/bin/fish", "-c"]

RUN curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && \
    fisher install jorgebucaran/fisher

RUN fisher install $SOURCE

RUN fish_ai_bug_report
