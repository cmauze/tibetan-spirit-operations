---
name: google-ads
description: Manage Search, Shopping, and Performance Max campaigns including keyword strategy, bidding, and optimization
version: "0.1.0"
category: marketing
tags: [google, search, ads]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 825
phase: 1
depends_on: [shared/brand-guidelines, shared/channel-config]
external_apis: [supabase, google]
cost_budget_usd: 0.15
---

# Google Ads Management Skill

## Overview
Plan, execute, and optimize Google Search, Shopping, and Performance Max campaigns to capture high-intent customers and drive conversions.

## Key Sections

### Google Ads Strategy
- Define Google Ads role in marketing funnel (high-intent capture)
- Plan campaigns by product category and intent
- Allocate budget across Search, Shopping, and Performance Max
- Set performance targets and ROAS goals
- Plan campaign seasonal adjustments

### Search Campaign Strategy
- Identify high-intent keywords for each product/category
- Build keyword research and grouping strategy
- Plan brand, category, and competitor keywords
- Develop negative keyword list
- Create ad group structure for relevance
- Plan bidding strategy by keyword performance

### Keyword Research and Management
- Conduct keyword research by category
- Identify primary, secondary, and long-tail keywords
- Analyze search volume and competition
- Build keyword lists by campaign
- Implement negative keywords to improve relevance
- Monitor keyword performance and trends

### Ad Copy and Landing Page Strategy
- Create compelling ad headlines and descriptions
- Build ad variations for A/B testing
- Align ad copy with search intent
- Develop landing pages optimized for conversion
- Test messaging and calls-to-action
- Improve Quality Score through relevance

### Shopping Campaign Setup
- Configure Google Merchant Center feed
- Ensure product data quality and accuracy
- Implement product-specific bidding strategy
- Organize products by category for management
- Use product promotion rules
- Monitor feed quality and errors

### Performance Max Campaign Strategy
- Define goals and conversion events for PMax
- Build audience signals and targeting
- Prepare creative assets (images, video, copy)
- Set budgets and performance targets
- Monitor automated bidding and optimization
- Refine performance over time

### Bidding Strategy
- Select bid strategies by campaign type (Search, Shopping, PMax)
- Implement conversion value bidding where applicable
- Set bid adjustments by device, location, time
- Monitor CPC trends and bidding efficiency
- Test automated bid strategies
- Scale successful bidding approaches

### Quality Score Optimization
- Monitor Quality Score by keyword and ad
- Improve landing page relevance and user experience
- Enhance ad relevance and CTR
- Maintain healthy keyword/ad structure
- Test ad copy variations
- Target Quality Score improvements

### Performance Monitoring and Reporting
- Monitor campaign performance daily
- Track key metrics (impressions, clicks, conversions, ROAS)
- Analyze performance by campaign, ad group, keyword
- Generate weekly/monthly performance reports
- Identify trends and optimization opportunities
- Present insights and recommendations

### Campaign Optimization
- Pause underperforming keywords/products
- Increase bids on high-performing keywords
- Implement bid adjustments for device/location/time
- Test new keywords and product categories
- Implement quality improvements
- Scale successful campaigns

### Conversion Tracking and Attribution
- Set up conversion tracking for website and calls
- Implement proper UTM parameters
- Configure attribution models
- Track ROAS and ROI by campaign
- Measure assisted conversions
- Optimize based on conversion data

## Dependencies
- Integrates with: campaign-architecture, performance-reporting, drift-detection, inventory-aware-advertising
- References: product-knowledge for product keywords

## Success Metrics
- Cost per acquisition (CPA)
- Return on ad spend (ROAS)
- Conversion rate
- Quality Score average
- Click-through rate (CTR)
- Impression share
