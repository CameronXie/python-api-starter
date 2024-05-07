FROM cameronx/aws-deployer:latest

RUN set -eux \
    && apt-get update && apt-get install -y --no-install-recommends \
      apt-transport-https \
      ca-certificates \
      curl \
      gnupg \
      jq \
      less \
      lsb-release \
      make \
      shellcheck \
      tree \
      vim \
      zip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG CFNLINT_VERSION=0.86.4
ARG POETRY_VERSION=1.8.2
ARG ACTIONLINT_VERSION=1.6.27
WORKDIR /tmp/build
RUN pip install cfn-lint==${CFNLINT_VERSION} poetry==${POETRY_VERSION} uvicorn \
    # install actionlint
    && wget -q -O actionlint.tar.gz https://github.com/rhysd/actionlint/releases/download/v${ACTIONLINT_VERSION}/actionlint_${ACTIONLINT_VERSION}_linux_amd64.tar.gz \
    && tar -xzf actionlint.tar.gz \
    && mv actionlint /usr/local/bin

# TODO: Remove this once IntelliJ supports refresh Python packages in container.
COPY pyproject.toml poetry.lock /tmp/build/
RUN poetry export --without-hashes --format=requirements.txt | pip install -r /dev/stdin \
    && rm -rf /tmp/build
