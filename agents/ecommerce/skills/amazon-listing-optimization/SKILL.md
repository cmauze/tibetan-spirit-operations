---
name: amazon-listing-optimization
description: Optimize Amazon listings following title rules, bullet points, and A+ Content best practices for maximum conversion
version: "0.1.0"
category: ecommerce
tags: [amazon, listings, asin]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 600
phase: 1
depends_on: [shared/brand-guidelines, shared/channel-config, shared/product-knowledge]
external_apis: [supabase, amazon]
cost_budget_usd: 0.15
---

# Amazon Listing Optimization Skill

## Overview
Maximize Amazon search visibility and conversion through compliance-aware optimization of titles, bullets, descriptions, and A+ Content.

## Key Sections

### Title Optimization
- Follow Amazon title guidelines (brand, product type, key attributes)
- Include primary search terms in title
- Balance keyword density with readability
- Stay within character limits and guidelines
- Verify title compliance with Amazon rules
- Test title variations for performance
- Monitor search placement impact

### Bullet Point Optimization
- Write 3-5 compelling, benefit-focused bullets
- Lead with most important features/benefits
- Include primary and secondary keywords
- Address common customer questions
- Use consistent formatting and tone
- Verify bullets enhance readability
- Test bullet variations for conversion lift

### Product Description
- Write detailed, scannable description
- Lead with key benefits and use cases
- Include technical specifications
- Address pain points and objections
- Use clear paragraphing and formatting
- Include material, dimensions, care instructions
- Optimize for both keywords and conversion

### Enhanced Content (A+ Content)
- Create modules with rich text and images
- Tell product story with lifestyle modules
- Highlight key benefits with comparison modules
- Add technical specs with specification modules
- Showcase use cases with demonstration
- Test A+ modules for conversion impact

### Search Positioning
- Research high-volume Amazon keywords
- Identify long-tail and niche keywords
- Monitor search term performance
- Adjust content for target keywords
- Track search placement and visibility
- Analyze competitor title/bullet strategies

### Listing Compliance and Audit
- Verify compliance with Amazon policies
- Check for prohibited claims or language
- Validate product images meet requirements
- Review pricing and availability accuracy
- Monitor for quality violations

### Performance Monitoring
- Track impressions, clicks, and conversion rate
- Monitor organic search ranking
- Analyze A/B test results
- Identify conversion barriers
- Track changes in visibility and sales
- Report on ROI of optimizations

## Dependencies
- Integrates with: content-performance, cross-channel-parity
- References: product-knowledge for product specifications

## Success Metrics
- Search impression volume
- Organic conversion rate
- Average position in search results
- Click-through rate
- Revenue per listing
