FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Install base dependencies
RUN apt-get update && apt-get install -y \
    software-properties-common \
    curl \
    wget \
    git \
    sudo \
    python3 \
    python3-pip \
    && add-apt-repository ppa:ubuntu-toolchain-r/test \
    && apt-get update \
    && apt-get install -y \
    libprocps-dev \
    gcc-11 \
    g++-11 \
    valgrind \
    gawk \
    sed \
    libffi-dev \
    ccache \
    libgoogle-perftools-dev \
    yasm \
    texinfo \
    autotools-dev \
    automake \
    cmake \
    libtool \
    build-essential \
    pkg-config \
    autoconf \
    libargtable2-dev \
    libmicrohttpd-dev \
    libhiredis-dev \
    redis-server \
    openssl \
    libssl-dev \
    doxygen \
    libgcrypt20-dev

# Install Node.js 18 LTS
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
  && apt-get install -y nodejs

# Install Docker CLI (optional)
RUN apt-get install -y docker.io

# Install solc
RUN npm install -g solc

# Create workspace user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME || true && \
    useradd --uid $USER_UID --gid $USER_GID -m $USERNAME || true && \
    echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME

USER $USERNAME
WORKDIR /workspace

# Install python deps later via postCreateCommand
