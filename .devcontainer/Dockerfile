FROM albx79/what-bump:1.2.0 as what-bump

FROM mcr.microsoft.com/devcontainers/python

RUN pip3 install --break-system-packages \
        pre-commit openai google-generativeai simple-term-menu

COPY --from=what-bump /what-bump /bin/what-bump
