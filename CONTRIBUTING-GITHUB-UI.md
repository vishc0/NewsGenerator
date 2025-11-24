# Quick guide: Editing this repo entirely from GitHub (web UI)

If you prefer to avoid local setup, these steps let you make changes, run CI, and manage releases entirely from GitHub's website.

1) Edit files in the browser
- Open a file and click the pencil icon to edit. Commit directly to `main` for small typo fixes, or create a branch and open a Pull Request for larger changes.

2) Run the workflow manually
- Actions → Scheduled Pipeline → Run workflow → choose `main` → Run. Wait for the run to finish.

3) Download artifacts
- After the run completes, open the `run-pipeline` job and click `Artifacts` → `newsgenerator-output` to download generated outputs.

7) Trigger pipeline from a PR comment
- Maintainers can trigger a pipeline run by commenting `/run-pipeline` on a Pull Request. The workflow only accepts this command from repository owners, members, or collaborators for safety.


4) Create a Draft Release
- Releases → Draft a new release → select the `v0.1` tag or create it.

5) Add or update secrets
- Settings → Secrets and variables → Actions → New repository secret. Add `HUGGINGFACE_API_KEY` etc.

6) Approving PRs and merging
- Use the Files changed tab and the Review button to approve. Merge when CI checks pass.
