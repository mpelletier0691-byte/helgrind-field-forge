"""Shared install snippets (not in default apt on Linux Mint)."""

# Install lazygit: apt if available, else GitHub release binary.
LAZYGIT_INSTALL = r"""
install_lazygit() {
  if command -v lazygit >/dev/null 2>&1; then
    echo "lazygit: already installed"
    return 0
  fi
  if apt-get install -y lazygit 2>/dev/null; then
    echo "lazygit: installed from apt"
    return 0
  fi
  echo "lazygit: installing from GitHub release…"
  apt-get install -y curl tar
  VER=$(curl -fsSL https://api.github.com/repos/jesseduffield/lazygit/releases/latest \
    | grep -m1 '"tag_name"' | sed 's/.*"v\([^"]*\)".*/\1/')
  [ -z "$VER" ] && VER="0.44.1"
  URL="https://github.com/jesseduffield/lazygit/releases/download/v${VER}/lazygit_${VER}_Linux_x86_64.tar.gz"
  curl -fsSL "$URL" -o /tmp/lazygit.tgz
  tar -xzf /tmp/lazygit.tgz -C /tmp lazygit
  install -m 755 /tmp/lazygit /usr/local/bin/lazygit
  rm -f /tmp/lazygit.tgz /tmp/lazygit
  command -v lazygit >/dev/null && echo "lazygit: OK" || echo "lazygit: install failed"
}
install_lazygit
"""

# Apt packages that are not in Linux Mint repos — install via script instead.
APT_SKIP = frozenset({"lazygit"})
