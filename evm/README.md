EVM integration scaffold for Dream-Mind-Lucid

Quick start:

1. Change into the `evm` folder:

```powershell
cd evm
```

2. Install dev dependencies:

```powershell
npm install
```

3. Compile contracts:

```powershell
npx hardhat compile
```

4. Run tests:

```powershell
npx hardhat test
```

5. Deploy locally:

```powershell
npx hardhat run --network localhost scripts/deploy.js
```

Note: This scaffold intentionally keeps threshold signature verification off-chain for now. Next steps are to add on-chain BLS verification (via precompile or verifier contract) and implement full lucidity proof flow.
