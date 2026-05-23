#!/usr/bin/env bash
# Sthala Bootstrap Installer
# Usage: curl -fsSL https://raw.githubusercontent.com/kannanokannan/sthala/main/install.sh | bash
#        bash install.sh --profile ca-firm
#        bash install.sh --profile distributor --tier 2

set -euo pipefail

STHALA_VERSION="0.1.0"
STHALA_REPO="https://github.com/kannanokannan/sthala"
STHALA_PROFILE="${STHALA_PROFILE:-generic}"
STHALA_DIR="${STHALA_DIR:-/opt/sthala}"
STHALA_DATA="${STHALA_DATA:-/var/sthala/data}"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()   { echo -e "${BLUE}[sthala]${NC} $*"; }
ok()    { echo -e "${GREEN}[ok]${NC} $*"; }
warn()  { echo -e "${YELLOW}[warn]${NC} $*"; }
error() { echo -e "${RED}[error]${NC} $*"; exit 1; }

# Parse args
while [[ $# -gt 0 ]]; do
  case $1 in
    --profile) STHALA_PROFILE="$2"; shift 2 ;;
    --tier)    STHALA_TIER="$2"; shift 2 ;;
    --dir)     STHALA_DIR="$2"; shift 2 ;;
    --help)    echo "Usage: install.sh [--profile PROFILE] [--tier TIER] [--dir DIR]"; exit 0 ;;
    *)         warn "Unknown option: $1"; shift ;;
  esac
done

echo ""
echo "  ███████╗████████╗██╗  ██╗ █████╗ ██╗      █████╗ "
echo "  ██╔════╝╚══██╔══╝██║  ██║██╔══██╗██║     ██╔══██╗"
echo "  ███████╗   ██║   ███████║███████║██║     ███████║"
echo "  ╚════██║   ██║   ██╔══██║██╔══██║██║     ██╔══██║"
echo "  ███████║   ██║   ██║  ██║██║  ██║███████╗██║  ██║"
echo "  ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝"
echo ""
echo "  Your AI's place. v${STHALA_VERSION}"
echo "  Profile: ${STHALA_PROFILE}"
echo ""

# ── Prerequisites ──────────────────────────────────────────────────────────────

log "Checking prerequisites..."

# OS check
if [[ -f /etc/os-release ]]; then
  source /etc/os-release
  log "OS: ${PRETTY_NAME:-Unknown}"
else
  warn "Cannot determine OS. Proceeding cautiously."
fi

# Root check
if [[ $EUID -eq 0 ]]; then
  warn "Running as root. Podman rootless preferred. Continuing anyway."
fi

# RAM check
RAM_GB=$(free -g | awk '/^Mem:/{print $2}')
log "RAM: ${RAM_GB}GB detected"
if [[ $RAM_GB -lt 16 ]]; then
  error "Minimum 16GB RAM required. Found ${RAM_GB}GB."
fi

# Disk check
DISK_FREE=$(df -BG / | awk 'NR==2 {print $4}' | tr -d 'G')
log "Disk free: ${DISK_FREE}GB"
if [[ $DISK_FREE -lt 100 ]]; then
  error "Minimum 100GB free disk required. Found ${DISK_FREE}GB."
fi

# Container runtime
if command -v podman &>/dev/null; then
  CONTAINER_CMD="podman"
  COMPOSE_CMD="podman-compose"
  ok "Podman found: $(podman --version)"
elif command -v docker &>/dev/null; then
  CONTAINER_CMD="docker"
  COMPOSE_CMD="docker compose"
  ok "Docker found: $(docker --version)"
else
  log "No container runtime found. Installing Podman..."
  if command -v apt-get &>/dev/null; then
    apt-get update -qq && apt-get install -y -qq podman podman-compose
  elif command -v dnf &>/dev/null; then
    dnf install -y -q podman podman-compose
  else
    error "Cannot install Podman. Please install manually: https://podman.io/getting-started/installation"
  fi
  CONTAINER_CMD="podman"
  COMPOSE_CMD="podman-compose"
fi

# Git
if ! command -v git &>/dev/null; then
  log "Installing git..."
  apt-get install -y -qq git 2>/dev/null || dnf install -y -q git 2>/dev/null || error "Cannot install git."
fi

# ── Hardware Detection ─────────────────────────────────────────────────────────

log "Detecting hardware..."
if [[ -z "${STHALA_TIER:-}" ]]; then
  if bash "${STHALA_DIR}/hardware/detect.sh" &>/dev/null 2>&1; then
    STHALA_TIER=$(bash "${STHALA_DIR}/hardware/detect.sh" 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tier',1))" 2>/dev/null || echo "1")
  else
    # Basic fallback detection
    if command -v nvidia-smi &>/dev/null; then
      VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
      if [[ ${VRAM:-0} -ge 20000 ]]; then
        STHALA_TIER=2
      else
        STHALA_TIER=1
      fi
    else
      STHALA_TIER=1
    fi
  fi
fi

log "Hardware tier: ${STHALA_TIER}"

# ── Clone / Update Repo ────────────────────────────────────────────────────────

if [[ -d "${STHALA_DIR}/.git" ]]; then
  log "Sthala already installed at ${STHALA_DIR}. Updating..."
  git -C "${STHALA_DIR}" pull --quiet
  ok "Updated."
else
  log "Cloning Sthala to ${STHALA_DIR}..."
  git clone --quiet "${STHALA_REPO}" "${STHALA_DIR}"
  ok "Cloned."
fi

# ── Create Data Directories ────────────────────────────────────────────────────

log "Creating data directories..."
mkdir -p "${STHALA_DATA}"/{input,output,models,vectors,jobs,audit}
ok "Data directories created at ${STHALA_DATA}"

# ── Launch Stack ───────────────────────────────────────────────────────────────

log "Launching Sthala stack (profile: ${STHALA_PROFILE}, tier: ${STHALA_TIER})..."

export STHALA_PROFILE
export STHALA_TIER
export STHALA_DATA

cd "${STHALA_DIR}"
${COMPOSE_CMD} -f stack/docker-compose.yml up -d

# ── Wait for Readiness ─────────────────────────────────────────────────────────

log "Waiting for inference service to be ready (this may take 2-5 minutes on first run)..."
READY=0
for i in $(seq 1 30); do
  if curl -sf http://localhost:8080/health &>/dev/null; then
    READY=1
    break
  fi
  sleep 10
done

if [[ $READY -eq 0 ]]; then
  warn "Inference service did not respond within 5 minutes."
  warn "Check logs: ${COMPOSE_CMD} -f ${STHALA_DIR}/stack/docker-compose.yml logs inference"
else
  ok "Inference service is ready."
fi

# ── Done ───────────────────────────────────────────────────────────────────────

echo ""
echo "  ╔══════════════════════════════════════════════════════╗"
echo "  ║  Sthala is running.                                  ║"
echo "  ║                                                      ║"
echo "  ║  Web console:  http://localhost:8080                 ║"
echo "  ║  API (OpenAI): http://localhost:8080/v1              ║"
echo "  ║  Data folder:  ${STHALA_DATA}/input              ║"
echo "  ║                                                      ║"
echo "  ║  Next: drop your files in the input folder           ║"
echo "  ║  Then: bash recipes/${STHALA_PROFILE}/run.sh        ║"
echo "  ╚══════════════════════════════════════════════════════╝"
echo ""
echo "  Docs:    ${STHALA_REPO}"
echo "  Issues:  ${STHALA_REPO}/issues"
echo ""
