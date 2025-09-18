curl -sS -X POST http://localhost:8000/v1/agents/run \
  -H "X-API-Key: dev-key" -H "Content-Type: application/json" \
  -d '{"prompt":"add 2+2 using an agent","provider":"mock","stream":false}'
