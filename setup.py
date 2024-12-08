import ast
import re
import sys
import platform

from setuptools import Extension, setup

from setuptools import find_packages, setup

def get_ext_modules() -> list:
    """获取三方模块"""
    # Linux
    if platform.system() == "Linux":
        extra_compile_flags = [
            "-std=c++17",
            "-O3",
            "-Wno-delete-incomplete",
            "-Wno-sign-compare",
        ]
        extra_link_args = ["-lstdc++"]
        runtime_library_dirs = ["$ORIGIN"]
        libraries = [
            "xmdapi",
            "sptraderapi",
            "traderapi",
        ]
    # Windows
    elif platform.system() == "Windows":
        extra_compile_flags = ["-O2", "-MT"]
        extra_link_args = []
        runtime_library_dirs = []
        libraries = [
            "xmdapi",
            "sptraderapi",
            "traderapi",
        ]

    include_dirs = ["yubaoCtrader/tora_gateway/api/include", "yubaoCtrader/tora_gateway/api/include/tora", "yubaoCtrader/tora_gateway/api/vntora"]
    library_dirs = ["yubaoCtrader/tora_gateway/api/libs", "yubaoCtrader/tora_gateway/api"]

    vntoramd = Extension(
        "yubaoCtrader.tora_gateway.api.vntoramd",
        ["yubaoCtrader/tora_gateway/api/vntora/vntoramd/vntoramd.cpp"],
        include_dirs=include_dirs,
        define_macros=[],
        undef_macros=[],
        library_dirs=library_dirs,
        libraries=libraries,
        extra_compile_args=extra_compile_flags,
        extra_link_args=extra_link_args,
        runtime_library_dirs=runtime_library_dirs,
        depends=[],
        language="cpp",
    )

    vntoraoption = Extension(
        "yubaoCtrader.tora_gateway.api.vntoraoption",
        ["yubaoCtrader/tora_gateway/api/vntora/vntoraoption/vntoraoption.cpp"],
        include_dirs=include_dirs,
        define_macros=[],
        undef_macros=[],
        library_dirs=library_dirs,
        libraries=libraries,
        extra_compile_args=extra_compile_flags,
        extra_link_args=extra_link_args,
        runtime_library_dirs=runtime_library_dirs,
        depends=[],
        language="cpp",
    )

    vntorastock = Extension(
        "yubaoCtrader.tora_gateway.api.vntorastock",
        ["yubaoCtrader/tora_gateway/api/vntora/vntorastock/vntorastock.cpp"],
        include_dirs=include_dirs,
        define_macros=[],
        undef_macros=[],
        library_dirs=library_dirs,
        libraries=libraries,
        extra_compile_args=extra_compile_flags,
        extra_link_args=extra_link_args,
        runtime_library_dirs=runtime_library_dirs,
        depends=[],
        language="cpp",
    )

    return [vntoramd, vntoraoption, vntorastock]


def get_install_requires():
    install_requires = [
        "simplejson",
        "flask",
        "requests",
        "aiohttp",
        "pytz",
        "peewee",
        "numpy",
        "pandas",
        "matplotlib",
        "seaborn",
        "deap",
        "tzlocal",
        "plotly",
        "importlib-metadata",
        "pymysql",
        "cryptography",
        "scikit-learn",
        "nbformat",
        "tqdm",
        "rqdatac",
        "wmi",
        "pymysql",
        "pyside6"
    ]

    if sys.version_info.minor < 7:
        install_requires.append("dataclasses")
    return install_requires


def get_version_string():
    global version
    with open("yubaoCtrader/__init__.py", "rb") as f:
        version_line = re.search(
            r"__version__\s+=\s+(.*)", f.read().decode("utf-8")
        ).group(1)
        return str(ast.literal_eval(version_line))

setup(
    name="yubaoCtrader",
    version=get_version_string(),
    author="yubao",
    author_email="baochunhui1996@gmail.com",
    license="MIT",
    url="",
    description="A framework for developing quant trading systems.",
    long_description=__doc__,
    keywords='quant quantitative investment trading algotrading',
    include_package_data=True,
    packages=find_packages(),
    package_data={"": ["*"]},
    install_requires=get_install_requires(),
    ext_modules=get_ext_modules(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: Microsoft :: Windows :: Windows 7",
        "Operating System :: Microsoft :: Windows :: Windows 8",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows Server 2008",
        "Operating System :: Microsoft :: Windows :: Windows Server 2012",
        "Operating System :: Microsoft :: Windows :: Windows Server 2012",
        "Operating System :: POSIX :: Linux"
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial :: Investment :: yubao",
        "Programming Language :: Python :: Implementation :: CPython",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English"
    ],
)
