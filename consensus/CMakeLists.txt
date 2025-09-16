cmake_minimum_required(VERSION 3.10)
project(dream_mind_consensus)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add SKALE consensus as external project
include(ExternalProject)
ExternalProject_Add(skale_consensus
  GIT_REPOSITORY    https://github.com/skalenetwork/skale-consensus.git
  GIT_TAG          develop
  CMAKE_ARGS      -DCMAKE_INSTALL_PREFIX=${CMAKE_BINARY_DIR}/skale-consensus
)

# Find required packages
find_package(OpenSSL REQUIRED)
find_package(Threads REQUIRED)

# Add nlohmann_json for JSON parsing
include(FetchContent)
FetchContent_Declare(
  json
  URL https://github.com/nlohmann/json/releases/download/v3.11.2/json.tar.xz
)
FetchContent_MakeAvailable(json)

# Add main consensus library
add_library(dream_consensus
  src/DreamConsensus.cpp
  src/DreamBlock.cpp
  src/DreamNode.cpp
  src/AgentRegistry.cpp
)

target_include_directories(dream_consensus PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_BINARY_DIR}/skale-consensus/include
)

target_link_libraries(dream_consensus
  OpenSSL::SSL
  OpenSSL::Crypto
  Threads::Threads
  ${CMAKE_BINARY_DIR}/skale-consensus/lib/libskale-consensus.a
)

# Add test executable
add_executable(dream_consensus_test
  test/test_main.cpp
  test/test_consensus.cpp
)

target_link_libraries(dream_consensus_test
  dream_consensus
  gtest
  gtest_main
)
