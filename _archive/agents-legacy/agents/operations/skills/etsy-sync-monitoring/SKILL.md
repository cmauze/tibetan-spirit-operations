---
name: etsy-sync-monitoring
description: Monitor CedCommerce sync status, detect sync failures, alert on issues, and coordinate remediation
version: "0.1.0"
category: operations
tags: [etsy, sync, monitoring]
author: operations-team
model: haiku
cacheable: true
estimated_tokens: 400
phase: 1
depends_on: [shared/brand-guidelines, shared/channel-config]
external_apis: [supabase, etsy]
cost_budget_usd: 0.05
---

# Etsy Sync Monitoring Skill

## Overview
Proactively monitor inventory and listing synchronization between Shopify and Etsy via CedCommerce, detect failures, and coordinate fixes.

## Key Sections

### CedCommerce Connection Monitoring
- Verify sync connection is active and healthy
- Check sync status dashboard regularly
- Monitor for authentication or API errors
- Alert if sync disconnects

### Inventory Sync Validation
- Monitor inventory level synchronization
- Detect inventory sync delays or mismatches
- Verify stock updates propagate to Etsy
- Identify SKUs with sync issues

### Listing Sync Monitoring
- Verify product listing updates sync to Etsy
- Monitor price changes propagate correctly
- Check for title or description sync failures
- Alert on any listing update failures

### Failure Detection and Alerting
- Establish monitoring thresholds and alerts
- Detect common sync failure patterns
- Identify which items fail to sync
- Generate alerts for immediate attention

### Remediation Coordination
- Document sync failure details
- Troubleshoot sync issues with CedCommerce
- Coordinate manual updates if needed
- Re-sync corrected data

### Performance Tracking
- Monitor sync speed and latency
- Track sync success rates
- Identify recurring problematic SKUs or listings
- Report on sync reliability

### Escalation Process
- Escalate unresolved sync issues
- Coordinate with CedCommerce support
- Implement permanent fixes
- Prevent future occurrences

## Dependencies
- Integrates with: inventory-management, etsy-content-optimization
- External: CedCommerce integration

## Success Metrics
- Sync uptime percentage
- Inventory sync accuracy
- Time to detect failures
- Time to resolution
