# Legal-Memo Skill

## Overview
Generate IRAC-format legal research memos as professional Word documents with proper Bluebook citation formatting, disclaimer injection, and citation verification via CourtListener API.

## Trigger Command
`/memo [topic_or_question]`

## Purpose
Produces professional legal memoranda for research purposes that follow industry-standard IRAC analytical structure, include verified case citations, and contain appropriate legal disclaimers.

## When to Invoke
- When legal research on a specific topic or question is needed
- For memo-to-file documentation of legal analysis
- For internal reference on legal issues
- For briefing partners or clients on legal matters
- When case citations need to be verified before finalizing analysis

## Who Can Use
- Licensed attorneys only (appropriate disclaimers and expertise required)
- Law firm staff under attorney supervision
- Legal consultants with proper credentials
- Not for use by non-lawyers for legal advice

## Input Requirements

**Required Parameter:** `[topic_or_question]`
- Legal topic, question, or issue to research
- Examples:
  - `/memo Contract breach remedies under UCC`
  - `/memo Defamation elements in social media posts`
  - `/memo Non-compete agreements enforceability`
  - `/memo Employment discrimination - hostile work environment`
  - `/memo Intellectual property infringement standard`

**Optional Parameters:**
- Jurisdiction (if specific state/federal law applies)
- Applicable body of law (state, federal, common law, statute)
- Specific statutes or cases to reference
- Opposing arguments to address
- Client facts or scenario (for applied analysis)

## Memo Structure & Format

All memos follow IRAC structure with additional professional sections:

### Section 1: Header Information

**To:** [Recipient name and title]
**From:** Dewey Cheatem, Esq.
**Date:** [Current date in format: February 8, 2025]
**Re:** [Topic slug: topic-in-title-case]

**Header Format Example:**
```
MEMORANDUM

TO:         [Recipient or "File"]
FROM:       Dewey Cheatem, Esq.
DATE:       February 8, 2025
RE:         Employment Discrimination - Hostile Work Environment Claims
```

### Section 2: Executive Summary

**Purpose:** One-page summary of legal issue, applicable law, and conclusion

**Content Requirements:**
- 1 paragraph describing the legal question
- 1 paragraph summarizing relevant law
- 1 paragraph stating conclusion/answer
- Total: 250-400 words
- No citations needed in executive summary
- Written in accessible language (not highly technical)

**Example:**
```
EXECUTIVE SUMMARY

This memo addresses the legal standards for establishing a hostile work
environment claim under Title VII of the Civil Rights Act. The issue is
whether the alleged conduct—[brief facts]—rises to the level of actionable
harassment under federal employment law.

Under Title VII, a hostile work environment exists when unwelcome conduct
is based on a protected characteristic, is severe or pervasive, and affects
employment or the work environment. Courts apply an objective reasonableness
test to determine if the conduct was sufficiently severe or pervasive.

Based on [jurisdiction] precedent and the facts presented, [conclusion about
whether conduct likely constitutes hostile work environment]. This analysis
assumes [relevant assumptions about evidence/jurisdiction].
```

### Section 3: IRAC Analysis (one per distinct issue)

For each discrete legal issue, include a complete IRAC section:

#### 3.1 ISSUE Subsection

**Format:** "Whether [plaintiff/party] can establish [legal claim] under [applicable law]"

**Content Requirements:**
- 1-2 sentences maximum
- State legal question clearly
- Reference applicable jurisdiction and law
- Do not include analysis

**Example:**
```
ISSUE

Whether an employer can be held liable for age discrimination under the Age
Discrimination in Employment Act (ADEA), 29 U.S.C. § 623, when its reduction
in force disproportionately affected employees over 40 years old.
```

#### 3.2 RULE Subsection

**Purpose:** Explain applicable law, including statutes, case precedent, and common law principles

**Content Requirements:**
- Cite all statutes with full citations (Bluebook format)
- Include 3-5 landmark cases per issue
- Explain each legal standard with authority
- Use block quotes sparingly (only for key legal language)
- Organize by legal standard (first element, second element, etc.)

