"""
Schema Classifier — identifies which database tables/entities are relevant
to a natural language question using keyword matching.
"""

import re
from typing import List, Dict, Any


DOMAIN_TOPICS = {
    'customer': {
        'keywords': ['customer', 'client', 'organization', 'org', 'company', 'parent', 'child',
                     'branch', 'partner', 'supplier', 'vendor', 'buyer', 'dealer', 'distributor'],
        'tables': ['customer', 'branch'],
        'description': 'Customer profiles, hierarchy (parent/child), branch assignments, grace periods'
    },
    'aging': {
        'keywords': ['aging', 'overdue', 'matured', 'immature', 'mature', 'past due',
                     'outstanding', 'due', 'grace', 'days overdue', 'delinquent', 'aged'],
        'tables': ['credit_invoice', 'customer', 'payment'],
        'description': 'Invoice aging, matured vs immature dues, grace period calculations, days overdue'
    },
    'invoice': {
        'keywords': ['invoice', 'credit invoice', 'sales', 'sale', 'transaction', 'grn',
                     'delivery', 'shipment', 'good received', 'good receipt', 'bill'],
        'tables': ['credit_invoice', 'customer'],
        'description': 'Sales invoices, GRN numbers, transaction dates, sales amounts, sales returns'
    },
    'return': {
        'keywords': ['return', 'sales return', 'credit note', 'refund', 'reversal',
                     'returned goods', 'goods returned'],
        'tables': ['credit_invoice'],
        'description': 'Sales return records, returned amounts'
    },
    'payment': {
        'keywords': ['payment', 'received', 'collection', 'cash', 'cheque', 'check',
                     'receipt', 'paid', 'settlement', 'remittance', 'pay'],
        'tables': ['payment', 'payment_details', 'payment_instrument', 'payment_instrument_type'],
        'description': 'Payments received, payment details, instruments (cheque/cash/claim), received dates'
    },
    'claim': {
        'keywords': ['claim', 'submitted', 'refund', 'refunded', 'recovery', 'supplier claim',
                     'claim settlement', 'claim amount', 'remaining claim'],
        'tables': ['claim', 'payment_details', 'payment'],
        'description': 'Claims submitted to suppliers, refund amounts, refund dates, remaining amounts'
    },
    'shortage': {
        'keywords': ['shortage', 'excess', 'short', 'extra', 'over', 'under payment',
                     'short paid', 'over paid', 'shortage amount'],
        'tables': ['payment'],
        'description': 'Payment shortage or excess amounts, discrepancies'
    },
    'financial': {
        'keywords': ['balance', 'outstanding', 'total due', 'net due', 'current due',
                     'financial', 'amount', 'summary', 'total', 'grand total'],
        'tables': ['credit_invoice', 'payment', 'customer'],
        'description': 'Current dues, outstanding balances, received payments, financial summaries'
    },
    'instrument': {
        'keywords': ['instrument', 'payment type', 'cash equivalent', 'non cash',
                     'cheque number', 'claim number', 'instrument type', 'serial no'],
        'tables': ['payment_instrument', 'payment_instrument_type', 'payment_details'],
        'description': 'Payment instrument types, cash vs non-cash instruments, instrument serial numbers'
    },
    'report': {
        'keywords': ['report', 'list', 'show', 'display', 'get', 'find', 'search',
                     'view', 'summary', 'details', 'breakdown', 'all'],
        'tables': ['credit_invoice', 'payment', 'customer', 'claim'],
        'description': 'General reporting and listing queries'
    },
}


def classify_question(question: str) -> List[Dict[str, Any]]:
    question_lower = question.lower()
    matched_topics = []

    for topic_name, topic_info in DOMAIN_TOPICS.items():
        score = 0
        for keyword in topic_info['keywords']:
            pattern = re.escape(keyword)
            if re.search(r'\b' + pattern + r's?\b', question_lower):
                score += 1

        if score > 0:
            matched_topics.append({
                'topic': topic_name,
                'score': score,
                'tables': topic_info['tables'],
                'description': topic_info['description'],
            })

    matched_topics.sort(key=lambda x: x['score'], reverse=True)

    return matched_topics


def get_relevant_tables(question: str) -> List[str]:
    matched = classify_question(question)
    tables = set()
    for topic in matched:
        tables.update(topic['tables'])
    return list(tables)


def get_relevant_schema(question: str) -> str:
    tables = get_relevant_tables(question)
    if not tables:
        tables = ['credit_invoice', 'payment', 'customer', 'claim', 'payment_details', 'payment_instrument']

    schema_blocks = []

    for table_name in tables:
        schema_info = SCHEMA_DEFINITIONS.get(table_name)
        if schema_info:
            schema_blocks.append(schema_info)

    if not schema_blocks:
        schema_blocks = list(SCHEMA_DEFINITIONS.values())

    return '\n\n'.join(schema_blocks)


