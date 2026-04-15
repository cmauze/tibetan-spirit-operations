---
name: agentic-discovery
description: Ensure product catalog is AI shopping agent-ready with proper schema, structured data, and metadata for discovery
version: "0.1.0"
category: ecommerce
tags: [ai-shopping, structured-data, schema]
author: operations-team
model: sonnet
cacheable: true
estimated_tokens: 550
phase: 1
depends_on: [shared/brand-guidelines, shared/product-knowledge]
external_apis: [supabase, shopify]
cost_budget_usd: 0.15
---

# Agentic Discovery Readiness Skill

## Overview
Prepare product catalog for AI-powered shopping agents by implementing JSON-LD structured data, proper taxonomy, and rich metadata.

## Key Sections

### JSON-LD Schema Implementation
- Implement Product schema with all relevant properties
- Include name, description, image, price, availability
- Add aggregateRating if reviews available
- Include offers and pricing information
- Verify schema is valid and complete
- Test schema with Google's schema validator

### Product Structured Data
- Add product type and category taxonomy
- Include material, color, size, other attributes
- Add brand and manufacturer information
- Include GTIN/UPC when applicable
- Verify data consistency across products

### Searchability Optimization
- Ensure products are discoverable by attribute
- Create proper category hierarchy
- Tag products for agent-based discovery
- Include synonyms and alternative terms
- Add seasonal or contextual tags

### Review and Rating Integration
- Display aggregate ratings in structured format
- Include review counts and recency
- Add rating distribution data
- Enable rating visibility for agents

### Inventory Status
- Mark inventory availability correctly
- Include in-stock indicators
- Add estimated delivery timeframe
- Update availability dynamically

### Price and Offer Structure
- Implement proper pricing schema
- Include currency and locale information
- Add promotional pricing if applicable
- Include shipping cost information

### Mobile and Voice Optimization
- Optimize for mobile discovery
- Prepare for voice search queries
- Ensure answer-able FAQ content
- Add quick product attributes

### Testing and Validation
- Validate all schema implementation
- Test with multiple validators
- Monitor for schema errors
- Verify agent accessibility to products

## Dependencies
- Integrates with: product-photography-standards, amazon-listing-optimization
- References: product-knowledge for product taxonomy

## Success Metrics
- Schema compliance percentage
- Product discoverability score
- Agent-indexed products
- Query coverage for products
