# Claude Code Session Tracking System

## Purpose
Track and categorize work across sessions to maintain context separation while leveraging shared knowledge.

---

## Work Categories

### 1. APP - Application Development
Core product work: PAIP system, marketplace, tools, infrastructure

### 2. CAREER - Private Career Materials
Resumes, cover letters, job applications
**Location**: `.resumes/` (git-ignored, private)

### 3. CONTENT - Public Content Creation
LinkedIn posts, blog articles, documentation

### 4. RESEARCH - Exploration and Learning
Market research, technology evaluation, skill building

---

## Session Audit Template

When ending a session, create: `.claude/session-audit-YYYY-MM-DD.md`

```markdown
# Session Audit: [Session Name]
**Session ID**: [from URL]
**Date**: YYYY-MM-DD
**Branch**: [branch name]

## Work by Category
### APP
- [ ] Task 1
- [ ] Task 2

### CAREER
- [ ] Resume for [Company] - [Role]

### CONTENT
- [ ] LinkedIn post about [topic]

### RESEARCH
- [ ] Explored [topic]

## Context Established
[Key knowledge/decisions that should carry forward]

## Files Created/Modified
[List of files]
```

---

## Resume Request Protocol

When requesting a resume in any session:

1. **Provide**: Job description (paste or link)
2. **Reference**: "Use my PAIP portfolio context"
3. **Specify**: Any customization (tone, emphasis, etc.)
4. **Output**: Goes to `.resumes/` automatically

### Portfolio Context Keywords
These trigger inclusion of your full background:
- "PAIP system"
- "119 tools"
- "VanguardLab marketplace"
- "Physical AI Pros"
- "DefensibleHiringAI"
- "Talent Intelligence portfolio"

---

## Session Index

| Date | Session ID | Primary Focus | Audit File |
|------|------------|---------------|------------|
| 2026-03-22 | session_01BeUP7Q6BMDsq6tux8ino9q | Agentic System + Resumes | session-audit-2026-03-22.md |

---

## Best Practices

1. **Start sessions with context**: "Continuing work on [project]"
2. **End sessions with audit**: Create audit file before closing
3. **Keep categories clean**: One primary focus per session when possible
4. **Cross-reference**: Note when secondary work leverages primary context
5. **Private stays private**: Career materials always to `.resumes/`
