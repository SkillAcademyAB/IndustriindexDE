Branch protection instructions

To require this repository's Healthcheck workflow to pass before a pull request can be merged, set up a branch protection rule for `main` and `develop`:

1. Go to the repository on GitHub.
2. Settings -> Branches -> Add rule.
3. In "Branch name pattern" enter `main` (repeat for `develop` if desired).
4. Check "Require status checks to pass before merging".
5. In the searchable list, select the workflow run named "Healthcheck" (it may appear as `Healthcheck` or `healthcheck`).
6. Optionally check "Require branches to be up to date before merging".
7. Save changes.

Notes:
- The workflow must have run at least once on the branch/PR to appear in the status check list.
- If your org enforces required reviewers or other checks, include those in the rule as needed.