**Citation Format - Bluebook Standard:**

**For Cases:**
```
[Case Name], [Volume] [Reporter] [Page], [Year]
```

Examples:
```
Miranda v. Arizona, 384 U.S. 436 (1966)
Smith v. Jones, 256 F.3d 789 (7th Cir. 2001)
Doe v. State, 123 N.E.2d 456 (Ill. App. 2020)
```

**For Statutes:**
```
[Title] U.S.C. § [Section]
```

Examples:
```
42 U.S.C. § 1983 (Civil rights actions)
Title VII of the Civil Rights Act, 42 U.S.C. § 2000e
```

**For Regulations:**
```
[Volume] C.F.R. § [Section]
```

Example:
```
29 C.F.R. § 1602.14 (EEOC regulations)
```

**For State Statutes:**
```
[State Abbrev.] [Code/Stat.] § [Section] ([Year])
```

Examples:
```
Cal. Civ. Code § 1670 (West 2025)
Tex. Bus. & Com. Code Ann. § 9.501 (West 2025)
```

**Rule Section Structure:**

1. Introduce primary statute or common law principle
2. Break down each element of the legal test
3. Cite controlling case law for each element
4. Explain how courts interpret ambiguous standards
5. Note any recent statutory changes or case developments
6. Discuss relevant secondary authority if appropriate

**Example Rule Section:**

```
RULE

To establish a claim for breach of contract, a plaintiff must show:
(1) the existence of a valid contract; (2) performance or tender of
performance by the plaintiff; (3) breach by the defendant; and (4) damages
resulting from the breach. See Smith v. Jones, 256 F.3d 789 (7th Cir. 2001).

The Formation of a Valid Contract

A valid contract requires mutual assent to essential terms: offer, acceptance,
and consideration. See Williams v. Walker-Thomas Furniture Co., 350 F.2d 445
(D.C. Cir. 1965). The parties must intend to be legally bound, and the terms
must be sufficiently definite to be enforceable. Id. at 450.

Under the Uniform Commercial Code (UCC), § 2-204(1), a contract for the sale
of goods is formed in any manner sufficient to show agreement, and need not be
found in a single document. 2 U.C.C. § 2-204(1) (2022). The terms may be
supplied by course of dealing, course of performance, or usage of trade. Id.
§ 2-202.

Proof of Performance

The plaintiff must show either actual performance or tender of performance
(offer to perform when due). See Brown v. Green, 199 F.3d 100 (3d Cir. 1998).
Tender requires the plaintiff to do or offer to do all things the contract
required. Id. at 105. For installment contracts, failure to pay one installment
may not constitute material breach unless the failure substantially impairs the
value of the contract. 2 U.C.C. § 2-612(2).
```

#### 3.3 APPLICATION Subsection

**Purpose:** Apply law to the facts of the specific case

**Content Requirements:**
- State relevant facts (assume facts provided or state assumptions)
- Apply each legal element to the facts
- Use same subheadings as Rule section for clarity
- Discuss how controlling precedent applies to these specific facts
- Acknowledge contrary arguments
- Explain why the law supports the conclusion

**Example Application Section:**

```
APPLICATION

Application of the contract formation rules to these facts indicates that a
valid contract likely existed. The parties exchanged clear communications about
the essential terms: [describe facts]. Under Williams, the parties demonstrated
mutual assent when [describe conduct showing agreement]. The terms were
sufficiently definite: price was $X, delivery was on [date], and the goods
were described as [description].

The defendant argues that the email exchange was preliminary negotiation only,
not a binding offer and acceptance. However, under the Uniform Commercial Code
and the approach adopted in this jurisdiction, the language used ("will sell,"
"confirmed purchase") indicates present commitment, not future negotiation.
Compare Brown v. Green, 199 F.3d 100 (finding binding commitment), with
Martinez v. Lopez, 188 F.3d 75 (finding preliminary discussion only).

Performance and Tender

Plaintiff performed by [describe performance], satisfying the requirement that
he tender performance prior to defendant's obligation. [Cite supporting case
showing similar performance sufficient]. Defendant does not dispute that
plaintiff performed his obligations under the contract.

Breach

Defendant's failure to [describe breach] constitutes material breach under these
facts. The breach goes to the heart of the contract because [explain why material].
Defendant provides no valid excuse for non-performance. Plaintiff was not required
to accept the non-conforming [good/service] under § 2-601.

Damages

Plaintiff can recover [describe damages calculations] based on standard
contract remedies. [Cite case establishing damages calculation].
```

