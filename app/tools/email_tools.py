"""
Email Automation — Power Automate HTTP Trigger
===============================================
LangGraph email_notify_node calls send_email_via_power_automate().
Power Automate then sends email via Office 365 / Outlook.

Setup in Power Automate:
  1. New flow → "When an HTTP request is received" trigger
  2. Copy the generated webhook URL → settings.POWER_AUTOMATE_WEBHOOK_URL
  3. Add "Send an email (V2)" action (Office 365 Outlook)
  4. Map: To=body.recipients, Subject=body.subject, Body=body.body
"""
from __future__ import annotations

import httpx
import structlog

from app.config import settings

logger = structlog.get_logger("app.email")


async def send_email_via_power_automate(
    recipients: list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    importance: str = "Normal",   # Low | Normal | High
) -> bool:
    """
    POST to Power Automate HTTP trigger which sends email via Outlook 365.
    Returns True on success, False on failure (non-raising — email is best-effort).
    """
    if not settings.POWER_AUTOMATE_WEBHOOK_URL:
        # Dev/test: log only (no actual send)
        logger.debug("email_mock", recipients=recipients, subject=subject)
        return True

    payload = {
        "recipients": recipients,
        "cc": cc or [],
        "subject": subject,
        "body": body,
        "importance": importance,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                settings.POWER_AUTOMATE_WEBHOOK_URL,
                json=payload,
            )
            response.raise_for_status()
            return True
        except (httpx.HTTPStatusError, httpx.RequestError) as exc:
            logger.error("email_send_failed", exc_info=exc, recipients=recipients)
            return False


# ── Pre-built email templates ─────────────────────────────────────────────────

def leave_request_email(employee_name: str, manager_email: str,
                         leave_type: str, start: str, end: str,
                         days: float, leave_id: str, approve_url: str) -> dict:
    return {
        "recipients": [manager_email],
        "subject": f"Leave Request — {employee_name} ({days} day(s))",
        "body": f"""
Hi,

<b>{employee_name}</b> has applied for <b>{leave_type}</b> leave:
<ul>
  <li>From: {start}</li>
  <li>To: {end}</li>
  <li>Duration: {days} business day(s)</li>
</ul>

<a href="{approve_url}">Click here to approve or reject</a>

This is an automated message from the Enterprise AI Copilot.
        """,
    }


def leave_approval_email(employee_email: str, decision: str,
                          leave_type: str, start: str, end: str,
                          reviewer_note: str = "") -> dict:
    status_word = "Approved ✅" if decision == "approved" else "Rejected ❌"
    return {
        "recipients": [employee_email],
        "subject": f"Your Leave Request has been {status_word}",
        "body": f"""
Hi,

Your <b>{leave_type}</b> leave request ({start} to {end}) has been <b>{decision}</b>.

{f'Note from reviewer: {reviewer_note}' if reviewer_note else ''}

This is an automated message from the Enterprise AI Copilot.
        """,
    }


def ticket_created_email(employee_email: str, ticket_no: str,
                          subject: str, priority: str) -> dict:
    return {
        "recipients": [employee_email],
        "subject": f"IT Ticket Created — {ticket_no}",
        "body": f"""
Hi,

Your IT support ticket has been created:
<ul>
  <li>Ticket No: <b>{ticket_no}</b></li>
  <li>Subject: {subject}</li>
  <li>Priority: {priority.upper()}</li>
  <li>Status: Open</li>
</ul>

The IT team will respond based on priority SLA. You'll receive updates via email.

This is an automated message from the Enterprise AI Copilot.
        """,
    }


def reimbursement_submitted_email(employee_email: str, claim_no: str,
                                   amount: float, currency: str) -> dict:
    return {
        "recipients": [employee_email],
        "subject": f"Reimbursement Claim Submitted — {claim_no}",
        "body": f"""
Hi,

Your reimbursement claim has been submitted:
<ul>
  <li>Claim No: <b>{claim_no}</b></li>
  <li>Amount: {currency} {amount:,.2f}</li>
  <li>Status: Under Review</li>
</ul>

The Finance team will process it within 5 business days.

This is an automated message from the Enterprise AI Copilot.
        """,
    }