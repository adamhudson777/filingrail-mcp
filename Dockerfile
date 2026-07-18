# syntax=docker/dockerfile:1

# filingrail-mcp — MCP server for the Filingrail SEC EDGAR API (stdio transport).
#
#   Build:  docker build -t filingrail-mcp .
#   Run:    docker run --rm -i -e RAPIDAPI_KEY=your-key filingrail-mcp
#
# The server speaks MCP over stdio (no ports). The end user brings their own
# RapidAPI key — free tier is 50 calls/day, no card:
#   https://rapidapi.com/hudson-enterprises-llc-hudson-enterprises-llc-default/api/filingrail

FROM python:3.12-slim

LABEL org.opencontainers.image.title="filingrail-mcp" \
      org.opencontainers.image.description="MCP server exposing the Filingrail SEC EDGAR API (financials, insider trades, 8-K events, 13F holdings) as stdio tools." \
      org.opencontainers.image.source="https://github.com/adamhudson777/filingrail-mcp" \
      org.opencontainers.image.licenses="MIT"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Copy build metadata + source, then install (pulls filingrail + mcp from PyPI).
# README.md is required at build time (pyproject reads it as the long description).
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir .

# Drop privileges — the console script installs to a system path still on PATH.
RUN useradd --create-home --uid 10001 appuser
USER appuser

# RAPIDAPI_KEY is supplied at runtime by the MCP client. No ports are exposed.
ENTRYPOINT ["python", "-m", "filingrail_mcp"]