#### 3.4 CONCLUSION Subsection

**Purpose:** State conclusion for this specific issue

**Content Requirements:**
- 1-2 sentences answering the Issue stated above
- Can include probability/likelihood language if appropriate
- Reference key facts and law supporting conclusion
- Do not repeat entire analysis

**Example:**

```
CONCLUSION

Plaintiff can likely establish breach of contract. The parties formed a valid
contract through their email exchange and order confirmation, plaintiff
performed by [X], and defendant's failure to [Y] constitutes material breach
entitling plaintiff to damages in the amount of [Z].
```

### Section 4: Conclusion

**Purpose:** Overall conclusion addressing all issues

**Content Requirements:**
- 1-2 paragraphs
- Answer the original research question
- Summarize key findings from each IRAC section
- Provide practical recommendation or next steps if applicable
- Acknowledge any uncertainties or need for further research

**Example:**

```
CONCLUSION

Based on the foregoing analysis, [party] likely has a viable claim for [cause
of action]. While not certain, the controlling law and available facts support
this conclusion. The strongest argument is [X]. The weakest point is [Y],
though case law suggests [mitigating factor]. Further investigation of [specific
fact or law] would strengthen the analysis. We recommend proceeding with
[action] and preparing evidence regarding [key facts].
```

### Section 5: Disclaimer

**Required Legal Disclaimer** - MUST be included on every memo

**Disclaimer Text (auto-appended):**

```
DISCLAIMER

This memorandum is for informational purposes only and does not constitute
legal advice. This memorandum is based on the facts and law as presented
herein and may not be relied upon for legal advice without independent
verification of all cited authorities and further discussion with counsel.
The analysis provided herein reflects current law as of the date of this
memorandum and may not account for subsequent statutory amendments or case
developments.

Any conclusions or recommendations are offered for discussion purposes only
and should not be construed as legal advice. The recipient of this memorandum
should seek independent counsel before taking any action based on the
analysis herein.

This memorandum is attorney work product and is intended for use by the
recipient and counsel only. It should not be disclosed to third parties
without the express consent of the author.
```

### Section 6: Sources Cited

**Purpose:** Complete bibliography of all sources

**Content Requirements:**
- List all statutes cited, with full citations
- List all cases cited, with full Bluebook citations
- Organize alphabetically within each category
- Include URLs for online resources if helpful

**Example:**

```
SOURCES CITED

Statutes and Regulations:
- Age Discrimination in Employment Act, 29 U.S.C. § 623
- Title VII of the Civil Rights Act, 42 U.S.C. § 2000e et seq.
- 29 C.F.R. § 1602.14
- California Fair Employment and Housing Act, Cal. Gov. Code § 12900 et seq.

Case Law:
- Brown v. Green, 199 F.3d 100 (3d Cir. 1998)
- Martinez v. Lopez, 188 F.3d 75 (5th Cir. 2001)
- Miranda v. Arizona, 384 U.S. 436 (1966)
- Smith v. Jones, 256 F.3d 789 (7th Cir. 2001)
- Williams v. Walker-Thomas Furniture Co., 350 F.2d 445 (D.C. Cir. 1965)

Secondary Sources:
- Restatement (Second) of Contracts § 90 (1979)
- Uniform Commercial Code § 2-204 (2022)
```

## Process Steps

### STEP 1: Parse Research Topic

**Action:** Understand the specific legal question

