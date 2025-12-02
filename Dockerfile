# ────────────── Base Image ──────────────
FROM python:3.12-slim

# ────────────── Create non-root user ──────────────
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && apt-get update && apt-get install -y --no-install-recommends \
    sudo \
    build-essential \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && rm -rf /var/lib/apt/lists/*

# ────────────── Environment Setup ──────────────
WORKDIR /workspace

# Copy project files
COPY pyproject.toml .
COPY source ./source
COPY tests ./tests
COPY README.md .

# Build args to differentiate environment
ARG ENV=dev
ENV ENV=${ENV}

# ────────────── Install dependencies ──────────────
# If ENV is production, install only main; otherwise, include dev dependencies
RUN pip install --upgrade pip \
    && if [ "$ENV" = "production" ]; then \
         pip install . ; \
       else \
         pip install ".[dev]" ; \
       fi

# ────────────── Set ownership ──────────────
RUN chown -R $USERNAME:$USERNAME /workspace

# ────────────── Switch to non-root user ──────────────
USER $USERNAME

# ────────────── Default command ──────────────
CMD ["python", "-m", "source.__main__"]