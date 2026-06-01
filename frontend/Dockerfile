# Multi-stage Dockerfile for MTG AI Frontend
# Based on FastAPI full-stack template best practices

# =============================================================================
# Stage 1: Dependencies
# =============================================================================
FROM node:22-alpine AS deps

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production=false

# =============================================================================
# Stage 2: Builder
# =============================================================================
FROM node:22-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source code
COPY . .

# Build arguments for environment configuration
ARG VITE_API_URL=/api
ENV VITE_API_URL=${VITE_API_URL}

# Build the application
RUN npm run build

# =============================================================================
# Stage 3: Production (nginx)
# =============================================================================
FROM nginx:alpine AS production

# Metadata labels
LABEL org.opencontainers.image.title="MTG AI Frontend"
LABEL org.opencontainers.image.description="Self-hosted competitive Commander (cEDH) deck-critique assistant: RAG over Scryfall/MTGJSON/meta data with a deterministic rules engine and a swappable generation backend."
LABEL org.opencontainers.image.authors="Byron Williams <byronawilliams@gmail.com>"

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Create non-root user for nginx
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup && \
    chown -R appuser:appgroup /var/cache/nginx && \
    chown -R appuser:appgroup /var/log/nginx && \
    chown -R appuser:appgroup /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R appuser:appgroup /var/run/nginx.pid

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -q --spider http://localhost/health || exit 1

# Run as non-root user
USER appuser

CMD ["nginx", "-g", "daemon off;"]

# =============================================================================
# Stage 4: Development (optional - for docker-compose dev)
# =============================================================================
FROM node:22-alpine AS development

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev)
RUN npm ci

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 3000

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
