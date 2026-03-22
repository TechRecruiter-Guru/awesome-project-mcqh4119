# Emergency Context Recovery via GitHub Gist

When context is completely lost (new machine, corrupted files, fresh Claude session), use this method.

---

## Creating the Emergency Gist

Run this command to create a private gist with your context:

```bash
gh gist create --private --desc "Claude Code Emergency Context - John Polhill III" \
  CLAUDE.md \
  .claude/QUICK-START.md \
  .claude/SESSION-TRACKING.md
```

Save the resulting gist URL somewhere safe (password manager, notes app, etc.)

---

## Recovering Context

### Option 1: Direct Gist Fetch
Tell Claude:
```
Fetch and read this gist: https://gist.github.com/TechRecruiter-Guru/[YOUR_GIST_ID]
```

### Option 2: Copy-Paste Emergency Prompt
Keep this minimal prompt in your notes:

```
I'm John Polhill III, AI-native technical recruiter. I build AI recruiting tools.
Key assets: PAIP 5-agent system, 119 tools at VanguardLab, DefensibleHiringAI.com
LinkedIn: linkedin.com/in/physicalai | GitHub: TechRecruiter-Guru
Preferences: ATS-safe resumes, print-friendly, no emojis unless asked, clean code
Full context: github.com/TechRecruiter-Guru/awesome-project-mcqh4119/CLAUDE.md
```

---

## Keeping the Gist Updated

After major CLAUDE.md changes:

```bash
# List your gists to find the ID
gh gist list

# Update the gist
gh gist edit [GIST_ID] CLAUDE.md
```

---

## Alternative Backup Locations

Consider keeping emergency context in:
1. **GitHub Gist** (private) - recommended
2. **Password manager secure notes**
3. **Google Keep / Apple Notes**
4. **Notion private page**

The key is having ONE reliable place you can access from anywhere.
