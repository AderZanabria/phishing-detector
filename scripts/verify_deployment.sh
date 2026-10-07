#!/usr/bin/env bash
# Verifica un backend ya desplegado. Uso: ./scripts/verify_deployment.sh https://api.ejemplo.com
set -u
BASE="${1:-}"
if [ -z "$BASE" ]; then
  echo "Uso: $0 https://tu-backend.onrender.com"
  exit 1
fi
BASE="${BASE%/}"
FAIL=0

check() {
  local name="$1" ok="$2"
  if [ "$ok" = "1" ]; then
    printf '\033[32mOK\033[0m  %s\n' "$name"
  else
    printf '\033[31mFAIL\033[0m %s\n' "$name"
    FAIL=1
  fi
}

start=$(python -c 'import time; print(time.time())')
health=$(curl -sS -m 20 -w '\n%{http_code}' "$BASE/health" || true)
code=$(printf '%s' "$health" | tail -n 1)
body=$(printf '%s' "$health" | sed '$d')
loaded=$(printf '%s' "$body" | python -c 'import json,sys; print(json.load(sys.stdin).get("model_loaded"))' 2>/dev/null || echo false)
[ "$code" = "200" ] && [ "$loaded" = "True" ]
check "GET /health 200 y model_loaded" $?

predict() {
  curl -sS -m 20 -w '\n%{http_code}' -X POST "$BASE/api/v1/predict" \
    -H 'Content-Type: application/json' -d "$1"
}

legit=$(predict '{"url":"https://www.google.com"}')
legit_code=$(printf '%s' "$legit" | tail -n 1)
legit_flag=$(printf '%s' "$legit" | sed '$d' | python -c 'import json,sys; print(json.load(sys.stdin).get("is_phishing"))' 2>/dev/null || echo '')
[ "$legit_code" = "200" ] && [ "$legit_flag" = "False" ]
check "URL legítima no marcada como phishing" $?

phish=$(predict '{"url":"http://192.168.0.1/login.php"}')
phish_code=$(printf '%s' "$phish" | tail -n 1)
phish_flag=$(printf '%s' "$phish" | sed '$d' | python -c 'import json,sys; print(json.load(sys.stdin).get("is_phishing"))' 2>/dev/null || echo '')
[ "$phish_code" = "200" ] && [ "$phish_flag" = "True" ]
check "URL sospechosa marcada como phishing" $?

batch=$(curl -sS -m 20 -w '\n%{http_code}' -X POST "$BASE/api/v1/predict/batch" \
  -H 'Content-Type: application/json' \
  -d '{"urls":["https://www.google.com","https://example.com","http://192.168.0.1/login.php"]}')
batch_code=$(printf '%s' "$batch" | tail -n 1)
batch_n=$(printf '%s' "$batch" | sed '$d' | python -c 'import json,sys; print(len(json.load(sys.stdin).get("results", [])))' 2>/dev/null || echo 0)
[ "$batch_code" = "200" ] && [ "$batch_n" = "3" ]
check "batch devuelve 3 results" $?

end=$(python -c 'import time; print(time.time())')
fast=$(python -c "print(1 if float('$end') - float('$start') < 2 else 0)")
check "tiempo total < 2s" "$fast"
exit $FAIL