1. Extract the core legal issue from the `/memo [topic]` command
2. Identify jurisdiction (federal, state, or specific state if mentioned)
3. Identify applicable body of law (contract, tort, criminal, employment, etc.)
4. Break into sub-issues if multiple questions present
5. Note any specific cases, statutes, or facts mentioned

**Examples of Topic Parsing:**

```
Input: `/memo Contract breach remedies under UCC`
Parsed:
- Main issue: Contract breach remedies
- Jurisdiction: Federal/All states (UCC is uniform)
- Sub-issues: Damages, specific performance, mitigation
- Applicable law: Uniform Commercial Code

Input: `/memo defamation elements in social media posts in California`
Parsed:
- Main issue: Defamation liability for social media content
- Jurisdiction: California (state-specific analysis)
- Sub-issues: Defamatory statement, publication, damages, fault
- Applicable law: California common law + Cal. Civil Code
```

**Output:**
- Identified main issue(s)
- Identified jurisdiction
- Identified applicable body of law
- Identified sub-issues (if any)

---

### STEP 2: Legal Research & Preparation

**Action:** Research applicable law and prepare analysis structure

1. Identify controlling law:
   - If jurisdiction mentioned, use that state's law
   - Otherwise use federal law or widely-applicable principles
   - Note if both state and federal law apply

2. Identify key cases for Rule section:
   - Landmark cases establishing the legal standard
   - Recent cases clarifying or changing law
   - Jurisdiction-specific cases if applicable
   - Aim for 3-5 cases per issue

3. Identify applicable statutes:
   - Primary statute if one governs the issue
   - Related statutes that provide context
   - Regulatory provisions if applicable

4. Structure the analysis:
   - Determine number of separate IRAC sections needed
   - Break complex issues into elements
   - Plan how to address potential counterarguments

**Output:**
- List of key cases to cite with full Bluebook citations
- List of applicable statutes with citations
- Analysis outline showing IRAC structure
- Identified counterarguments to address

---

### STEP 3: Verify Case Citations via CourtListener

**Action:** Verify all case citations using CourtListener API before finalizing

**For Each Case Citation:**

1. Query CourtListener API with case name
2. Verify information:
   - Correct spelling of case name
   - Correct volume and reporter
   - Correct page number
   - Correct year
   - Confirm case is from controlling jurisdiction (if jurisdiction-specific)

3. Check case status:
   - Is case still good law?
   - Has it been overruled or reversed?
   - Are there relevant updates or clarifications?
   - Note any subsequent history

4. If citation cannot be verified:
   - Mark case as "unverified"
   - Include note in memo: "Citation to [Case] unverified via CourtListener"
   - Consider replacing with verified case if available

5. Log verification results:
   - Case name: [verified/unverified]
   - Citation: [verified citation]
   - Status: [good law/reversed/modified/etc.]

**CourtListener API Approach:**

- Search for case by name and year
- Verify reporter and page number match
- Check case history for reversal or modification
- Note if case is from appropriate jurisdiction
- Document verification status in memo prep

**Output:**
- All case citations verified
- Any unverified cases noted
- Any reversals or modifications noted
- Citation corrections applied if needed

---

### STEP 4: Write Executive Summary

**Action:** Compose one-page executive summary

1. Write opening paragraph:
   - State the legal question clearly
   - Provide brief context if needed
   - 1 paragraph maximum

2. Write rule paragraph:
   - Summarize key legal principle
   - Mention primary statute or controlling case
   - No citations needed, but reference sources
   - 1 paragraph maximum

3. Write conclusion paragraph:
   - Directly answer the question
   - State conclusion with confidence level if appropriate
   - Note any key assumptions
   - 1 paragraph maximum

4. Review for clarity:
   - Ensure non-lawyer could understand summary
   - Remove jargon or explain it
   - Check length: 250-400 words

**Output:**
- Completed Executive Summary section
- Ready for inclusion in memo

---

### STEP 5: Write IRAC Sections

**Action:** Compose Issue, Rule, Application, Conclusion sections

For each distinct legal issue:

**Write ISSUE Subsection:**
1. State "Whether [party] can establish [claim] under [law]"
2. Reference applicable statute or common law
3. Keep to 1-2 sentences
4. Make it clear and unambiguous

