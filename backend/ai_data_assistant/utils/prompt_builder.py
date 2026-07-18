"""
Prompt Builder — constructs the LLM prompt with schema context and few-shot examples.
"""

from typing import List, Dict, Any
from .schema_classifier import get_relevant_schema


SYSTEM_INSTRUCTION = """You are a SQL query generator for a Debt Collection Management System. Your task is to convert natural language questions into PostgreSQL SQL queries.

## RULES (MUST FOLLOW):
1. Generate ONLY SELECT queries. Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE, or any DDL/DML.
2. Always use PostgreSQL syntax.
3. Inline filter values directly in the SQL — do NOT use parameterized placeholders like %(name)s. Write literal values directly (e.g., WHERE name = 'ACI Logistics', NOT WHERE name = %(name)s).
4. When filtering by date, use the format YYYY-MM-DD and cast with ::date.
5. Never include EXPLAIN, ANALYZE, or any diagnostic commands.
6. Never use pg_sleep, COPY, or any dangerous functions.
7. Return ONLY the SQL query without any markdown formatting, explanation, or surrounding backticks.
8. Prefix table aliases with their standard abbreviations (ci for credit_invoice, p for payment, c for customer, pc for parent customer, pd for payment_details, pi for payment_instrument, pit for payment_instrument_type, cl for claim).
9. For parent-child customer hierarchy: parent organizations (is_parent=TRUE) have child customers linked via c.parent_id = pc.id.
10. Use COALESCE for nullable columns, especially amounts.
11. Always include meaningful column aliases in the SELECT clause.
"""


FEW_SHOT_EXAMPLES = [
    {
        "question": "Show me all unpaid invoices for ACI Logistics that are past due",
        "sql": """SELECT ci.alias_id, ci.transaction_date, ci.sales_amount, ci.sales_return,
       (ci.sales_amount - ci.sales_return) AS net_due,
       (ci.transaction_date + ci.payment_grace_days) AS due_date,
       GREATEST(CURRENT_DATE - (ci.transaction_date + ci.payment_grace_days), 0) AS days_overdue
FROM credit_invoice ci
JOIN customer c ON c.id = ci.customer_id
JOIN customer pc ON pc.id = c.parent_id
WHERE pc.name = 'ACI Logistics'
  AND ci.payment_id IS NULL
  AND (ci.transaction_date + ci.payment_grace_days) < CURRENT_DATE
ORDER BY ci.transaction_date"""
    },
    {
        "question": "What is the total outstanding balance for all customers in the Dhaka branch?",
        "sql": """SELECT SUM(ci.sales_amount - ci.sales_return) AS total_outstanding
FROM credit_invoice ci
JOIN branch b ON b.id = ci.branch_id
WHERE b.name = 'Dhaka'
  AND ci.payment_id IS NULL"""
    },
    {
        "question": "List claims that have been submitted but not yet refunded",
        "sql": """SELECT cl.alias_id AS claim_id, c.name AS customer_name,
       pd.amount AS claim_amount, cl.submitted_date,
       (pd.amount - COALESCE(cl.refund_amount, 0)) AS remaining_amount
FROM claim cl
JOIN payment_details pd ON pd.id = cl.payment_details_id
JOIN payment p ON p.id = pd.payment_id
JOIN customer c ON c.id = p.customer_id
WHERE cl.submitted_date IS NOT NULL
  AND (cl.refund_amount IS NULL OR cl.refund_amount = 0)
ORDER BY cl.submitted_date"""
    },
    {
        "question": "Which customers have more than 30 days overdue?",
        "sql": """SELECT c.name AS customer_name,
       ci.alias_id AS invoice_id,
       ci.transaction_date,
       (ci.transaction_date + ci.payment_grace_days) AS due_date,
       GREATEST(CURRENT_DATE - (ci.transaction_date + ci.payment_grace_days), 0) AS days_overdue,
       (ci.sales_amount - ci.sales_return) AS amount_due
FROM credit_invoice ci
JOIN customer c ON c.id = ci.customer_id
WHERE ci.payment_id IS NULL
  AND GREATEST(CURRENT_DATE - (ci.transaction_date + ci.payment_grace_days), 0) > 30
ORDER BY days_overdue DESC"""
    },
    {
        "question": "Show me payment summary for last month including shortage amounts",
        "sql": """SELECT p.alias_id AS payment_id, p.received_date,
       c.name AS customer_name,
       p.total_amount, p.cash_equivalent_amount,
       p.claim_amount, p.shortage_amount
FROM payment p
JOIN customer c ON c.id = p.customer_id
WHERE p.received_date >= date_trunc('month', CURRENT_DATE - interval '1 month')
  AND p.received_date < date_trunc('month', CURRENT_DATE)
ORDER BY p.received_date"""
    },
    {
        "question": "List all sales returns by customer this year",
        "sql": """SELECT c.name AS customer_name,
       COUNT(ci.id) AS return_count,
       SUM(ci.sales_return) AS total_return_amount
FROM credit_invoice ci
JOIN customer c ON c.id = ci.customer_id
WHERE ci.sales_return > 0
  AND ci.transaction_date >= date_trunc('year', CURRENT_DATE)
GROUP BY c.name
ORDER BY total_return_amount DESC"""
    },
]


def build_prompt(question: str) -> List[Dict[str, str]]:
    relevant_schema = get_relevant_schema(question)

    selected_examples = []
    for example in FEW_SHOT_EXAMPLES:
        example_lower = example['question'].lower()
        question_lower = question.lower()
        if any(kw in example_lower for kw in question_lower.split()):
            if len(selected_examples) < 2:
                selected_examples.append(example)
        if len(selected_examples) >= 2:
            break

    if not selected_examples:
        selected_examples = FEW_SHOT_EXAMPLES[:2]

    examples_text = "\n\n".join([
        f"Question: {ex['question']}\nSQL: {ex['sql']}"
        for ex in selected_examples
    ])

    user_prompt = f"""## Database Schema
{relevant_schema}

## Examples
{examples_text}

## Question
{question}

## Instructions
Generate a PostgreSQL SELECT query for the above question. Return ONLY the SQL query, no explanation, no markdown formatting."""
    return [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": user_prompt},
    ]