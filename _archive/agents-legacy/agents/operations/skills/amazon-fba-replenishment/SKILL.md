---
name: amazon-fba-replenishment
description: Manage pallet shipments to Amazon Fulfillment Centers with prep requirements, label compliance, and inventory allocation
version: "0.1.0"
category: operations
tags: [amazon, fba, replenishment]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 400
phase: 1
depends_on: [shared/brand-guidelines, shared/channel-config]
external_apis: [supabase, amazon]
cost_budget_usd: 0.15
---

# Amazon FBA Replenishment Skill

## Overview
Coordinate inventory replenishment to Amazon FCs, ensuring proper packaging, labeling, and documentation to avoid inbound QC issues.

## Key Sections

### Inventory Level Monitoring
- Track inventory in Amazon FCs by ASIN
- Monitor sales velocity and turnover
- Identify SKUs approaching stock-out

### Replenishment Planning
- Determine replenishment quantities and timing
- Calculate lead time from fulfillment location to FC
- Plan pallet builds for efficiency

### Shipment Preparation
- Aggregate inventory for pallet shipment
- Apply Amazon barcode labels per requirement
- Organize pallets by FC destination
- Prepare case-level labeling

### Amazon Labeling Compliance
- Apply FNSKU labels to units if required
- Ensure label placement per Amazon specs
- Verify no commingling issues
- Generate barcode sheets

### Shipping to FCs
- Generate Amazon shipping labels
- Select carrier and arrange pickup
- Provide tracking information
- Monitor shipment transit

### Inbound Compliance
- Verify shipment received in Amazon system
- Monitor for QC flags or damage claims
- Confirm units available for sale

### Post-Receipt Monitoring
- Track products through Amazon's "receiving" status
- Identify and resolve any inbound issues
- Confirm final inventory update

## Dependencies
- Integrates with: inventory-management, fulfillment-domestic
- References: product-knowledge for SKU information

## Success Metrics
- On-time pallet arrival to FCs
- Zero inbound QC issues
- Inventory available for sale within SLA