**Write RULE Subsection:**
1. Cite primary statute with full citation
2. Explain statutory language or common law principle
3. Break down into legal elements or prongs
4. Cite 3-5 cases for each major element
5. Use Bluebook citations throughout
6. Organize with clear headings for each element
7. Include block quotes only for key language

**Write APPLICATION Subsection:**
1. Assume facts provided or state assumptions clearly
2. Apply each legal element to the facts
3. Use same subheadings as Rule section
4. Discuss how controlling cases support conclusion
5. Address counterarguments explicitly
6. Explain why law supports the conclusion

**Write CONCLUSION Subsection:**
1. Answer the Issue stated above
2. Provide 1-2 sentence conclusion
3. Reference key facts and law
4. Do not repeat entire analysis

**Output:**
- Complete IRAC section for each issue
- All citations verified
- All elements of IRAC present
- Counterarguments addressed

---

### STEP 6: Write Overall Conclusion

**Action:** Compose final conclusion addressing all issues

1. Summarize findings from each IRAC section
2. Answer original research question
3. Provide practical recommendation
4. Note uncertainties or further research needs
5. Keep to 1-2 paragraphs

**Output:**
- Final Conclusion section
- Practical recommendations if applicable

---

### STEP 7: Append Disclaimer

**Action:** Auto-append required legal disclaimer

1. Add Disclaimer section before Sources Cited
2. Use standard disclaimer text provided above
3. Ensure full text is included
4. Note that this is attorney work product

**Output:**
- Disclaimer section added
- Required language included

---

### STEP 8: Compile Sources Cited

**Action:** Create bibliography of all sources

1. Extract all statutes cited and list with full citations
2. Extract all cases cited and list with Bluebook citations
3. Organize by type (Statutes, Cases, Secondary Sources)
4. Arrange alphabetically within each type
5. Include jurisdiction information if helpful

**Output:**
- Complete Sources Cited section
- Organized by type
- Full Bluebook citations for all sources

---

### STEP 9: Generate Word Document

**Action:** Create professional Word (.docx) document

**Use `docx` skill to create document with:**

1. Professional formatting:
   - 1" margins all sides
   - 12pt Times New Roman or Courier font (traditional legal)
   - Single spacing within sections, double spacing between
   - Page breaks between major sections

2. Header:
   - TO, FROM, DATE, RE fields formatted
   - Centered "MEMORANDUM" title

3. Sections in order:
   - Executive Summary
   - IRAC Sections (numbered)
   - Conclusion
   - Disclaimer
   - Sources Cited

4. Page numbering:
   - Footer with page numbers
   - First page unnumbered or marked "Page 1"

5. Table of Contents:
   - Optional but recommended for longer memos
   - Auto-generated if using docx skill

**Output:**
- Professional .docx file created
- Proper legal formatting
- All sections included and formatted

---

### STEP 10: Save with Proper Naming

**Action:** Save file with standardized naming convention

**Filename Format:**
```
[DATE]_memo_[topic_slug].docx
```

**Examples:**
```
2025-02-08_memo_contract-breach-remedies.docx
2025-02-08_memo_employment-discrimination-hostile-environment.docx
2025-02-08_memo_ip-infringement-standards.docx
```

**Naming Rules:**
- Date in YYYY-MM-DD format
- Topic slug in lowercase with hyphens
- Replace spaces, slashes, and special characters with hyphens
- Maximum filename length: 100 characters

**Save Location:**
- `dewey-cheatem-esq/documents/[filename.docx]`

**Output:**
- File saved with proper naming
- Confirm save location and filename
- Provide filepath to user

---

### STEP 11: Verification Checklist

**Action:** Verify memo meets quality standards before delivery

Before finalizing, confirm:

**Content Checklist:**
- [ ] All legal citations are accurate and verified
- [ ] No hallucinated case names or citations
- [ ] Proper jurisdiction is identified
- [ ] IRAC structure is complete (Issue, Rule, Application, Conclusion)
- [ ] All issues are addressed
- [ ] Counterarguments are acknowledged
- [ ] Disclaimer is included
- [ ] Sources Cited section complete

