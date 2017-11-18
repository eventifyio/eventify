#!/bin/bash
uuid=$(uuidgen)
timestamp=$(date +%s)

json=$(cat <<EOF 
{
    "topic": "test",
    "kwargs": {
        "event_id": "a3fc874b-f5ec-45d2-a0b4-8e8006de88c0",
        "old_event_id": "$uuid",
        "message": "stuff and things",
        "timestamp": $timestamp,
        "name": "TestEvent",
        "trace_id": "6fe2aa3a-f5b9-4f9d-bdf9-2391e23a55bf"
    }
}
EOF
)

curl -H "Content-Type: application/json" \
     -d "$json" \
     http://localhost:8080/publish

