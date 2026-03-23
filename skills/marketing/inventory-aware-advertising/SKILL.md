---
name: Inventory-Aware Advertising
description: Pause or start ads based on stock levels, prevent overselling, and optimize ad spend for inventory constraints
---

# Inventory-Aware Advertising Skill

## Overview
Implement dynamic advertising controls tied to inventory levels to prevent overselling, manage cash flow, and optimize ad efficiency.

## Key Sections

### Inventory Monitoring Integration
- Connect advertising platforms to inventory system
- Real-time inventory level tracking
- Monitor stock levels by SKU and location
- Alert on inventory changes
- Track inventory velocity and trends
- Identify slow-moving and fast-moving items

### Stock Level Thresholds
- Define minimum stock levels by product
- Set safety stock requirements
- Define lead time and reorder points
- Calculate inventory holding costs
- Establish pause/resume thresholds
- Plan threshold adjustments by season

### Auto-Pause Rules by Platform
- Google Ads: Pause campaigns for out-of-stock
- Amazon PPC: Pause product ads when stock low
- Meta/Facebook: Pause product catalog ads
- Etsy Ads: Pause promoted listings
- Shopify: Pause ads at collection/channel level
- Implement platform-specific pause mechanics

### Low Stock Messaging Strategy
- Display "low stock" warnings on product pages
- Add limited availability messaging to ads
- Adjust ad copy for low inventory
- Update product availability status
- Implement backorder messaging if applicable
- Change product visibility in catalogs

### Bid Adjustment Strategy
- Reduce bids for low-stock products
- Maintain bids for adequate stock products
- Increase bids for overstocked items
- Balance visibility with inventory availability
- Test bid adjustment impacts
- Optimize for inventory-aware profitability

### Campaign Pause/Resume Automation
- Set rules to auto-pause campaigns when stock depletes
- Define grace period for immediate replenishment
- Implement partial pause (reduce spend) for low stock
- Auto-resume when stock replenished
- Manual override capability for special cases
- Document pause/resume actions

### Inventory Forecast Integration
- Incorporate forecasted inventory in rules
- Account for pending inbound shipments
- Plan pause/resume around restock dates
- Adjust advertising based on forecasted stock
- Monitor forecast accuracy
- Update rules based on forecast changes

### Overselling Prevention
- Monitor order rate vs. stock level
- Calculate inventory depletion rate
- Pause before stock runs out completely
- Alert on high overselling risk
- Implement backorder management if applicable
- Track overselling incidents

### Fulfillment Location Awareness
- Manage inventory by fulfillment location
- Pause ads for items in slow facilities
- Coordinate multi-location advertising
- Account for inter-warehouse transfers
- Monitor location-specific inventory
- Optimize fulfillment routing

### Seasonal and Event Inventory Planning
- Plan inventory for major selling events
- Coordinate ad intensity with stock levels
- Manage inventory for seasonal products
- Plan for holiday inventory surges
- Implement early pause for seasonal stock depletion
- Plan post-season clearance advertising

### Performance and Profitability Impact
- Calculate impact of inventory pausing on revenue
- Monitor profit impact of ad pausing
- Track inventory holding costs
- Measure obsolescence reduction
- Calculate cash flow impact
- Report on inventory optimization ROI

### Coordination with Supply Chain
- Integrate with supplier-communication
- Coordinate with fulfillment teams
- Plan reorder timing with advertising
- Alert supply chain on inventory issues
- Coordinate seasonal inventory builds
- Plan for lead time visibility

### Testing and Optimization
- Test pause thresholds for optimal results
- Monitor impact of different pause levels
- Test bid adjustment strategies
- Validate automation rules
- Measure customer satisfaction with changes
- Optimize rules based on learnings

### Reporting and Analytics
- Generate inventory-advertising alignment reports
- Track pause frequency by product
- Report on overselling prevention
- Calculate cost savings from pausing
- Monitor inventory turnover
- Share insights with stakeholders

## Dependencies
- Integrates with: all marketing channels, inventory-management, drift-detection
- References: product-knowledge for inventory information

## Success Metrics
- Overselling incidents (goal: zero)
- Inventory turnover rate
- Days inventory outstanding
- Advertising spend efficiency (ads paused/total)
- Profit impact of inventory optimization
- Revenue loss from paused advertising
