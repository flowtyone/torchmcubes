from setuptools import setup

setup_kwargs = {
    'name': 'torchmcubes',
    'version': '0.1.0',
    'description': 'torchmcubes: marching cubes for PyTorch',
    'license': 'MIT',
    'author': 'Tatsuya Yatagawa',
    'author_email': 'tatsy.mail@gmail.com',
    'packages': [
        'torchmcubes'
    ],
    'classifiers': [
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
}

try:
    import torch
    import numpy
except:
    import subprocess
    import threading
    import sys
    import locale

    def handle_stream(stream, is_stdout):
        stream.reconfigure(encoding=locale.getpreferredencoding(), errors='replace')

        for msg in stream:
            if is_stdout:
                print(msg, end="", file=sys.stdout)
            else:
                print(msg, end="", file=sys.stderr)

    def process_wrap(cmd_str, cwd=None, handler=None):
        print(f"EXECUTE: {cmd_str} in '{cwd}'")
        process = subprocess.Popen(cmd_str, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

        if handler is None:
            handler = handle_stream

        stdout_thread = threading.Thread(target=handler, args=(process.stdout, True))
        stderr_thread = threading.Thread(target=handler, args=(process.stderr, False))

        stdout_thread.start()
        stderr_thread.start()

        stdout_thread.join()
        stderr_thread.join()

        return process.wait()

    process_wrap([sys.executable, '-m', 'pip', 'install', 'torch', 'numpy'])


try:
    from torch.utils.cpp_extension import CUDAExtension
    from torch.utils.cpp_extension import BuildExtension

    setup_kwargs.update({
        'ext_modules': [
            CUDAExtension(
                'torchmcubes_module',
                [
                    'cxx/pscan.cu',
                    'cxx/mcubes.cpp',
                    'cxx/mcubes_cpu.cpp',
                    'cxx/mcubes_cuda.cu',
                    'cxx/grid_interp_cpu.cpp',
                    'cxx/grid_interp_cuda.cu',
                ],
                extra_compile_args=['-DWITH_CUDA'],
            )
        ],
        'cmdclass': {
            'build_ext': BuildExtension
        }
    })
    setup(**setup_kwargs)

except:
    print('CUDA environment was not successfully loaded!')
    print('Build only CPU module!')

    from torch.utils.cpp_extension import CppExtension
    from torch.utils.cpp_extension import BuildExtension

    setup_kwargs.update({
        'ext_modules': [
            CppExtension('torchmcubes_module', [
                'cxx/mcubes.cpp',
                'cxx/mcubes_cpu.cpp',
                'cxx/grid_interp_cpu.cpp',
            ])
        ],
        'cmdclass': {
            'build_ext': BuildExtension
        }
    })
    setup(**setup_kwargs)
