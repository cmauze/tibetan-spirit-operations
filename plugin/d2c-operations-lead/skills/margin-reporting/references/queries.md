# Margin Reporting — Query Patterns & Report Template

## SQL Query Patterns

### 1. SKU-Level Margins

```sql
SELECT
  sku,
  product_title,
  category,
  channel,
  revenue_net,
  cogs_total,
  gross_margin_pct,
  cogs_confidence,          -- 'confirmed' | 'estimated'
  margin_floor_pct,
  (gross_margin_pct < margin_floor_pct) AS below_floor,
  (gross_margin_pct < 0)                AS negative_margin
FROM product_margin_detail
WHERE period_start = date_trunc('week', current_date - interval '7 days')
ORDER BY gross_margin_pct ASC;
```

### 2. Channel Profitability Rollup

```sql
SELECT
  channel,
  period_month,
  total_revenue_net,
  total_cogs,
  gross_margin_pct,
  LAG(gross_margin_pct) OVER (PARTITION BY channel ORDER BY period_month) AS prior_margin_pct,
  (gross_margin_pct - LAG(gross_margin_pct) OVER (PARTITION BY channel ORDER BY period_month)) AS margin_delta_pp
FROM channel_profitability_monthly
WHERE period_month >= date_trunc('month', current_date - interval '3 months')
ORDER BY channel, period_month;
```

### 3. Category Rollup

```sql
SELECT
  category,
  COUNT(DISTINCT sku)                        AS sku_count,
  SUM(revenue_net)                           AS category_revenue,
  SUM(cogs_total)                            AS category_cogs,
  ROUND(
    (SUM(revenue_net) - SUM(cogs_total)) / NULLIF(SUM(revenue_net), 0) * 100,
    1
  )                                          AS category_margin_pct,
  BOOL_OR(cogs_confidence = 'estimated')     AS has_estimated_cogs,
  COUNT(*) FILTER (WHERE gross_margin_pct < margin_floor_pct) AS below_floor_count
FROM product_margin_detail
WHERE period_start = date_trunc('week', current_date - interval '7 days')
GROUP BY category
ORDER BY category_margin_pct ASC;
```

### 4. Below-Floor Alert Query

```sql
SELECT
  sku,
  product_title,
  category,
  channel,
  gross_margin_pct,
  margin_floor_pct,
  (gross_margin_pct - margin_floor_pct) AS gap_pp,
  cogs_confidence,
  CASE
    WHEN gross_margin_pct < 0 THEN 'URGENT — negative margin'
    ELSE 'ALERT — below floor'
  END AS alert_level
FROM product_margin_detail
WHERE period_start = date_trunc('week', current_date - interval '7 days')
  AND gross_margin_pct < margin_floor_pct
ORDER BY gross_margin_pct ASC;
```


```sql
SELECT
```

---

## Trend Arrow Logic


| Condition | Arrow |
|-----------|-------|
| `margin_delta_pp >= 2.0` | ▲ |
| `margin_delta_pp <= -2.0` | ▼ |
| `-2.0 < margin_delta_pp < 2.0` | ─ |

---

## Report Template

```
{BRAND_NAME} — WEEKLY MARGIN REPORT
Week ending: {YYYY-MM-DD}
Generated: {timestamp} | ai_generated: true

═══════════════════════════════════════
EXECUTIVE SUMMARY
═══════════════════════════════════════
Overall gross margin:  {X.X}%  {trend arrow}  (prior week: {X.X}%)
Revenue (net):         ${X,XXX}
COGS coverage:         {X} confirmed SKUs / {X} estimated SKUs
Below-floor alerts:    {N} SKUs  ({N} URGENT)
Anomalies flagged:     {N}

═══════════════════════════════════════
BY CATEGORY
═══════════════════════════════════════
{category}             {X.X}%  {trend arrow}  [{confirmed|estimated*}]
  └─ {N} SKUs | Revenue: ${X,XXX} | Below-floor: {N}
...


═══════════════════════════════════════
BY CHANNEL
═══════════════════════════════════════
{channel}              {X.X}%  {trend arrow}
  Revenue: ${X,XXX} | Floor: {X.X}% | Gap to floor: {+/−X.X}pp
...

═══════════════════════════════════════
BELOW-FLOOR ALERTS
═══════════════════════════════════════
[URGENT — negative margin]
  Channel: {channel} | Category: {category}
  Margin: {X.X}% | Floor: {X.X}% | Gap: {−X.X}pp
  COGS: {confirmed|estimated}

  ...

═══════════════════════════════════════
═══════════════════════════════════════
Charitable allocation: {X.X}% of revenue (${XXX})

═══════════════════════════════════════
ACTION ITEMS
═══════════════════════════════════════
[ ] {Specific action derived from alerts or anomalies}
...

═══════════════════════════════════════
DATA QUALITY NOTES
═══════════════════════════════════════
- Estimated COGS rows: {N}
- Anomalies requiring investigation: {descriptions}
- Missing data: {any gaps noted}
```

---



