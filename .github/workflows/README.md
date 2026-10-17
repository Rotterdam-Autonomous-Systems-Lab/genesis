# GitHub workflows

[foundry.yml](foundry.yml) checks pinned tool/dependency integrity, formatting, offline compilation, unit/fuzz/stateful tests, and a loopback Anvil smoke query on Ubuntu 24.04. Permissions are contents:read only, third-party actions are pinned by commit, checkout credentials are not persisted, and caching is disabled.

Tool setup downloads versioned build tools over HTTPS; tests use only the in-memory EVM. The Anvil smoke check creates no accounts and submits no transactions. There are no broadcast/deployment commands, public blockchain RPC endpoints, production credentials, or secret inputs. This CI does not implement the Python agents or claim full Experiment 001 acceptance.
