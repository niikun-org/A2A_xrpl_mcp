# HuggingFace Spaces Dockerfile for A2A MCP Demo with IPFS support
# This enables full IPFS + XRPL anchoring functionality on Spaces

FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    tar \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install IPFS (Kubo)
ENV IPFS_VERSION=v0.24.0
RUN wget https://dist.ipfs.tech/kubo/${IPFS_VERSION}/kubo_${IPFS_VERSION}_linux-amd64.tar.gz && \
    tar -xvzf kubo_${IPFS_VERSION}_linux-amd64.tar.gz && \
    cd kubo && \
    bash install.sh && \
    cd .. && \
    rm -rf kubo kubo_${IPFS_VERSION}_linux-amd64.tar.gz

# Initialize IPFS repository
RUN ipfs init

# Configure IPFS for local use (disable external connections for security)
RUN ipfs config Addresses.API /ip4/127.0.0.1/tcp/5001 && \
    ipfs config Addresses.Gateway /ip4/127.0.0.1/tcp/8080 && \
    ipfs config --json API.HTTPHeaders.Access-Control-Allow-Origin '["*"]' && \
    ipfs config --json API.HTTPHeaders.Access-Control-Allow-Methods '["GET", "POST"]'

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create necessary directories
RUN mkdir -p logs traces

# Expose ports
# 7860: Gradio UI (HuggingFace Spaces default)
# 5001: IPFS API (internal only)
# 8080: IPFS Gateway (internal only)
# 8000: MCP Server (internal only)
EXPOSE 7860

# Create startup script
RUN echo '#!/bin/bash\n\
echo "======================================================="\n\
echo "🚀 A2A MCP Demo with IPFS - Starting..."\n\
echo "======================================================="\n\
\n\
# Start IPFS daemon in background\n\
echo "📦 Starting IPFS daemon..."\n\
ipfs daemon &\n\
IPFS_PID=$!\n\
\n\
# Wait for IPFS to be ready\n\
echo "⏳ Waiting for IPFS to start..."\n\
for i in {1..30}; do\n\
  if curl -s http://127.0.0.1:5001/api/v0/version > /dev/null 2>&1; then\n\
    echo "✅ IPFS is ready"\n\
    break\n\
  fi\n\
  sleep 1\n\
done\n\
\n\
# Start MCP server in background\n\
echo "📡 Starting MCP server..."\n\
python -m mcp.mcp_server &\n\
MCP_PID=$!\n\
\n\
# Wait for MCP server\n\
sleep 3\n\
\n\
# Start Gradio app\n\
echo "🌐 Starting Gradio UI on port 7860..."\n\
echo "======================================================="\n\
python app.py\n\
\n\
# Cleanup on exit\n\
kill $IPFS_PID $MCP_PID 2>/dev/null\n\
' > /app/start.sh && chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:7860/ || exit 1

# Set environment variables
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7860
ENV IPFS_API_URL=/ip4/127.0.0.1/tcp/5001/http

# Run the startup script
CMD ["/app/start.sh"]
