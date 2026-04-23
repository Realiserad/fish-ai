FROM albx79/what-bump:1.2.0 as what-bump
FROM mikefarah/yq:4.53.2 as yq

FROM mcr.microsoft.com/devcontainers/python:3.11-buster

WORKDIR /home/vscode

COPY requirements-dev.txt .

RUN pip3 install \
    --no-cache-dir \
    --break-system-packages \
    -r requirements-dev.txt

COPY --from=what-bump /what-bump /bin/what-bump
COPY --from=yq /usr/bin/yq /bin/yq
