---
name: drift-detection
description: Monitor performance anomalies, detect issues early, and auto-pause underperforming campaigns
version: "0.1.0"
category: marketing
tags: [drift, anomaly, monitoring]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 1025
phase: 1
depends_on: [shared/brand-guidelines, shared/supabase-ops-db]
external_apis: [supabase]
cost_budget_usd: 0.15
---

# Drift Detection and Anomaly Monitoring Skill

## Overview
Establish automated and manual systems to detect performance anomalies, alert teams to issues, and implement guardrails to prevent profit erosion.

## Key Sections

### Anomaly Detection Framework
- Define baseline performance metrics by channel
- Establish performance thresholds and triggers
- Set alert conditions for anomalies
- Plan alert frequency and escalation
- Document anomaly types and responses
- Test detection accuracy and false positives

### Campaign Performance Thresholds
- Set ROAS minimum thresholds by channel
- Define CPA maximum thresholds
- Set conversion rate minimums
- Define click-through rate minimums
- Establish cost per click maximums
- Set engagement rate minimums

### Quality Score and Relevance Monitoring
- Monitor Google Ads Quality Scores
- Track relevance metrics by platform
- Alert on dropping quality scores
- Identify problematic keywords/ads
- Track impressions share losses
- Recommend quality improvements

### Bid and Budget Monitoring
- Track bid prices and trends
- Monitor cost per click changes
- Alert on unusual bid escalations
- Track budget pacing and overspend
- Monitor daily budget hits
- Alert on budget allocation issues

### Conversion Tracking Issues
- Monitor conversion tracking completeness
- Detect tracking implementation errors
- Alert on sudden conversion drops
- Validate conversion data accuracy
- Identify missing or incomplete tracking
- Flag tracking discrepancies

### Campaign Status Monitoring
- Monitor campaign pause/status changes
- Alert on unintended pauses
- Track policy violations or account issues
- Monitor ad approval status
- Alert on keyword disapprovals
- Document status changes and reasons

### Fraud and Bot Detection
- Monitor for suspicious traffic patterns
- Identify potential click fraud
- Track invalid traffic indications
- Monitor referrer and device patterns
- Alert on unusual geographic traffic
- Document suspected fraud incidents

### Profitability Monitoring
- Calculate profitability by campaign
- Alert on negative ROI campaigns
- Monitor margin impact of marketing
- Track product-specific profitability
- Alert on margin erosion trends
- Recommend profitability improvements

### Auto-Pause Rules Implementation
- Set rules to auto-pause underperforming campaigns
- Define pause criteria (ROAS, CPA thresholds)
- Implement gradual spend reduction before pause
- Alert on auto-pause actions
- Maintain manual override capability
- Document auto-pause actions and reasons

### Inventory and Stock-Out Monitoring
- Alert when products stock out
- Coordinate with inventory-aware-advertising
- Pause ads for out-of-stock items
- Reduce bids for low-stock products
- Monitor backorder status
- Update campaigns for limited inventory

### Alert and Escalation System
- Set up real-time alert system
- Define alert priority levels
- Route alerts to appropriate teams
- Implement alert fatigue prevention
- Set up manual review for high-impact issues
- Document alert response times

### Trend Analysis and Patterns
- Monitor performance trends over time
- Identify seasonal or cyclical patterns
- Track algorithm changes impact
- Monitor competitive changes
- Identify emerging issues early
- Build predictive models if applicable

### Reporting and Documentation
- Generate anomaly reports
- Document issues and root causes
- Track resolution time
- Report on detection accuracy
- Share findings with team
- Build knowledge base of issues

### Testing and Validation
- Test detection accuracy and sensitivity
- Monitor false positive rate
- Validate alert rules effectiveness
- Test auto-pause functionality
- Ensure manual override works
- Update thresholds based on performance

## Dependencies
- Integrates with: all marketing channel skills, performance-reporting, inventory-aware-advertising
- Monitors: platform APIs and analytics data

## Success Metrics
- Anomaly detection sensitivity and specificity
- Time to detect issues
- False positive rate
- Response time to alerts
- Impact of prevented issues (profit saved)
- System reliability and uptime