**Format Checklist:**
- [ ] Professional Word document formatting
- [ ] Proper Bluebook citations throughout
- [ ] Header section complete (TO, FROM, DATE, RE)
- [ ] Margins, fonts, spacing correct
- [ ] Page numbers present
- [ ] No spelling or grammar errors

**Legal Standards Checklist:**
- [ ] Analysis follows IRAC format
- [ ] Law is current as of memo date
- [ ] Controlling jurisdiction law is applied
- [ ] All statutes cited with full citations
- [ ] All cases cited with reporter and page
- [ ] Conclusions supported by law and facts
- [ ] Disclaimer language standard and complete

**Output:**
- All checks passed: ✓ Ready for delivery
- Checks failed: ✗ Items needing correction [list items]

---

### STEP 12: Final Delivery

**Action:** Deliver completed memo to user

1. Confirm file is saved to documents/ folder
2. Provide filepath to user
3. Summary of memo contents:
   - Topic: [topic]
   - Issues addressed: [X] issues
   - Jurisdiction: [jurisdiction]
   - Conclusion: [brief conclusion summary]
4. Remind user of disclaimer and attorney work product status
5. Note any limitations or assumptions in analysis

**Output:**
- File location: `/dewey-cheatem-esq/documents/[filename.docx]`
- Memo summary: [topic, issues, conclusion]
- Status: ✓ Complete and ready for use

## Citation Verification Details

### CourtListener Integration

When verifying cases, use CourtListener's search API:

**Search Query Examples:**
- Case name + year: "Miranda v. Arizona 1966"
- Case name + reporter: "Smith v. Jones 256 F.3d"
- PACER case number if available

**Verification Checks:**
1. Case name spelling and abbreviations
2. Volume number before reporter abbreviation
3. Reporter abbreviation (F.3d, U.S., N.E.2d, etc.)
4. Starting page number
5. Year in parentheses
6. Court of decision matches jurisdiction

**Common Reporter Abbreviations:**
- U.S. = United States Supreme Court
- F., F.2d, F.3d = Federal Reporter (Circuit Courts)
- S.Ct. = Supreme Court Reporter
- L.Ed., L.Ed.2d = Lawyers' Edition
- Regional: N.E., N.W., S.E., S.W., N.E.2d, etc.
- State reporters: (State abbreviation), e.g., Cal., Tex.

**Unable to Verify:**
If case cannot be verified:
- Mark as [unverified] in memo
- Provide citation as best understood
- Add explanatory note: "Citation to [Case] unverified via CourtListener. Further verification recommended."
- Consider replacing with verified, similar authority

### Handling Unpublished Opinions

Some cases are "unpublished" or "not reported." Rules vary by jurisdiction:

- Federal: Unpublished opinions may have citation restrictions
- Many states: Unpublished opinions may not be cited
- Local court rules: Check jurisdiction-specific rules
- Generally: Cite reported opinions when available

If using unpublished opinion:
- Note in memo: "[Case] (unpublished opinion per [jurisdiction] rule)"
- Explain why this authority is being used
- Provide full PACER citation if available

## Quality Standards

**Citation Accuracy:**
- 100% of citations must be verified or clearly marked as unverified
- No hallucinated cases or incorrect citations
- All statutory citations include correct section numbers

**Legal Analysis:**
- IRAC structure complete for every issue
- Conclusions supported by cited authority
- Counterarguments acknowledged
- Appropriate hedging language for uncertain issues

**Professional Standards:**
- Proper Bluebook citation format throughout
- Professional Word document formatting
- Clear, organized structure
- Appropriate disclaimer language
- Attorney work product designation

**Completeness:**
- All requested issues addressed
- Appropriate depth for topic complexity
- Sources Cited includes all referenced materials
- Assumptions clearly stated

## Error Handling

### Error: Cannot Verify Case Citation

**Cause:** Case name, reporter, or year appears incorrect or unreported

