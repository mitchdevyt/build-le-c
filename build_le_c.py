import os
import platform
import subprocess
import sys

# Set the output program name and build type (debug or release)
output_program = "output_program"
build_type = sys.argv[1].lower() if len(sys.argv) > 1 else "debug"

# Paths for source, include, library, and build directories
src_dir = 'src'
include_dir = 'include'
library_dir = 'library'
build_dir = 'build'

# Ensure the build directory exists
os.makedirs(build_dir, exist_ok=True)

# Full path to the output program
output_path = os.path.join(build_dir, output_program)

# Collect all .c files in src and all .h files in include
c_files = []
for root, _, files in os.walk(src_dir):
    for file in files:
        if file.endswith('.c'):
            c_files.append(os.path.join(root, file))

include_files = []
for root, _, files in os.walk(include_dir):
    for file in files:
        if file.endswith('.h'):
            include_files.append(os.path.join(root, file))

# Collect all .a or .lib files in the library directory
library_files = []
for root, _, files in os.walk(library_dir):
    for file in files:
        if file.endswith('.a') or (platform.system().lower() == 'windows' and file.endswith('.lib')):
            library_files.append(os.path.join(root, file))

# Detect OS and select compiler
os_type = platform.system().lower()
if os_type == 'windows':
    compiler = 'cl'
elif 'linux' in os_type or 'darwin' in os_type:  # Darwin is the OS name for macOS
    compiler = 'gcc'
else:
    raise OSError("Unsupported OS. This script supports Linux, macOS, and Windows.")

# Detect system architecture
architecture = platform.machine().lower()
arch_flags = []
if 'x86' in architecture and '64' not in architecture:
    arch_flags = ['/arch:IA32'] if compiler == 'cl' else ['-m32']
elif 'x86_64' in architecture or 'amd64' in architecture:
    arch_flags = ['/arch:AVX'] if compiler == 'cl' else ['-m64']
elif 'arm64' in architecture:
    arch_flags = ['/arch:ARM64'] if compiler == 'cl' else ['-march=armv8-a']
elif 'arm' in architecture:
    arch_flags = ['/arch:ARM'] if compiler == 'cl' else ['-march=armv7-a']
else:
    raise OSError("Unsupported architecture. This script supports x86, x64, ARM, and ARM64.")

# Set build flags based on build type
if build_type == "debug":
    build_flags = ['/Zi', '/Od', '/DEBUG'] if compiler == 'cl' else ['-g']
elif build_type == "release":
    build_flags = ['/O2', '/DNDEBUG'] if compiler == 'cl' else ['-O2']
else:
    raise ValueError("Invalid build type. Use 'debug' or 'release'.")

# Compile with the appropriate command
try:
    if compiler == 'gcc':
        # GCC command for Linux/macOS
        library_flags = library_files  # .a files are linked directly by specifying their paths
        gcc_command = ['gcc', '-o', output_path] + arch_flags + build_flags + c_files + ['-I', include_dir] + library_flags
        subprocess.run(gcc_command, check=True)
        print(f"Compilation successful with GCC in {build_type} mode.")
    elif compiler == 'cl':
        # MSVC command for Windows
        library_flags = [f'/link {lib}' for lib in library_files]  # For MSVC, use /link with .lib files
        cl_command = ['cl', f'/Fe:{output_path}.exe'] + arch_flags + build_flags + c_files + [f'/I{include_dir}'] + library_flags
        subprocess.run(cl_command, check=True)
        print(f"Compilation successful with MSVC in {build_type} mode.")
except subprocess.CalledProcessError as e:
    print("Compilation failed.")
    print(e)