SCHEMA_DEFINITIONS = {
    'customer': """
Table: customer (alias: c)
Columns:
  id (INTEGER, PK)
  alias_id (VARCHAR, unique identifier)
  name (TEXT) - customer/organization name
  is_parent (BOOLEAN) - TRUE if this is a parent organization
  parent_id (INTEGER, FK -> customer.id) - parent organization reference
  branch_id (INTEGER, FK -> branch.id) - branch assignment
  grace_days (INTEGER) - payment grace period in days
  is_active (BOOLEAN) - whether customer is active
  address (TEXT)
  phone (TEXT)
  created_at (TIMESTAMP)
  updated_at (TIMESTAMP)
Relationships:
  A customer can have children (child organizations) via parent_id
  parent_id references the same customer table (self-referential)
""",
    'branch': """
Table: branch
Columns:
  id (INTEGER, PK)
  alias_id (VARCHAR, unique)
  name (VARCHAR) - branch name
  parent_id (INTEGER, FK -> branch.id) - parent branch
  branch_type (INTEGER) - 1=Head Office, 2=Branch
""",
    'credit_invoice': """
Table: credit_invoice (alias: ci)
Columns:
  id (INTEGER, PK)
  alias_id (VARCHAR, unique)
  branch_id (INTEGER, FK -> branch.id) - branch this invoice belongs to
  customer_id (INTEGER, FK -> customer.id) - child customer this invoice is for
  grn (TEXT) - goods received note number
  transaction_date (DATE) - invoice date
  delivery_man (TEXT)
  remarks (TEXT)
  sales_amount (DECIMAL(18,4)) - total sales amount
  sales_return (DECIMAL(18,4)) - sales return amount
  payment_grace_days (INTEGER) - grace period for this invoice (copied from customer)
  payment_id (INTEGER, FK -> payment.id, NULLABLE) - linked payment when paid
  status (BOOLEAN) - invoice status
  invoice_image (TEXT) - path to uploaded invoice image
  updated_at (TIMESTAMP)
  updated_by (INTEGER, FK -> auth_user.id)
  version (INTEGER) - optimistic locking version
Indexes:
  idx_ci_transaction_date (transaction_date)
  idx_ci_branch_date (branch_id, transaction_date)
  idx_ci_customer_date (customer_id, transaction_date)
  idx_ci_payment_date (payment_id, transaction_date)
  idx_ci_updated_at (updated_at DESC)
Note: net_due = sales_amount - sales_return (computed)
""",
    'payment': """
Table: payment (alias: p)
Columns:
  id (INTEGER, PK)
  alias_id (VARCHAR, unique)
  branch_id (INTEGER, FK -> branch.id)
  customer_id (INTEGER, FK -> customer.id) - parent customer
  received_date (DATE) - date payment was received
  claim_amount (DECIMAL(18,4)) - total claim amount in this payment
  cash_equivalent_amount (DECIMAL(18,4)) - total cash/cheque amount
  total_amount (DECIMAL(18,4)) - total payment amount
  shortage_amount (DECIMAL(18,4)) - shortage or excess amount
  updated_at (TIMESTAMP)
  updated_by (INTEGER, FK -> auth_user.id)
  version (INTEGER)
Relationships:
  payment.invoice_set -> CreditInvoice records linked to this payment (one-to-many)
  payment.paymentdetails_set -> PaymentDetails records (one-to-many)
""",
    'payment_details': """
Table: payment_details (alias: pd)
Columns:
  id (INTEGER, PK)
  alias_id (VARCHAR, unique)
  branch_id (INTEGER, FK -> branch.id)
  id_number (VARCHAR) - instrument serial number (branch-unique)
  payment_id (INTEGER, FK -> payment.id)
  payment_instrument_id (INTEGER, FK -> payment_instrument.id)
  detail (TEXT) - remarks/description
  amount (DECIMAL(18,4)) - instrument amount
Relationships:
  payment_details.payment_detail -> Claim (one-to-one, only for claim instruments)
""",
    'payment_instrument': """
Table: payment_instrument (alias: pi)
Columns:
  id (INTEGER, PK)
  branch_id (INTEGER, FK -> branch.id)
  serial_no (INTEGER)
  instrument_type_id (INTEGER, FK -> payment_instrument_type.id)
  instrument_name (TEXT) - name of the instrument
  is_active (BOOLEAN)
  updated_at (TIMESTAMP)
  updated_by (INTEGER, FK -> auth_user.id)
  version (INTEGER)
""",
    'payment_instrument_type': """
Table: payment_instrument_type (alias: pit)
Columns:
  id (INTEGER, PK)
  branch_id (INTEGER, FK -> branch.id)
  serial_no (INTEGER) - 1=Cash Equivalent, 2=Cash, 3=Claim
  type_name (TEXT) - 'Cheque', 'Cash', 'Claim', etc.
  is_cash_equivalent (BOOLEAN) - TRUE if cash equivalent
  prefix (VARCHAR(2)) - ID number prefix (e.g., 'CQ', 'CH', 'CL')
  last_number (INTEGER) - last auto-generated number
  auto_number (BOOLEAN) - whether numbers are auto-generated
""",
    'claim': """
Table: claim (alias: cl)
Columns:
  id (INTEGER, PK)
  alias_id (VARCHAR, unique)
  branch_id (INTEGER, FK -> branch.id)
  payment_details_id (INTEGER, FK -> payment_details.id, unique)
  submitted_date (DATE) - date claim was submitted to supplier
  refund_amount (DECIMAL(18,4)) - amount refunded by supplier
  refund_date (DATE) - date refund was received
  remarks (TEXT)
  updated_at (TIMESTAMP)
  updated_by (INTEGER, FK -> auth_user.id)
  version (INTEGER)
Computed: remaining_amount = payment_details.amount - refund_amount
""",
}