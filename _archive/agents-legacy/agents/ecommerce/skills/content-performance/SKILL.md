---
name: content-performance
description: Track page and product conversion rates, analyze performance metrics, and identify optimization opportunities
version: "0.1.0"
category: ecommerce
tags: [content, conversion, analytics]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 475
phase: 1
depends_on: [shared/brand-guidelines, shared/supabase-ops-db]
external_apis: [supabase]
cost_budget_usd: 0.15
---

# Content Performance Tracking Skill

## Overview
Analyze conversion metrics across pages and products to identify high-performers and optimization opportunities, guiding content strategy.

## Key Sections

### Data Collection
- Gather analytics from Shopify and Google Analytics
- Track page views and visitor behavior
- Collect conversion data by page and product
- Import transaction data and revenue

### Page Performance Analysis
- Track conversion rate by page type (category, featured, collection)
- Monitor bounce rates and time-on-page
- Identify high-traffic, low-converting pages
- Analyze traffic sources and referrers

### Product Performance Analysis
- Calculate conversion rate by product
- Track revenue and AOV by product
- Identify top performers and underperformers
- Analyze views-to-purchase ratio

### Customer Journey Analysis
- Track navigation patterns
- Identify common drop-off points
- Analyze cross-sell and upsell effectiveness
- Study cart abandonment patterns

### Competitive Context
- Compare internal performance to benchmarks
- Analyze category trends
- Identify market-driven changes
- Assess seasonal patterns

### Reporting and Insights
- Generate performance reports by page/product
- Calculate growth rates and trends
- Recommend high-impact optimizations
- Prioritize content improvements

### Optimization Tracking
- Monitor impact of content changes
- Track A/B test results
- Measure improvement from optimizations
- Document lessons learned

## Dependencies
- Integrates with: site-health, collection-management
- References: product-photography-standards, amazon-listing-optimization for content quality

## Success Metrics
- Page conversion rates
- Product conversion rates
- Revenue per page/product
- Time to identify and act on insights
