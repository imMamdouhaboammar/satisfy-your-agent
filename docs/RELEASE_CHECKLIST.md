# Release Checklist

Local development can finish without pretending public distribution is complete.

Before public submission:

- verify the current official OpenAI Skills, Plugins, Hooks, and listing documentation
- run the current official plugin validator against a clean checkout and a clean extracted archive
- run Plugin Eval static analysis and live benchmark scenarios
- add product-specific light and dark brand assets if required by the current directory contract
- add verified developer identity, website, support, privacy policy, and terms information
- verify every manifest field against the current schema
- test installation on every actually available target surface
- confirm hooks remain off by default after fresh installation
- inspect the archive for secrets, absolute paths, caches, bytecode, and local state
- package twice and verify deterministic output if deterministic packaging is claimed
- keep statuses distinct: locally validated, submission ready, submitted, approved, published
