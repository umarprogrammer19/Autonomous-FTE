---
name: ceo-briefing
description: Use this skill when the user asks for a business update, financial summary, or the Monday Morning CEO Briefing.
---

# Monday Morning CEO Briefing

## Objective

You are an autonomous executive assistant. Your job is to query our Odoo system, analyze our recent sales, and write a CEO briefing.



## Instructions

1. Use your `mcp\_\_odoo\_\_execute\_method` tool to search the `sale.order` model. 

2. Set the `method` to `search\_read`.

3. In the `kwargs\_json`, request the `name`, `partner\_id`, `state`, and `amount\_total` fields. Limit it to the last 10 records.

4. Analyze the data returned from Odoo. Calculate the total revenue from orders that are in the "sale" (confirmed) state.

5. Write a professional markdown report summarizing the recent sales and total confirmed revenue.

6. Save this report as `CEO\_Briefing.md` in the current directory using your file system tools.


## Rules

- Do NOT guess the data. Only use what the Odoo MCP tool returns.
- Be concise and professional.

