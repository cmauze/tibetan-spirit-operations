#!/bin/bash
# Hook: Notification handler for Tibetan Spirit — delivers to Slack + local JSON
# Runs async (non-blocking, fire-and-forget)
# Env: SLACK_WEBHOOK_TS_ALERTS, SLACK_WEBHOOK_TS_CUSTOMER_SERVICE

set -euo pipefail

INPUT=$(cat)
DATA_DIR="data"

mkdir -p "$DATA_DIR"

python3 -c "
import json, sys, os, urllib.request, time

data = json.loads(sys.stdin.read())
notification_type = data.get('notification_type', 'unknown')
message = data.get('message', 'Notification')
session_id = data.get('session_id', 'unknown')

if notification_type == 'auth_success':
    sys.exit(0)

# --- Route to webhook ---
WEBHOOK_ALERTS = os.environ.get('SLACK_WEBHOOK_TS_ALERTS', '')
WEBHOOK_CS = os.environ.get('SLACK_WEBHOOK_TS_CUSTOMER_SERVICE', '')

cs_types = {'cs_draft', 'cs_escalation', 'customer_service'}
if notification_type in cs_types:
    webhook_url = WEBHOOK_CS
    channel_label = '#ts-customer-service'
else:
    webhook_url = WEBHOOK_ALERTS
    channel_label = '#ts-alerts'

# Block Kit message
blocks = [
    {
        'type': 'header',
        'text': {'type': 'plain_text', 'text': notification_type.replace('_', ' ').title(), 'emoji': True}
    },
    {
        'type': 'section',
        'text': {'type': 'mrkdwn', 'text': message[:3000]}
    },
    {
        'type': 'context',
        'elements': [{'type': 'mrkdwn', 'text': f'tibetan-spirit | Session: {session_id[:8]} | {channel_label}'}]
    }
]

payload = json.dumps({
    'text': f'{notification_type}: {message[:200]}',
    'blocks': blocks
}).encode()

# --- Rate limiting (5/hour/channel) ---
RATE_LIMIT_FILE = '$DATA_DIR/slack-rate-limits.json'
MAX_PER_HOUR = 5

try:
    with open(RATE_LIMIT_FILE, 'r') as f:
        rate_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    rate_data = {}

now_ts = time.time()
hour_ago = now_ts - 3600
recent = [t for t in rate_data.get(channel_label, []) if t > hour_ago]
rate_limited = len(recent) >= MAX_PER_HOUR

if not rate_limited:
    recent.append(now_ts)
rate_data[channel_label] = recent
with open(RATE_LIMIT_FILE, 'w') as f:
    json.dump(rate_data, f)

# Send to Slack
delivered_via = 'local_log'
if rate_limited:
    delivered_via = f'local_log (rate limited: {channel_label})'
elif webhook_url:
    try:
        req = urllib.request.Request(webhook_url, data=payload, headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req, timeout=5)
        delivered_via = f'slack ({channel_label})'
    except Exception as e:
        delivered_via = f'local_log (slack failed: {str(e)[:80]})'

# --- Always log locally ---
from datetime import datetime
log_file = '$DATA_DIR/notifications.json'
try:
    with open(log_file, 'r') as f:
        logs = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    logs = []

logs.append({
    'timestamp': datetime.now().astimezone().isoformat(),
    'type': notification_type,
    'message': message,
    'session_id': session_id[:8] if len(session_id) > 8 else session_id,
    'delivered_via': delivered_via
})

with open(log_file, 'w') as f:
    json.dump(logs, f, indent=2)
" <<< "$INPUT" 2>/dev/null || true

exit 0