**Action:**
1. Search CourtListener with various combinations of information
2. Try searching with different case name variations
3. Check if case is from correct jurisdiction/court
4. If still unable to verify: Mark as [unverified] and note in memo

**Output:**
- Citation marked as unverified in memo
- Explanatory note added
- Recommendation to verify independently

### Error: Case Has Been Overruled or Reversed

**Cause:** Controlling case on which analysis depends has been overruled

**Action:**
1. Note in Rule section: "[Case] (reversed/overruled by [newer case])"
2. Update analysis to rely on newer authority
3. If no replacement authority: Note limitation in Conclusion
4. May affect overall conclusion

**Output:**
- Analysis updated to reflect current law
- Disclaimer added about case history
- Conclusion may change

### Error: Topic Requires Multiple Jurisdictions

**Cause:** Legal issue is jurisdiction-dependent and user didn't specify

**Action:**
1. Request clarification: "Which jurisdiction applies? (Federal, specific state, or all)"
2. If no response: Default to federal law with note about state variation
3. May need separate analyses for different jurisdictions

**Output:**
- Confirm jurisdiction with user
- Note any state-by-state variations in memo

### Error: Insufficient Authority on Topic

**Cause:** Limited case law or statutory guidance on specific issue

**Action:**
1. Use analogous authority (similar legal principles)
2. Use secondary sources (Restatements, treatises)
3. Note limitations in memo and Conclusion
4. Explicitly state this area of law has limited precedent
5. Recommend further research or client facts analysis

**Output:**
- Analysis based on best available authority
- Limitations clearly noted
- Recommendation for further research included

## Related Skills

- `docx`: For Word document creation/formatting
- Other legal research skills (if available)

## Ethical Considerations

**Attorney Only Use:**
- This skill is designed for use by licensed attorneys
- Non-lawyers should not use this skill for providing legal advice
- Users must have requisite legal knowledge and expertise

**Work Product Doctrine:**
- All memos are attorney work product
- Protect from disclosure with appropriate "Confidential" markings
- Should not be shared with non-lawyers without attorney approval

**Competence:**
- User responsible for verifying analysis
- User should understand subject matter
- User should not rely solely on this skill without independent review
- Consult additional authorities for complex or novel issues

**Disclaimer Necessity:**
- Disclaimer must be included on every memo
- Disclaimer does not eliminate user responsibility for accuracy
- Memo is for internal analysis, not client advice without review

## File Organization

**Save Location:**
```
dewey-cheatem-esq/documents/[YYYY-MM-DD]_memo_[topic_slug].docx
```

**Directory Structure:**
```
dewey-cheatem-esq/
├── documents/
│   ├── 2025-02-08_memo_contract-remedies.docx
│   ├── 2025-02-08_memo_defamation-social-media.docx
│   ├── 2025-02-08_memo_ip-infringement.docx
│   └── [additional memos]
├── research_notes/
├── sources/
└── templates/
```

## Performance Targets

- Topic parsing: < 1 minute
- Legal research and verification: 5-10 minutes
- Writing memo: 15-30 minutes (depending on complexity)
- Total memo generation: 20-45 minutes per memo
- Simpler topics: 20 minutes
- Complex multi-issue topics: 45 minutes

## Support & Limitations

**This skill can help with:**
- Standard legal research on well-established topics
- IRAC-format memo writing
- Citation verification via CourtListener
- Professional Word document formatting
- Legal disclaimer inclusion

**This skill cannot:**
- Provide actual legal advice (user must provide context)
- Predict case outcomes or appellate success
- Understand client-specific facts (user must provide)
- Replace attorney judgment or experience
- Handle novel or cutting-edge legal issues without verified authority
- Guarantee accuracy (verification should be done by attorney)

**Recommended Verification Steps:**
1. Review all case citations personally
2. Verify law is current in your jurisdiction
3. Research any recent developments not included
4. Adapt memo to specific client facts
5. Never provide memo to client without attorney personalization
6. Do not rely solely on this tool for important legal analysis
