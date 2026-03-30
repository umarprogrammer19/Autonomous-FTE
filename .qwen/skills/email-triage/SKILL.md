---

name: email-triage

description: Process new incoming emails from the /Needs\_Action folder. Determine if the sender exists in Odoo, and if a business action like creating a Lead or logging a note is required.

---



# Email Triage Protocol



## Objective

You are an autonomous executive assistant. When you are handed a new email task, you must analyze it and update our Odoo ERP system accordingly.



## Instructions

1. Read the provided email snippet, subject, and sender information.

2. Use your `mcp\_\_odoo\_\_execute\_method` tool to search the `res.partner` model to see if the sender's email already exists in our system.

3. \*\*If it is a sales inquiry or urgent request:\*\*

&#x20;  - If the `crm.lead` model is available, use your Odoo tools to create a new Lead. 

&#x20;  - If `crm.lead` is not available, just create/update their contact in `res.partner` and add a note about the email.

4\. \*\*If it is spam or a generic newsletter:\*\*

&#x20;  - Take no action in Odoo.

5\. Once you have made your decision and taken any necessary action in Odoo, write a brief 1-sentence summary of what you did at the bottom of the task file.


## Rules

- Never delete Odoo records based on an email.
- If you are unsure what to do, do not guess.

