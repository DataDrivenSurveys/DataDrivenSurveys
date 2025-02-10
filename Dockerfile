# Use AMD64 platform explicitly
FROM --platform=linux/amd64 ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN echo "Docker build is running......"

# Remove the direct BLIS installation since it will be handled by uv sync
# RUN pip install --no-cache-dir blis==1.2.0  # Remove this line

# Install Rust
RUN apt-get update && apt-get install -y curl && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> /root/.bashrc && \
    echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> /root/.profile && \
    export PATH="$HOME/.cargo/bin:$PATH" && \
    rustc --version

ENV PATH="/root/.cargo/bin:$PATH"

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Add project files
ADD pyproject.toml uv.lock LICENSE README.md ./
ADD ddsurveys/ ddsurveys/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"
ENTRYPOINT []
ENTRYPOINT ["sh", "/app/ddsurveys/entrypoint.sh"]
CMD ["gunicorn", "ddsurveys.wsgi:app", "--bind", "0.0.0.0:4000", "--reload"]