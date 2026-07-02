"""Generate the three sample corporate PDFs used by the evaluation golden set.

Run once before executing the eval suite:
    python scripts/create_sample_docs.py

Creates:
    data/employee_handbook.pdf      (40 pages)
    data/financial_procedures.pdf   (18 pages)
    data/it_policy.pdf              (11 pages)
"""

from pathlib import Path

import fitz  # PyMuPDF

PAGE_CONTENT: dict[str, dict[int, tuple[str, str]]] = {
    "employee_handbook.pdf": {
        1: (
            "1. Introduction and Purpose",
            "This Employee Handbook ('Handbook') has been prepared to provide information "
            "about our company's policies, procedures, and benefits. The purpose of this handbook "
            "is to provide guidelines, policies, and procedures that govern employment at the "
            "organization, helping employees understand their rights, responsibilities, and the "
            "company's expectations.\n\n"
            "This Handbook applies to all full-time and part-time employees. The company reserves "
            "the right to amend, modify, or revoke any policy at any time. By accepting employment, "
            "you agree to read, understand, and comply with all guidelines set forth herein. "
            "Questions should be directed to your HR representative.",
        ),
        5: (
            "5. Resignation and Termination",
            "5.1 Voluntary Resignation\n\n"
            "Employees who choose to leave the company voluntarily are expected to provide "
            "reasonable notice. Employees are expected to provide at least two weeks written notice "
            "before resigning from their position. This notice should be submitted in writing to "
            "both your direct manager and the HR department.\n\n"
            "Senior management positions (Director level and above) are expected to provide a "
            "minimum of four weeks written notice.\n\n"
            "5.2 Notice Period Conduct\n\n"
            "During the notice period, employees must maintain regular duties, assist with the "
            "transition of responsibilities, and return all company property in good condition.",
        ),
        8: (
            "8. Working Hours and Attendance",
            "8.1 Standard Working Hours\n\n"
            "The standard working week is 40 hours, typically Monday through Friday.\n\n"
            "8.2 Core Hours\n\n"
            "Core working hours are from 10:00 AM to 3:00 PM local time, during which all "
            "employees must be available for meetings and collaboration. Outside of these core "
            "hours, employees have flexibility in scheduling their working day, subject to "
            "operational requirements and manager approval.\n\n"
            "8.3 Flexible Working\n\n"
            "The company supports flexible working arrangements where operationally feasible. "
            "All arrangements must be agreed in advance with your line manager.",
        ),
        12: (
            "12. Annual Leave",
            "12.1 Leave Entitlement\n\n"
            "Full-time employees are entitled to 20 days of paid annual leave per year, which "
            "increases to 25 days after five years of service. Part-time employees receive leave "
            "on a pro-rated basis.\n\n"
            "12.2 Leave Year\n\n"
            "The leave year runs from January 1st to December 31st. Leave must be taken within "
            "the leave year in which it is accrued.\n\n"
            "12.3 Booking Leave\n\n"
            "All annual leave requests must be submitted through the HR portal with a minimum of "
            "two weeks advance notice for periods of one week or less, and four weeks for longer "
            "periods. Approval is subject to business requirements.",
        ),
        15: (
            "15. Remote Work Policy",
            "15.1 Eligibility\n\n"
            "Eligibility for remote work is determined by role type, performance record, and "
            "business needs. Not all roles are suitable for remote working.\n\n"
            "15.2 Remote Work Allowance\n\n"
            "Employees may work remotely up to three days per week with manager approval, "
            "provided they maintain productivity and attend required in-person meetings. "
            "All remote working arrangements must be agreed in advance with your line manager.\n\n"
            "15.3 Equipment and Security\n\n"
            "Employees working remotely must use company-issued equipment and ensure their "
            "internet connection is secure. Confidential information must not be visible to "
            "or accessible by others.",
        ),
        18: (
            "18. Parental Leave",
            "18.1 Eligibility\n\n"
            "All employees who have been employed for a minimum of 12 months are eligible to "
            "apply for parental leave.\n\n"
            "18.2 Notification Requirements\n\n"
            "Employees must notify HR at least eight weeks before the expected leave start date "
            "and submit a formal parental leave request form for manager and HR approval. "
            "This notification should include the expected start date, anticipated duration, "
            "and any requested adjustments to working arrangements upon return.\n\n"
            "18.3 Duration and Pay\n\n"
            "Statutory parental leave pay applies in all cases, with enhanced pay subject to "
            "length of service.",
        ),
        20: (
            "20. Disciplinary Procedures",
            "20.1 Purpose\n\n"
            "The disciplinary procedure is designed to help and encourage employees to achieve "
            "and maintain standards of conduct.\n\n"
            "20.2 Progressive Disciplinary Steps\n\n"
            "Disciplinary procedures follow a progressive approach: verbal warning, written "
            "warning, final written warning, and termination, depending on the severity of the "
            "misconduct. The company reserves the right to skip steps in cases of gross misconduct.\n\n"
            "20.3 Gross Misconduct\n\n"
            "Certain offenses are considered gross misconduct and may result in immediate "
            "termination without prior warnings, including theft, fraud, violence, and serious "
            "data breaches.\n\n"
            "20.4 Right of Appeal\n\n"
            "Employees may appeal any disciplinary decision within five business days of "
            "receiving written notice of the outcome.",
        ),
        22: (
            "22. Workplace Harassment and Discrimination Policy",
            "22.1 Policy Statement\n\n"
            "The company has a zero-tolerance policy for harassment of any kind. We are committed "
            "to providing a work environment free of harassment, discrimination, and hostile "
            "conduct. Employees who experience or witness harassment should report it to HR "
            "immediately. All reports are investigated confidentially.\n\n"
            "22.2 Definition of Harassment\n\n"
            "Harassment includes any unwelcome conduct based on a protected characteristic "
            "(including sex, race, religion, disability, age, or sexual orientation).\n\n"
            "22.3 Reporting Procedure\n\n"
            "Complaints should be made to your HR Business Partner or via the anonymous "
            "reporting hotline. All complaints will be treated seriously and investigated promptly.",
        ),
        25: (
            "25. IT Support and Resources",
            "25.1 Help Desk Services\n\n"
            "The IT department provides technical support for all company-issued hardware and "
            "software. Employees should contact the IT Help Desk by submitting a ticket through "
            "the internal portal or calling the support hotline during business hours "
            "(Monday to Friday, 8:00 AM to 6:00 PM).\n\n"
            "25.2 Response Times\n\n"
            "The IT Help Desk aims to respond to priority issues within four business hours "
            "and standard requests within one business day.\n\n"
            "25.3 Self-Service Resources\n\n"
            "A knowledge base of common solutions and FAQs is available on the company intranet. "
            "Employees are encouraged to consult it before submitting a ticket.",
        ),
        30: (
            "30. Conflicts of Interest",
            "30.1 Policy\n\n"
            "Employees must disclose any potential conflicts of interest to their manager and HR "
            "in writing. Outside employment or financial interests that conflict with company "
            "duties are prohibited without written approval.\n\n"
            "30.2 What Constitutes a Conflict\n\n"
            "A conflict of interest arises when an employee's personal interests could influence, "
            "or appear to influence, their professional judgment. This includes financial interests "
            "in competitors, suppliers, or clients, and personal relationships with vendors.\n\n"
            "30.3 Disclosure Requirements\n\n"
            "All potential conflicts must be declared using the Conflict of Interest Disclosure "
            "Form, submitted upon employment and updated annually.\n\n"
            "30.4 Consequences\n\n"
            "Failure to disclose may result in disciplinary action, up to and including termination.",
        ),
        35: (
            "35. Performance Management",
            "35.1 Review Cycle\n\n"
            "Performance reviews are conducted annually in December, with a mid-year check-in "
            "in June. Reviews involve self-assessment, manager evaluation, and goal-setting "
            "for the following year.\n\n"
            "35.2 Performance Rating Scale\n\n"
            "Performance is rated on a five-point scale: Exceptional, Exceeds Expectations, "
            "Meets Expectations, Needs Improvement, and Unsatisfactory.\n\n"
            "35.3 Goal-Setting\n\n"
            "Goals are set using the SMART framework and should align with both team and "
            "company objectives.",
        ),
        40: (
            "40. Benefits Overview",
            "40.1 Health Insurance\n\n"
            "The health insurance plan covers medical, dental, and vision care for employees "
            "and their dependents, with the company covering 80% of premiums for employees "
            "and 60% for dependents. Employees may choose from three plan tiers: Standard, "
            "Enhanced, and Premier.\n\n"
            "40.2 Enrollment\n\n"
            "New employees must enroll within 30 days of their start date. Changes may only "
            "be made during the annual open enrollment period or following a qualifying life event.\n\n"
            "40.3 Dental and Vision\n\n"
            "Dental coverage includes two annual cleanings, x-rays, and restorative procedures. "
            "Vision coverage includes an annual eye examination and a frames/contacts allowance.",
        ),
    },
    "financial_procedures.pdf": {
        2: (
            "2. Financial Calendar",
            "2.1 Fiscal Year\n\n"
            "The company's fiscal year runs from January 1 to December 31. All financial "
            "reporting, budgeting, and planning activities are aligned to this calendar year.\n\n"
            "2.2 Reporting Deadlines\n\n"
            "Monthly management accounts must be finalized within ten business days of month-end. "
            "Quarterly reports must be submitted to the Board within fifteen business days. "
            "The annual report must be filed within ninety days of fiscal year-end.\n\n"
            "2.3 Budget Cycle\n\n"
            "The annual budget cycle commences in September. Departmental budgets must be "
            "submitted to Finance by November 1st for Board approval before December 31st.",
        ),
        3: (
            "3. Monthly Financial Reporting",
            "3.1 Report Components\n\n"
            "Monthly financial reports must include revenue, expenses, EBITDA, cash flow "
            "statement, accounts receivable aging, and a variance analysis comparing actuals "
            "to budget. Each component should be presented for the current month and year-to-date.\n\n"
            "3.2 Revenue Section\n\n"
            "Revenue must be broken down by business unit, product line, and geography. "
            "Deferred revenue and adjustments must be separately disclosed with explanatory notes.\n\n"
            "3.3 Variance Analysis\n\n"
            "Variance analysis must explain all material differences between actual results "
            "and the approved budget.",
        ),
        5: (
            "5. Financial Systems",
            "5.1 Enterprise Resource Planning\n\n"
            "The company uses SAP for its enterprise resource planning and financial reporting. "
            "All financial transactions must be recorded in SAP within two business days of "
            "occurrence. Employees requiring access must submit an access request to Finance Systems.\n\n"
            "5.2 Data Visualization\n\n"
            "Tableau is used for data visualization and executive dashboards. Tableau is "
            "connected to the SAP data warehouse and refreshes on a nightly basis.\n\n"
            "5.3 Expense Management\n\n"
            "All employee expense claims must be submitted through the Concur expense "
            "management system.",
        ),
        7: (
            "7. Capital Expenditure Policy",
            "7.1 Definition\n\n"
            "Capital expenditure (CapEx) refers to funds used to acquire, upgrade, or maintain "
            "physical assets that will provide benefit for more than one year.\n\n"
            "7.2 Approval Thresholds\n\n"
            "Capital expenditures above $10,000 require VP approval; those above $50,000 require "
            "CFO approval; and those above $250,000 require Board approval. All CapEx requests "
            "must be submitted using the Capital Expenditure Request Form.\n\n"
            "7.3 Business Case Requirement\n\n"
            "All CapEx requests above $10,000 must be accompanied by a business case including "
            "projected return on investment, payback period, and alternatives considered.",
        ),
        8: (
            "8. Budget Management",
            "8.1 Variance Reporting\n\n"
            "Budget variances exceeding 5% or $5,000 (whichever is greater) must be reported "
            "to the department head with a written explanation within five business days of "
            "month-end close. The explanation must include the root cause, corrective actions "
            "planned, and a revised full-year forecast.\n\n"
            "8.2 Re-forecasting\n\n"
            "Departments are required to submit a revised forecast at the end of Q1, Q2, and Q3.\n\n"
            "8.3 Budget Amendments\n\n"
            "Formal budget amendments above $100,000 require CFO approval.",
        ),
        10: (
            "10. Expense Reimbursement",
            "10.1 Submission Requirements\n\n"
            "Expense reports must be submitted within 30 days of incurring the expense, along "
            "with original receipts for any expenditure over $25. Late submissions may result "
            "in the expense not being reimbursed.\n\n"
            "10.2 Eligible Expenses\n\n"
            "The company will reimburse reasonable and necessary business expenses including "
            "travel, accommodation, meals during business travel, and client entertainment.\n\n"
            "10.3 Non-Reimbursable Expenses\n\n"
            "Personal expenses, alcohol (unless part of approved client entertainment), "
            "and parking fines are not reimbursable without prior VP approval.",
        ),
        12: (
            "12. Accounts Payable and Vendor Management",
            "12.1 Standard Payment Terms\n\n"
            "Standard vendor payment terms are Net 30 from invoice receipt. Early payment "
            "discounts may be negotiated for Net 10 or Net 15 terms. All deviations from "
            "standard payment terms must be approved by the CFO in writing.\n\n"
            "12.2 Invoice Processing\n\n"
            "All invoices must be matched to an approved purchase order before payment. "
            "Invoices without a valid purchase order number will be returned to the vendor.\n\n"
            "12.3 Vendor Onboarding\n\n"
            "New vendors must complete the Vendor Registration Form and pass compliance "
            "checks before any purchase orders can be issued.",
        ),
        14: (
            "14. Vendor Dispute Resolution",
            "14.1 Escalation Process\n\n"
            "Unresolved vendor disputes should first be escalated to the Procurement Manager, "
            "then to Legal if unresolved within 30 days, and finally to the CFO if legal "
            "negotiation fails.\n\n"
            "14.2 Dispute Documentation\n\n"
            "All vendor disputes must be documented in writing, including the nature of the "
            "dispute, amounts in question, communications to date, and proposed resolution.\n\n"
            "14.3 Payment Withholding\n\n"
            "Payment for disputed invoices may be withheld pending resolution, provided the "
            "vendor has been notified in writing within 10 business days.",
        ),
        15: (
            "15. Audit and Compliance",
            "15.1 Accounting Standards\n\n"
            "The company follows Generally Accepted Accounting Principles (GAAP) and undergoes "
            "an annual external audit by a certified public accounting firm. Significant "
            "departures from GAAP must be disclosed and approved by the Board Audit Committee.\n\n"
            "15.2 External Audit\n\n"
            "The external auditor is appointed annually by the Board. All finance staff must "
            "cooperate fully and provide requested documentation within agreed timescales.\n\n"
            "15.3 Internal Audit\n\n"
            "The Internal Audit function reports directly to the Audit Committee and conducts "
            "periodic reviews of financial controls.",
        ),
        18: (
            "18. Document Retention and Records Management",
            "18.1 Retention Requirements\n\n"
            "Financial records must be retained for a minimum of seven years in accordance "
            "with regulatory requirements and the company's document retention policy. "
            "This includes general ledger records, accounts payable and receivable records, "
            "payroll records, and all financial statements.\n\n"
            "18.2 Electronic Records\n\n"
            "Electronic financial records must be stored in the company's approved document "
            "management system and backed up daily.\n\n"
            "18.3 Destruction of Records\n\n"
            "Records may only be destroyed after the retention period has expired and with "
            "written approval from the Legal and Finance departments.",
        ),
    },
    "it_policy.pdf": {
        4: (
            "4. Physical Security",
            "4.1 Server Room Access Controls\n\n"
            "Access to server rooms requires Level 3 security clearance, a valid employee badge, "
            "and must be logged in the access management system. Access is granted on a "
            "need-to-access basis and must be authorized by the IT Security Manager.\n\n"
            "4.2 Visitor Access\n\n"
            "Visitors to the data center or server rooms must be accompanied by an authorized "
            "employee at all times and logged in the visitor management system.\n\n"
            "4.3 Access Review\n\n"
            "Server room access rights are reviewed quarterly. Access that is no longer required "
            "must be revoked within 24 hours of any change in role or employment status.",
        ),
        6: (
            "6. Password and Authentication Policy",
            "6.1 Password Requirements\n\n"
            "Employees must change their passwords every 90 days. Passwords must be at least "
            "12 characters and include uppercase, lowercase, numbers, and special characters. "
            "Passwords must not contain the employee's name or commonly used words.\n\n"
            "6.2 Multi-Factor Authentication\n\n"
            "Multi-factor authentication (MFA) is mandatory for all externally accessible "
            "systems including email, VPN, and cloud applications.\n\n"
            "6.3 Password Sharing\n\n"
            "Sharing of passwords is strictly prohibited. Each employee must have a unique "
            "password for each system. Approved password managers may be used.",
        ),
        7: (
            "7. Software Management Policy",
            "7.1 Approved Software\n\n"
            "Employees may only install software that has been pre-approved by IT and is on "
            "the company's approved software list. Unauthorized software installation is a "
            "disciplinary offense. The approved software list is available on the IT intranet "
            "page and is updated quarterly.\n\n"
            "7.2 Software Requests\n\n"
            "Requests for new software must be submitted via the IT Help Desk portal. "
            "The IT Security team will evaluate the request within five business days.\n\n"
            "7.3 License Compliance\n\n"
            "All software must be properly licensed. Unlicensed software should be reported "
            "to IT immediately.",
        ),
        9: (
            "9. Bring Your Own Device (BYOD) Policy",
            "9.1 Policy Scope\n\n"
            "This policy applies to personal devices (smartphones, tablets, laptops) used to "
            "access company data, email, or systems.\n\n"
            "9.2 Enrollment Requirements\n\n"
            "Personal devices may be used for work purposes only after enrolling in the Mobile "
            "Device Management (MDM) program and agreeing to the BYOD policy terms. "
            "Enrollment must be completed with the IT department before any work-related use.\n\n"
            "9.3 Security Requirements\n\n"
            "Enrolled devices must maintain screen lock with a PIN of at least 6 digits, "
            "have encryption enabled, and have the company's MDM profile installed. "
            "The company reserves the right to remotely wipe enrolled devices if lost, stolen, "
            "or upon termination of employment.",
        ),
        11: (
            "11. Data Breach Response",
            "11.1 Reporting a Suspected Breach\n\n"
            "Employees who suspect a data breach must immediately notify the IT Security team "
            "via the security hotline and their direct manager. They should not attempt to "
            "investigate or remediate the issue themselves. Prompt reporting is essential to "
            "limit the impact of a breach.\n\n"
            "11.2 What Constitutes a Breach\n\n"
            "A data breach is any incident where unauthorized individuals may have gained "
            "access to, or disclosed, company or personal data.\n\n"
            "11.3 Response Process\n\n"
            "The IT Security team will assess, contain, and notify affected parties. "
            "Regulatory notification timelines (typically 72 hours for GDPR) must be met.",
        ),
    },
}


