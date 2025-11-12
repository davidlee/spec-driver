---
id: ISSUE-019
name: installer needs to install or mention npx ts-doc-gen
created: '2025-11-05'
updated: '2025-11-05'
status: open
kind: issue
categories: []
severity: p3
impact: user
---

# installer needs to install or mention npx ts-doc-gen

yeah so running sync on a TS project will hang silently unless you've got the package installed, as it tries to run npx ts-doc-gen which is presumably hanging awaiting user confirmation.

Ideally there's a way to pass -y to npx or similar, otherwise we'll have to deal with it during installation.
