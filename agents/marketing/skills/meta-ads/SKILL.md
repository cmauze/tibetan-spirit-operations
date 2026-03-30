---
name: meta-ads
description: Manage Facebook and Instagram advertising campaigns including strategy, creative, targeting, and optimization
version: "0.1.0"
category: marketing
tags: [meta, facebook, instagram, ads]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 750
phase: 1
depends_on: [shared/brand-guidelines, shared/channel-config]
external_apis: [supabase, meta]
cost_budget_usd: 0.15
---

# Meta Ads Management Skill

## Overview
Plan, execute, and optimize Facebook and Instagram advertising campaigns to drive awareness, consideration, and conversion.

## Key Sections

### Meta Advertising Strategy
- Define Meta's role in overall marketing strategy
- Identify campaigns aligned with business objectives
- Plan budget allocation between channels
- Define target customer segments for Meta
- Assess competitive landscape on Meta platforms

### Campaign Planning and Structure
- Plan campaign calendar aligned with marketing calendar
- Define campaigns by objective (awareness, conversions, etc.)
- Organize ad sets by audience and product
- Plan creative variations and A/B tests
- Coordinate with creative-library for assets
- Set performance targets and KPIs

### Audience Strategy and Targeting
- Build core audience segments
- Create lookalike audiences from customer lists
- Develop retargeting audiences by funnel stage
- Plan exclusion audiences (existing customers, etc.)
- Test custom and detailed targeting options
- Monitor audience overlap and efficiency

### Creative and Ad Format Strategy
- Develop creative by campaign objective
- Test single image, carousel, video, and collection ads
- Plan creative variations by audience
- Align with creative-library standards
- Optimize copy and CTAs for Meta
- Test creative refresh frequency

### Bid Strategy and Budget
- Select bid strategies by campaign objective
- Allocate budgets across campaigns and ad sets
- Plan daily and lifetime budgets
- Implement automated bid optimization
- Test bid strategies and scaling approaches
- Monitor cost per result and ROI

### Campaign Execution
- Set up campaigns, ad sets, and ads in Ads Manager
- Configure conversion tracking and attribution
- Implement UTM parameters for attribution
- Set up dynamic product ads if applicable
- Configure rules and automation for optimization
- Plan campaign launch timing

### Performance Monitoring and Optimization
- Monitor daily performance vs. targets
- Track cost per click, conversion, and ROI
- Identify high and low-performing audiences
- Test creative variations and performance
- Implement winner/loser analysis
- Optimize based on performance data

### A/B Testing Framework
- Design tests for creative, audience, and bidding
- Run tests with statistical significance requirement
- Document test hypothesis, results, and learnings
- Scale winning variations
- Iterate quickly with continuous testing
- Share learnings with team

### Audience and Lookalike Development
- Build seed audiences from customer lists
- Create lookalike audiences of various sizes
- Test different lookalike and targeting approaches
- Refresh lookalike audiences regularly
- Monitor lookalike quality and performance

### Reporting and Analytics
- Generate campaign performance reports
- Calculate ROI and payback period
- Track key metrics by campaign, ad set, and ad
- Build dashboards for real-time monitoring
- Share insights and recommendations
- Document performance trends and patterns

## Dependencies
- Integrates with: campaign-architecture, creative-library, performance-reporting, drift-detection
- References: product-knowledge for product-specific campaigns

## Success Metrics
- Cost per acquisition (CPA)
- Return on ad spend (ROAS)
- Conversion rate
- Audience quality and reach
- Campaign growth rate and scale
