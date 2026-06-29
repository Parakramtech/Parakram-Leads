#!/bin/bash
set -e

echo "=== Parakram Lead Intelligence - Production Deployment ==="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# --- Prerequisites ---
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker required. Install: curl -fsSL https://get.docker.com | sh${NC}"; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo -e "${RED}Docker Compose required.${NC}"; exit 1; }

# --- Get server IP ---
SERVER_IP=$(curl -s http://checkip.amazonaws.com 2>/dev/null || curl -s https://api.ipify.org 2>/dev/null || echo "YOUR_SERVER_IP")
echo -e "${GREEN}Detected server IP: ${SERVER_IP}${NC}"

# --- .env setup ---
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << EOF
# Database
DATABASE_URL=postgresql+asyncpg://sigma:sigma@postgres:5432/sigma_leads
DATABASE_URL_SYNC=postgresql://sigma:sigma@postgres:5432/sigma_leads
DB_PASSWORD=sigma

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# Security
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || echo "change-this-secret-key-in-production")

# OpenAI (optional - all services work offline without it)
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o

# SMTP (optional - needed for email sending)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=

# Twilio (optional - needed for SMS alerts)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=

# WhatsApp
WHATSAPP_API_KEY=
WHATSAPP_PHONE_NUMBER_ID=

# Personal Alerts
PERSONAL_ALERT_PHONE=
PERSONAL_ALERT_EMAIL=

# Server
SERVER_IP=${SERVER_IP}
PUBLIC_API_URL=http://${SERVER_IP}:80/api/v1

# Debug
DEBUG=false
EOF
    echo -e "${YELLOW}Edit .env to add your SMTP/Twilio/WhatsApp keys, then re-run.${NC}"
    echo -e "${YELLOW}For now, launching with defaults (all intelligence works, email/SMS optional).${NC}"
fi

# --- Pull & Build ---
echo -e "${GREEN}1. Building and starting services...${NC}"
docker compose -f docker compose.prod.yml up -d --build

# --- Migrate ---
echo -e "${GREEN}2. Running database migrations...${NC}"
sleep 3
docker compose -f docker compose.prod.yml exec -T backend alembic upgrade head 2>/dev/null || \
    echo -e "${YELLOW}Migration skipped (DB may still be starting). Run manually: docker compose exec backend alembic upgrade head${NC}"

# --- Health check ---
echo -e "${GREEN}3. Checking health...${NC}"
sleep 5
if curl -s -o /dev/null -w "%{http_code}" http://localhost/health | grep -q 200; then
    echo -e "${GREEN}Health check passed!${NC}"
else
    echo -e "${YELLOW}Health check pending. Check with: curl http://localhost/health${NC}"
fi

echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo -e "Frontend: http://${SERVER_IP}"
echo -e "API:      http://${SERVER_IP}/api/"
echo -e "Health:   http://${SERVER_IP}/health"
echo ""
echo -e "${YELLOW}First-time setup:${NC}"
echo -e "  1. Open http://${SERVER_IP} in browser"
echo -e "  2. Create admin account at /register"
echo -e "  3. Add SMTP/Twilio keys in Settings for email/SMS features"
echo -e "  4. Import leads via CSV or run scrapers"
echo -e ""
echo -e "${YELLOW}Commands:${NC}"
echo -e "  View logs:    docker compose logs -f"
echo -e "  Stop:         docker compose down"
echo -e "  Update:       git pull && ./scripts/deploy.sh"
