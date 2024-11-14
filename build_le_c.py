import os
import platform
import subprocess
import sys

# Set the output program name and build type (debug or release)
output_program = "output_program"  # Change this to your desired output name
build_type = sys.argv[1].lower() if len(sys.argv) > 1 else "debug"

# Paths for source, include, and library directories
src_dir = 'src'
include_dir = 'include'
library_dir = 'library'

# Collect all .c files in src and all .h files in include
c_files = []
for root, _, files in os.walk(src_dir):
    for file in files:
        if file.endswith('.c'):
            c_files.append(os.path.join(root, file))

h_files = []
for root, _, files in os.walk(include_dir):
    for file in files:
        if file.endswith('.h'):
            h_files.append(os.path.join(root, file))

# Collect all .a or .lib files in the library directory
library_files = []
for root, _, files in os.walk(library_dir):
    for file in files:
        if file.endswith('.a') or (platform.system().lower() == 'windows' and file.endswith('.lib')):
            library_files.append(os.path.join(root, file))

# Detect OS and select compiler
os_type = platform.system().lower()
if 'linux' in os_type or 'darwin' in os_type:  # Darwin is the OS name for macOS
    compiler = 'gcc'
elif 'windows' in os_type:
    compiler = 'cl'
else:
    raise OSError("Unsupported OS. This script supports only Linux, macOS, and Windows.")

# Detect system architecture
architecture = platform.machine().lower()
if 'x86' in architecture and '64' not in architecture:
    arch_flags = ['-m32'] if compiler == 'gcc' else ['/arch:IA32']
elif 'x86_64' in architecture or 'amd64' in architecture:
    arch_flags = ['-m64'] if compiler == 'gcc' else ['/arch:AVX']
elif 'arm64' in architecture:
    arch_flags = ['-march=armv8-a'] if compiler == 'gcc' else ['/arch:ARM64']
elif 'arm' in architecture:
    arch_flags = ['-march=armv7-a'] if compiler == 'gcc' else ['/arch:ARM']
else:
    raise OSError("Unsupported architecture. This script supports x86, x64, ARM, and ARM64.")

# Set build flags based on build type
if build_type == "debug":
    build_flags = ['-g'] if compiler == 'gcc' else ['/Zi', '/Od', '/DEBUG']
elif build_type == "release":
    build_flags = ['-O2'] if compiler == 'gcc' else ['/O2', '/DNDEBUG']
else:
    raise ValueError("Invalid build type. Use 'debug' or 'release'.")

# Compile with the appropriate command
try:
    if compiler == 'gcc':
        # GCC command for Linux/macOS
        library_flags = library_files  # .a files are linked directly by specifying their paths
        gcc_command = ['gcc', '-o', output_program] + arch_flags + build_flags + c_files + ['-I', include_dir] + library_flags
        subprocess.run(gcc_command, check=True)
        print(f"Compilation successful with GCC in {build_type} mode.")
    elif compiler == 'cl':
        # MSVC command for Windows
        library_flags = [f'/link {lib}' for lib in library_files]  # For MSVC, use /link with .lib files
        cl_command = ['cl', f'/Fe:{output_program}.exe'] + arch_flags + build_flags + c_files + [f'/I{include_dir}'] + library_flags
        subprocess.run(cl_command, check=True)
        print(f"Compilation successful with MSVC in {build_type} mode.")
except subprocess.CalledProcessError as e:
    print("Compilation failed.")
    print(e)
