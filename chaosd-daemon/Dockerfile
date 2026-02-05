FROM golang:1.21-bullseye AS builder

WORKDIR /workspace

# Install dependencies
RUN apt-get update && apt-get install -y git make && rm -rf /var/lib/apt/lists/*

# Clone Chaosd (latest version)
RUN git clone --depth 1 https://github.com/chaos-mesh/chaosd.git .

# Build Chaosd
RUN make chaosd

FROM debian:bullseye-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the binary from builder
COPY --from=builder /workspace/bin/chaosd /usr/local/bin/chaosd

# Create data directory
RUN mkdir -p /var/lib/chaosd

EXPOSE 31767

CMD ["chaosd", "server", "--port", "31767"]
