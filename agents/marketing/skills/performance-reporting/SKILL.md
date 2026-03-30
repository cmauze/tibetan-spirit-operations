---
name: performance-reporting
description: Generate daily/weekly marketing analytics, track KPIs, and provide actionable insights across all channels
version: "0.1.0"
category: marketing
tags: [reporting, analytics, roas]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 1025
phase: 1
depends_on: [shared/brand-guidelines, shared/supabase-ops-db]
external_apis: [supabase]
cost_budget_usd: 0.15
---

# Performance Reporting and Analytics Skill

## Overview
Systematically collect, analyze, and report marketing performance data across channels to inform decision-making and drive continuous improvement.

## Key Sections

### Reporting Framework and Strategy
- Define KPIs by channel and business objective
- Establish reporting cadence (daily, weekly, monthly)
- Select reporting tools and dashboards
- Determine audience and format for each report
- Plan executive summary approach
- Establish data accuracy and validation standards

### Data Collection and Consolidation
- Collect data from all marketing platforms
- Consolidate data from multiple sources
- Ensure data consistency and accuracy
- Validate data quality and completeness
- Resolve data discrepancies
- Document data sources and update timing

### Dashboard and Visualization
- Build executive dashboard for leadership
- Create channel-specific dashboards
- Implement real-time performance monitoring
- Visualize key metrics and trends
- Use appropriate chart types for clarity
- Update dashboards regularly

### Daily Reporting
- Track daily performance by channel
- Monitor spend vs. budget
- Alert on performance anomalies
- Identify quick optimization opportunities
- Document daily performance summary
- Maintain daily performance log

### Weekly Reporting
- Generate comprehensive weekly reports
- Summarize key performance metrics
- Compare actual to targets
- Analyze performance trends
- Highlight wins and opportunities
- Provide optimization recommendations

### Monthly Reporting
- Generate detailed monthly performance reports
- Calculate month-over-month and year-over-year trends
- Provide channel-specific analysis
- Calculate ROI and profitability metrics
- Summarize insights and learnings
- Present recommendations for next month

### Attribution and Multi-Touch Analytics
- Implement attribution modeling
- Track assisted conversions
- Understand customer journey
- Assign credit to multiple touchpoints
- Analyze channel interactions
- Optimize based on attribution insights

### Cohort Analysis
- Track customer cohorts by acquisition channel
- Analyze retention and lifetime value by cohort
- Identify high-value customer segments
- Track product affinity by cohort
- Measure repeat purchase rate
- Optimize acquisition by cohort profitability

### Conversion Funnel Analysis
- Track conversion rates by stage
- Identify funnel drop-off points
- Analyze conversion path variations
- Measure impact of optimizations
- Identify bottlenecks and barriers
- Recommend improvement actions

### Competitive and Benchmarking Analysis
- Benchmark performance vs. industry standards
- Track competitive performance
- Compare pricing and positioning
- Analyze competitor marketing effectiveness
- Identify competitive opportunities
- Report on competitive threats

### ROI and Profitability Analysis
- Calculate ROI by channel and campaign
- Track customer acquisition cost (CAC)
- Measure lifetime value (LTV)
- Calculate LTV:CAC ratio
- Track payback period
- Analyze profitability trends

### Forecasting and Planning
- Forecast revenue by channel
- Project performance based on trends
- Plan seasonal adjustments
- Forecast budget allocation
- Identify growth opportunities
- Present scenarios for planning

### Insights and Recommendations
- Identify key insights from data
- Provide actionable recommendations
- Prioritize optimization opportunities
- Quantify impact of recommendations
- Present findings to stakeholders
- Document decisions and actions taken

### Data Governance and Accuracy
- Validate data quality regularly
- Document data sources and definitions
- Maintain data dictionary
- Ensure consistent metrics across reports
- Reconcile data discrepancies
- Audit reporting accuracy

## Dependencies
- Integrates with: all marketing channel skills, campaign-architecture, drift-detection
- References: platform analytics and reporting tools

## Success Metrics
- Report completion rate and timeliness
- Data accuracy and validation percentage
- Action taken on recommendations
- Impact of recommended optimizations
- Stakeholder satisfaction with reporting
- Decision quality based on analytics
