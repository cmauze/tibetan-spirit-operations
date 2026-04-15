---
name: promotion-strategy
description: Define when and how to discount by category, apply channel-specific rules, and maximize promotion ROI
version: "0.1.0"
category: category-management
tags: [promotions, discounts, strategy]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 797
phase: 1
depends_on: [shared/brand-guidelines, shared/channel-config]
external_apis: [supabase]
cost_budget_usd: 0.15
---

# Promotion Strategy Skill

## Overview
Strategically plan promotions to drive volume, clear inventory, and maximize profitability while maintaining brand positioning and margin health.

## Key Sections

### Promotion Planning Framework
- Establish promotion calendar aligned with seasons
- Identify strategic promotion windows (holidays, events, seasonal)
- Align with marketing campaigns and thematic events
- Balance promotional frequency and intensity
- Account for channel-specific promotional opportunities

### Discount Strategy by Category
- Define discount tiers and depths for each category
- Establish minimum margin thresholds
- Plan discount timing to maximize relevance
- Consider category elasticity and customer expectations
- Differentiate premium vs. value tier discounting

### Channel-Specific Promotion Rules
- D2C: Full promotional flexibility, brand control
- Etsy: Limited promotional capability, positioning considerations
- Amazon: Promotional tactics (Lightning Deals, coupons, etc.)
- Marketplace rules: Follow platform requirements
- Plan channel-appropriate promotional tactics

### Promotional Mechanics
- Define discount types (percent off, dollar off, BOGO, bundling)
- Set promotional duration and constraints
- Plan threshold-based promotions (min order value)
- Structure limited-time offers
- Define bundle and cross-sell mechanics

### Margin and Profitability Analysis
- Calculate margin impact of promotions
- Determine minimum discount depth for profitability
- Assess incremental volume needed to justify discount
- Track promotional ROI and payback
- Build data-driven promotion decisions

### Inventory Clearance Strategy
- Identify products requiring clearance
- Plan clearance promotion depth and duration
- Coordinate with assortment-planning
- Manage clearance inventory expectations
- Track clearance success and lessons

### Customer Segment Targeting
- Segment customers by loyalty and lifetime value
- Target promotions to high-value segments
- Use email and SMS for targeted promotions
- Personalize promotion offers by customer
- Track response and engagement by segment

### Competitive Response Planning
- Monitor competitor promotional activity
- Coordinate with competitive-research
- Plan defensive and offensive promotional tactics
- Assess competitive promotional threats
- Maintain promotional discipline

### Campaign Execution and Monitoring
- Implement promotions across channels
- Monitor promotion performance in real-time
- Track customer response and conversion lift
- Identify underperforming promotions
- Adjust tactics based on performance data
- Document promotion results and ROI

## Dependencies
- Integrates with: pricing-strategy, assortment-planning, campaign-architecture, competitive-research
- References: product-knowledge for promotion eligibility

## Success Metrics
- Promotion ROI (incremental revenue vs. discount cost)
- Volume lift during promotions
- Margin impact and profitability
- Inventory clearance rate
- Customer acquisition cost via promotion
