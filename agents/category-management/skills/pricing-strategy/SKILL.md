---
name: pricing-strategy
description: Cross-channel pricing optimization while maintaining margin floors and considering all fees
version: "0.1.0"
category: category-management
tags: [pricing, margins, channels]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 717
phase: 1
depends_on: [shared/brand-guidelines, shared/channel-config, shared/product-knowledge]
external_apis: [supabase, shopify]
cost_budget_usd: 0.15
---

# Pricing Strategy Skill

## Overview
Develop and maintain consistent, profitable pricing across channels while optimizing for margin, competitiveness, and customer perception.

## Key Sections

### Margin Floor Definition
- Calculate cost of goods sold (COGS) by product
- Define minimum acceptable margin by product/category
- Account for fulfillment and overhead costs
- Establish margin targets by channel
- Review and update cost assumptions regularly

### Channel-Specific Fee Analysis
- D2C: Minimal fees (payment processor only)
- Etsy: Transaction, payment, shipping fees
- Amazon: Referral fees, FBA fees, storage fees
- eBay: Insertion, listing, final value fees
- Shopify: Platform fees and transaction fees
- Calculate net margins after all fees

### Competitive Pricing Research
- Monitor competitor prices by channel
- Identify price positioning opportunities
- Track price elasticity patterns
- Assess premium positioning feasibility
- Analyze competitor promotional tactics

### Channel-Specific Pricing Strategy
- D2C: Premium pricing opportunity, brand positioning
- Etsy: Competitive pricing, handmade positioning
- Amazon: Volume-focused, FBA fee consideration
- eBay: Promotional/discount positioning
- Align channel pricing with go-to-market strategy

### Dynamic Pricing Considerations
- Evaluate demand-based pricing
- Monitor inventory levels for dynamic pricing
- Track seasonality impact on pricing
- Consider promotional timing and depth
- Balance price consistency with margin optimization

### Pricing Optimization Process
- Analyze historical pricing and conversion impact
- Test price variations for elasticity
- Monitor competitor price reactions
- Track market share impact of price changes
- Document pricing decisions and rationale

### Promotional Pricing Strategy
- Define discount thresholds by category
- Calculate margin impact of promotions
- Plan promotional calendar
- Coordinate with campaign-architecture
- Monitor promotional effectiveness

### Price Monitoring and Audits
- Verify prices are set correctly across channels
- Check for pricing errors or discrepancies
- Monitor for channel sync failures
- Identify manual overrides or exceptions
- Reconcile with cost changes

### Reporting and Decision Support
- Generate margin reports by product/channel
- Highlight pricing anomalies
- Recommend pricing adjustments
- Track pricing strategy impact
- Present insights to leadership

## Dependencies
- Integrates with: amazon-fee-analysis, channel-profitability, promotion-strategy, competitive-research
- References: product-knowledge for product costs

## Success Metrics
- Average margin by product/channel
- Pricing compliance rate
- Competitive positioning score
- Promotion ROI
