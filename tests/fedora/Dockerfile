FROM fedora:40

ARG SOURCE=.

RUN dnf -y install fish python pip git

WORKDIR /workspace

COPY . .

SHELL ["/usr/bin/fish", "-c"]

RUN curl -sL https://raw.githubusercontent.com/jorgebucaran/fisher/main/functions/fisher.fish | source && \
    fisher install jorgebucaran/fisher

RUN fisher install $SOURCE

RUN fish_ai_bug_report
