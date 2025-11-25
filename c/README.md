# Tetris C Compilation and Running Instructions

## Windows

**Install a C compiler (if you don't have one):**
- Download [MinGW](https://www.mingw-w64.org/), or
- Install GCC via MSYS2, or
- Use Visual Studio with C++ tools

**Compile:**
```bash
gcc tetris.c -o tetris.exe
```

**Run:**
```bash
tetris.exe
```

## Linux

**Install GCC (if not already installed):**
```bash
sudo apt install gcc        # Ubuntu/Debian
sudo yum install gcc        # Fedora/RHEL
sudo pacman -S gcc          # Arch
```

**Compile:**
```bash
gcc tetris.c -o tetris
```

**Run:**
```bash
./tetris
```

## macOS

**Install Xcode Command Line Tools (if not already installed):**
```bash
xcode-select --install
```

**Compile:**
```bash
gcc tetris.c -o tetris
```

**Run:**
```bash
./tetris
```