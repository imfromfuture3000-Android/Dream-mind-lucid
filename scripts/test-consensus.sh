#!/bin/bash
set -euo pipefail

echo "🧪 Running SKALE consensus basic test..."

cd /workspace/skale-consensus/test/onenode
sudo NO_ULIMIT_CHECK=1 TEST_TIME_S=60 TEST_TRANSACTIONS_PER_BLOCK=10 ../../build/consensust [consensus-basic]

echo "✅ Basic consensus test complete!"
