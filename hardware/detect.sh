#!/usr/bin/env bash
# Sthala Hardware Detection
# Outputs JSON: cpu, ram, gpu, disk, os, tier recommendation

set -euo pipefail

detect_cpu() {
  local model cores avx512
  model=$(grep -m1 "model name" /proc/cpuinfo 2>/dev/null | cut -d: -f2 | xargs || echo "unknown")
  cores=$(nproc 2>/dev/null || echo 0)
  avx512="false"
  grep -q "avx512f" /proc/cpuinfo 2>/dev/null && avx512="true"
  echo "{\"model\":\"${model}\",\"cores\":${cores},\"avx512\":${avx512}}"
}

detect_ram() {
  awk '/^MemTotal:/{printf "%d", $2/1024/1024}' /proc/meminfo 2>/dev/null || echo 0
}

detect_gpu() {
  if command -v nvidia-smi &>/dev/null; then
    local model vram
    model=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1 | xargs || echo "unknown")
    vram=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d ' ')
    vram_gb=$(( ${vram:-0} / 1024 ))
    echo "{\"vendor\":\"nvidia\",\"model\":\"${model}\",\"vram_gb\":${vram_gb}}"
  elif command -v rocm-smi &>/dev/null; then
    local model
    model=$(rocm-smi --showproductname 2>/dev/null | grep -oP '(?<=GPU\[0\] : ).*' | xargs || echo "unknown")
    echo "{\"vendor\":\"amd\",\"model\":\"${model}\",\"vram_gb\":0}"
  else
    echo "{\"vendor\":\"none\",\"model\":\"none\",\"vram_gb\":0}"
  fi
}

detect_disk() {
  df -BG / 2>/dev/null | awk 'NR==2 {print $4}' | tr -d 'G' || echo 0
}

detect_os() {
  if [[ -f /etc/os-release ]]; then
    source /etc/os-release
    echo "${ID:-unknown}-${VERSION_ID:-unknown}"
  else
    echo "unknown"
  fi
}

recommend_tier() {
  local ram_gb=$1 vram_gb=$2
  if   [[ $vram_gb -ge 48 ]];  then echo 4
  elif [[ $vram_gb -ge 24 ]];  then echo 2
  elif [[ $vram_gb -ge 16 ]];  then echo 2
  elif [[ $ram_gb  -ge 128 ]]; then echo 3
  elif [[ $ram_gb  -ge 64 ]];  then echo 2
  else                               echo 1
  fi
}

CPU=$(detect_cpu)
RAM=$(detect_ram)
GPU=$(detect_gpu)
DISK=$(detect_disk)
OS=$(detect_os)
VRAM=$(echo "$GPU" | python3 -c "import sys,json; print(json.load(sys.stdin).get('vram_gb',0))" 2>/dev/null || echo 0)
TIER=$(recommend_tier "$RAM" "$VRAM")

cat <<EOF
{
  "cpu": ${CPU},
  "ram_gb": ${RAM},
  "gpu": ${GPU},
  "disk_free_gb": ${DISK},
  "os": "${OS}",
  "tier": ${TIER},
  "recommendations": {
    "inference_backend": $([ "$VRAM" -ge 16 ] && echo '"vllm"' || echo '"llama.cpp"'),
    "default_model": $([ "$VRAM" -ge 24 ] && echo '"Sarvam-30B Q6_K"' || ([ "$RAM" -ge 32 ] && echo '"Qwen2.5-7B Q4"' || echo '"Phi-3 mini Q4"'))
  }
}
EOF
