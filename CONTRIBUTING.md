# Contributing to NewsGenerator

This repository is designed to be developed and managed primarily on GitHub (web UI, Codespaces, or GitHub.dev). This document explains the recommended workflow for online contributions, managing CI, secrets, releases, and collaboration tasks so maintainers and AI agents can operate from GitHub directly.

Quick paths to edit on GitHub
- Edit files in the browser: open the repository on GitHub and click a file → pencil icon to edit → propose changes via a Pull Request.
- Open the repository in the lightweight editor: press `.` on the repository page to open `github.dev`.
- Use GitHub Codespaces for a full development environment (recommended for heavy edits).

Branching and PRs
- Use feature branches named like `feat/<short-desc>` or `fix/<short-desc>`.
- Always open a Pull Request for non-trivial changes. Fill the PR template and link any related issues.
- Include tests or run the pipeline locally in Codespaces before requesting review.

Issue and PR triage
- Use the Issues tab to track bugs, feature requests, and tasks.
- Label issues for priority (`priority:high`, `priority:medium`, `area:ingest`, `area:publisher`).
- Use Projects or Discussions for roadmap planning.

Running and verifying CI on GitHub
- Workflows: Actions → select `Scheduled Pipeline` → `Run workflow` to execute the pipeline manually.
- Artifacts: after runs, open the job and download `newsgenerator-output` to inspect `content/` and `outbox/`.

Secrets and publishing
- Add secrets in Settings → Secrets and variables → Actions. Recommended secrets:
  - `HUGGINGFACE_API_KEY`
  - `OPENAI_API_KEY` (optional)
  - `INTERNET_ARCHIVE_ACCESS_KEY`, `INTERNET_ARCHIVE_SECRET` (optional)
  - `ENABLE_PUBLISH` (set to `true` to allow publishing job to upload episodes)
- Publishing steps are guarded: the publish job checks `ENABLE_PUBLISH` and IA secrets before uploading. Keep `ENABLE_PUBLISH` unset to prevent accidental publishes.

How to create a Draft Release
- Go to Releases → Draft a new release → select tag (e.g. `v0.1`) → Save draft.
- Or use `gh` from Codespaces: `gh release create v0.1 --title "Draft v0.1" --notes "Initial scaffold" --draft`.

Recommended repository settings
- Enable branch protections on `main`: require PR reviews, status checks (Actions), and require linear history.
- Restrict who can push to `main` to prevent accidental direct pushes.

How AI maintainers (Copilot) can help from GitHub
- The AI agent can open PRs with code changes, update workflows, and draft release notes.
- Provide the agent with instructions for the next task (e.g., "Implement Open-Meteo ingestor and add tests"). The agent will create a branch, push changes, and open a PR.
- Repository-specific instructions for Copilot are maintained in `.github/copilot-instructions.md` and help guide AI agents to follow project conventions and best practices.

If something fails
- Open Actions logs and paste the relevant snippet into an Issue; tag `area:infra` and assign to maintainers.

Thanks for contributing — if you want, I can add a README section for repository badges and backlog items.
