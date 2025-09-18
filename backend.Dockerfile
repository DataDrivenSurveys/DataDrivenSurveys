# This Dockerfile builds the backend

FROM ghcr.io/astral-sh/uv:python3.12-bookworm

# Install dos2unix
RUN apt-get update && apt-get install -y dos2unix

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
  --mount=type=bind,source=uv.lock,target=uv.lock \
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  uv sync --frozen --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD pyproject.toml uv.lock LICENSE README.md ./
ADD ddsurveys/ /app/ddsurveys/
RUN --mount=type=cache,target=/root/.cache/uv \
  uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Ensure entrypiont can be run
RUN dos2unix /app/ddsurveys/entrypoint.sh && chmod +x /app/ddsurveys/entrypoint.sh


# Set the entry point script
ENTRYPOINT ["sh", "/app/ddsurveys/entrypoint.sh"]


# Default command runs Gunicorn
CMD ["gunicorn", "ddsurveys.wsgi:app", "--bind", "0.0.0.0:4000", "--reload"]
