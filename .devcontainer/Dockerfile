FROM albx79/what-bump:1.2.0 as what-bump

FROM mcr.microsoft.com/devcontainers/python

COPY requirements-dev.txt .

RUN pip3 install --break-system-packages -r requirements-dev.txt

COPY --from=what-bump /what-bump /bin/what-bump
