# Dream-mind-lucid Repository Instructions

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

This is a documentation-only repository for the $DREAM token ecosystem, a blockchain project concept built on SKALE Network featuring dream mining, cognitive staking, and lucidity-based access controls.

## Current Repository State

**CRITICAL**: This repository currently contains ONLY documentation files. There is no source code, build system, smart contracts, or development infrastructure present.

Do NOT attempt to:
- Run build commands (no build system exists)
- Run tests (no test framework exists) 
- Install dependencies (no package files exist)
- Start servers or applications (no runnable code exists)

## Working Effectively

### Repository Navigation
Always start by understanding the current minimal structure:
- `cd /path/to/Dream-mind-lucid`
- `ls -la` -- shows only README.md, LICENSE, and .github/
- `git --no-pager status` -- check working tree status
- `git --no-pager log --oneline -5` -- review recent commits

### Documentation Work
- `cat README.md` -- review the main project documentation
- `cat LICENSE` -- MIT license file
- Use any text editor to modify documentation files
- Always validate markdown syntax before committing

### Git Operations
- `git --no-pager branch -a` -- show all branches
- `git --no-pager diff` -- show unstaged changes  
- `git --no-pager diff --cached` -- show staged changes
- `git add <file>` -- stage specific files
- `git commit -m "message"` -- commit staged changes
- Use report_progress tool for committing and pushing to PR

## Validation Steps

**ALWAYS run these validation commands after making documentation changes:**

1. **Verify file syntax and readability**:
   - `cat README.md | head -10` -- ensure file is readable
   - Check markdown renders properly in preview

2. **Confirm git operations work**:
   - `git --no-pager status` -- verify changes are detected
   - `git --no-pager diff` -- review your modifications

3. **Repository structure validation**:
   - `find . -type f ! -path "*/.git/*" | sort` -- list all non-git files
   - Ensure no unintended files are added

## Project Context

### Core Concept
$DREAM is conceptualized as a "living neural network" on SKALE Network with three tokens:
- **$DREAM**: Dream Mining & Community Governance (1B supply)
- **$MIND**: Cognitive Staking & Neural Compute (777M supply)  
- **$LUCID**: Access Key to Lucid Zones & AI Oracles (333M supply)

### Key Features (Conceptual)
- Dream mining with AI validation
- Zero gas fees (SKALE-native)
- Resonance-based airdrops
- Cognitive staking for MindNodes
- Lucid Gates for future-prediction arenas

### Contract Addresses (Placeholders)
All contract addresses in README.md are placeholders (0xDREAM..., 0xAIRDROP..., etc.)

## Development Expectations

**Future Development**: When smart contracts, frontend, or backend components are added:
- Look for package.json, hardhat.config.js, or truffle-config.js for blockchain development
- Check for src/, contracts/, or app/ directories for source code
- Update these instructions when build systems are implemented
- Add specific build, test, and deployment commands when available

**Documentation Changes**: 
- Always maintain consistency with the established tone and structure in README.md
- Preserve the existing token supply numbers and conceptual framework
- Keep contract address placeholders until real deployments occur

## Common Tasks Reference

### Repository Root Contents
```
ls -la
total 24
drwxr-xr-x 4 user user 4096 date .
drwxr-xr-x 3 user user 4096 date ..
drwxr-xr-x 7 user user 4096 date .git
drwxr-xr-x 2 user user 4096 date .github
-rw-r--r-- 1 user user 1073 date LICENSE  
-rw-r--r-- 1 user user 1605 date README.md
```

### README.md Key Sections
- Project overview and vision
- Core tokens table ($DREAM, $MIND, $LUCID)
- Key features checklist
- Contract addresses (placeholders)
- Usage examples (conceptual JavaScript)

### Git Branch Information
- Main development occurs on feature branches
- Use descriptive commit messages for documentation changes
- Always use report_progress tool for final commits and PR updates

## Troubleshooting

**"Command not found" errors**: Expected - no build tools are installed because none are needed yet.

**"No such file or directory" for source files**: Expected - this is a documentation-only repository.

**Git conflicts**: Coordinate with other contributors when editing README.md simultaneously.

**Missing dependencies**: Not applicable - no dependency management system exists yet.