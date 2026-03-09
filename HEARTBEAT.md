# HEARTBEAT.md

# Quota warning monitor

- Check `/status` usage (session_status) on each heartbeat.
- If **day remaining < 25%** OR **week remaining < 25%**, send an alert in this channel with current remaining % and ETA.
- If both are >= 25%, reply `HEARTBEAT_OK`.
