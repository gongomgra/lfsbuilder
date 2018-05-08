# Builder: '@@LFS_BUILDER_NAME@@'

# Do not locate and remember (hash) commands as they are looked up for execution
set +h

# Any command which fail will cause the shell script to exit immediately
set -e

# Any command will fail if using any unset variable. For example: "sudo rm -rf /${UNSET_VARIABLE}*"
# won't run "sudo rm /*". It will fail instead
set -u

# Default umask value
umask 022

# LFS custom PATH
PATH=@@LFS_ENV_PATH_VALUE@@
export PATH

# LFS mount point
LFS=@@LFS_BASE_DIRECTORY@@
export LFS

# LFS target kernel name
LFS_TGT=$(uname -m)-lfs-linux-gnu
export LFS_TGT

LC_ALL=POSIX
export LC_ALL

# LFS compile core numbers
MAKEFLAGS='@@LFS_MAKEFLAGS@@'
export MAKEFLAGS

# Terminal has full of colors
TERM=xterm-256color
export TERM
