# Issue tracker: Local Markdown

Issues and PRDs for this repo live as markdown files in `.scratch/`. GitHub Issues is not used by agent skills.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The PRD is `.scratch/<feature-slug>/PRD.md`
- Implementation issues are `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`
- Triage state is recorded as a `Status:` line near the top of each issue file
- Comments and conversation history append under a `## Comments` heading

## Skill operations

When a skill says "publish to the issue tracker", create a file under `.scratch/<feature-slug>/`.

When a skill says "fetch the relevant ticket", read the referenced local markdown file.
