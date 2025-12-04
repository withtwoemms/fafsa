# Take-Home Assignment: FAFSA Edit Rule Processor

## Overview

Build a service that applies validation rules ("edits") to FAFSA application data. The service should accept application data, apply configured edit rules, and return validation results.

**Time Limit:** we would not want you to spend more than 2 hours on the solution. We are looking for working software, to review your thinking and discuss.

**AI Usage:** We **encourage** the use of AI tools (ChatGPT, Claude, Copilot, etc.). We want to see how you work with modern tools to build quality software. What matters is your engineering decisions and ability to explain/extend your code.

**Tooling** While tooling/frameworks is open, we remind you that we  utlise a combination of Java/Spring and Python in our existing stack.

---

## Background

In financial aid processing, "edits" are validation rules that check application data for errors, inconsistencies, or missing information and provided feedback to users. For example:
- "Age must be between 14 and 120"
- "If married, spouse SSN is required"
- "Income cannot be negative"
- "State code must be valid"

Your service will apply these rules to application data and report violations.

---

## System Constraints

Design your service with these operational characteristics:

- **Rules**: Implement validation rules (listed below)
- **Rule Changes**: Rules may be added or modified during the year
- **Accuracy**: All rules must be applied consistently

---

## Core Requirements

### 1. Application Data API

Accept FAFSA application data via HTTP API:

- Endpoint that accepts application data
- Application includes:
  - Student info: name, DOB, SSN
  - Dependency status: dependent/independent
  - Marital status: single/married
  - Spouse info: name, SSN (if married)
  - Household: number in household, number in college
  - Income: student income, parent income (if dependent)
  - State: state of legal residence
- Return validation results

### 2. Edit Rules

Implement these 7 required validation rules:

1. **Student Age**: Student must be at least 14 years old
2. **SSN Format**: SSN must be in valid format (9 digits)
3. **Dependent Parent Income**: If dependency status is "dependent", parent income is required
4. **Income Validation**: Income values cannot be negative
5. **Household Logic**: Number in college cannot exceed number in household
6. **State Code**: State code must be a valid US state abbreviation
7. **Marital Status**: If marital status is "married", spouse information is required

**Implementation Requirements:**
- Apply all applicable rules to each application
- Rules can have different severity levels (you decide how to categorize)
- Handle conditional rules that depend on other fields

### 3. Validation Results

Return clear validation results:

- Which rules passed/failed
- Error messages for failed rules
- Overall application status (valid/invalid, or more nuanced)
- Enough information to understand what's wrong and how to correct

---

## Intentionally Open Questions

**You decide and document your reasoning:**

- **Rule Representation**: How are rules defined? (code, config file, database, DSL?)
- **Rule Priority**: Do some rules run before others? Does order matter?
- **Error Handling**: Stop at first error or collect all errors?
- **Rule Conflicts**: What if rules contradict each other?
- **Performance**: How do you efficiently apply many rules to many applications?
- **Extensibility**: How easy is it to add new rules?
- **Severity Levels**: How do you categorize different types of violations?

---

## What to Submit

### Required

1. **Source Code**
   - Complete, runnable service
   - **Tests** that cover core validation logic
   - **no** intermidiate files or libraries
   - Clean git history (don't squash - we want to see how you built this)
   - Any language/framework you're comfortable with

2. **Documentation**
   - **README.md**: How to build, run, and test your service
   - **DECISIONS.md**: Your design decisions, trade-offs, and assumptions
   - Example API usage

---

## What We're Evaluating

### Must Have (to pass)
- **Works**: Can we run it and validate applications?
- **Runnable**: Clear build/run instructions that work
- **Documented**: We understand your decisions from DECISIONS.md
- **Clean**: Code is readable and maintainable
- **Testing strategy**: Meaningful tests with good coverage of core validation logic

### Should Have (separates good from great)
- **Smart decisions**: Thoughtful rule representation and application strategy
- **Error handling**: Gracefully handles edge cases
- **Extensibility**: Easy to add new rules
- **Performance**: Considers the throughput requirements

### Nice to Have (bonus points)
- **Production thinking**: Logging, metrics, config management
- **Clean git history**: Incremental commits showing your thought process

---

## AI Usage - Important

**AI Usage.** What we're evaluating:

- **Engineering judgment**: Can you make and justify technical decisions?
- **Understanding**: Can you explain your code and extend it?
- **Quality**: Is the result clean, tested, and production-ready?

AI is a tool. We care about **your decisions**, not whether you used AI.

---

## What Happens Next

After submission:

1. We'll review your code
2. If it looks good, we'll schedule a **90-minute technical interview**
3. In the interview, you'll:
   - Walk us through your solution (~10 min)
   - Discuss your design decisions
   - Extend your code based on new requirements (live coding)
   - Discuss how it would scale/change with different constraints

**Tip**: Be ready to modify your code in the interview. We'll ask you to add features, change constraints, or handle new scenarios.

---

## Submission Instructions

Submit a Git repository (GitHub/GitLab/Bitbucket link or zip) containing:

- [ ] Source code, including tests
- [ ] README.md (build/run instructions)
- [ ] DECISIONS.md (your design decisions and reasoning)
- [ ] Git history (not squashed)

**Deadline:** You will work with recruiter to find a time and deadline to submit your code.

---

## Sample Application Data

Here's example data to help you get started:

**Valid Application:**
```json
{
  "studentInfo": {
    "firstName": "Jane",
    "lastName": "Smith",
    "ssn": "123456789",
    "dateOfBirth": "2003-05-15"
  },
  "dependencyStatus": "dependent",
  "maritalStatus": "single",
  "household": {
    "numberInHousehold": 4,
    "numberInCollege": 1
  },
  "income": {
    "studentIncome": 5000,
    "parentIncome": 65000
  },
  "stateOfResidence": "CA"
}
```

**Invalid Application Example:**
```json
{
  "studentInfo": {
    "firstName": "John",
    "lastName": "Doe",
    "ssn": "invalid",
    "dateOfBirth": "2015-01-01"
  },
  "dependencyStatus": "dependent",
  "maritalStatus": "married",
  "household": {
    "numberInHousehold": 2,
    "numberInCollege": 5
  },
  "income": {
    "studentIncome": -1000
  },
  "stateOfResidence": "XX"
}
```

This application violates multiple rules:
- Student too young (9 years old, < 14)
- Invalid SSN format
- Dependent but missing parent income
- Married but missing spouse info
- Negative student income
- Number in college (5) > household (2)
- Invalid state code

---

## Questions?

Feel free to ask! Some ambiguity is intentional - we want to see how you handle it. Use your best judgment and document your assumptions.

---

**Time Spent:** Please document honestly how long this took you. We're calibrating our expectations.

**Good luck!** We're excited to see your approach.