def _create_pdf(out_path: Path, pages: dict[int, tuple[str, str]]) -> None:
    doc = fitz.open()
    max_page = max(pages.keys())
    font_bold = "helv"
    font_regular = "helv"

    for page_num in range(1, max_page + 1):
        page = doc.new_page(width=595, height=842)

        # Page number footer
        page.insert_text(
            (50, 820), f"Page {page_num}", fontsize=8,
            fontname=font_regular, color=(0.5, 0.5, 0.5),
        )

        if page_num in pages:
            heading, body = pages[page_num]
            # Heading
            page.insert_text(
                (50, 70), heading, fontsize=14,
                fontname=font_bold, color=(0.1, 0.1, 0.3),
            )
            # Body text with word-wrap
            rect = fitz.Rect(50, 100, 545, 790)
            page.insert_textbox(
                rect, body, fontsize=10.5,
                fontname=font_regular, color=(0.1, 0.1, 0.1),
            )
        else:
            # Intentionally blank filler page
            page.insert_text(
                (50, 420), "[This page intentionally left blank]",
                fontsize=10, fontname=font_regular, color=(0.6, 0.6, 0.6),
            )

    doc.save(str(out_path))
    print(f"  Created {out_path.name} ({max_page} pages, {out_path.stat().st_size // 1024} KB)")


def main() -> None:
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    print("Generating sample corporate documents for the evaluation golden set...\n")
    for filename, pages in PAGE_CONTENT.items():
        _create_pdf(data_dir / filename, pages)

    print(f"\nDone. 3 PDFs written to {data_dir}/")
    print("Next: run `python -m eval.run_eval` to evaluate the system against these documents.")


if __name__ == "__main__":
    main()
