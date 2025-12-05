FROM fedora:43 AS install-with-pip

ARG SOURCE=.

RUN dnf -y install fish python pip git

WORKDIR /workspace

COPY . .

SHELL ["/usr/bin/fish", "-c"]

RUN curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && \
    fisher install jorgebucaran/fisher

RUN fisher install $SOURCE

RUN fish_ai_bug_report

FROM fedora:43 AS install-with-uv

ARG SOURCE=.

RUN dnf -y install fish git

RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    . $HOME/.local/bin/env

WORKDIR /workspace

COPY . .

SHELL ["/usr/bin/fish", "-c"]

RUN curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && \
    fisher install jorgebucaran/fisher

RUN fisher install $SOURCE

RUN fish_ai_bug_report
