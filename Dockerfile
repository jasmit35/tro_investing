##===============================================================================
##  Build a TRO investing image using uv 
##===============================================================================

##-------------------------------------------------------------------------------
##  Prep an OS
##-------------------------------------------------------------------------------

FROM python:3.13-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml README.md ./
RUN uv sync

##  Add additional software and upgrade all to current
RUN apt-get update && \
    apt-get install -y openssl && \
    apt-get install -y iproute2 && \
    apt-get -y upgrade && \
    rm -rf /var/lib/apt/lists/*


##-------------------------------------------------------------------------------
##  Build out the image
##-------------------------------------------------------------------------------

FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

##  Varables used for the build only
ARG APP_NAME="tro_investing"
ARG APP_HOME="/opt/app/${APP_NAME}"

##  Set the timezone
RUN ln -sf /usr/share/zoneinfo/America/Chicago /etc/localtime && \
    echo "America/Chicago" > /etc/timezone

##  Get the application code set up
WORKDIR ${APP_HOME}
COPY --from=builder /app .
COPY src/tro_investing . 

##  Application userid
RUN groupadd -g 20000 appgroup && \
    useradd -u 20001 -g appgroup -m -s /bin/bash appowner

RUN chown -R appowner:appgroup . 

##-------------------------------------------------------------------------------
##  Do it...
##-------------------------------------------------------------------------------

USER appowner
ENV ENVIRONMENT="test"
ENV PATH="${APP_HOME}/.venv/bin:${PATH}"
ENV PYTHONPATH="${APP_HOME}"
ENTRYPOINT [ "uv", "run", "python/main.py"]
#  CMD ["sleep", "3600"]

