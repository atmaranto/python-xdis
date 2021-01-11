# (C) Copyright 2018-2020 by Rocky Bernstein
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

"""
Everything you ever wanted to know about Python versions and their
magic numbers. And a little bit more...

by_magic: in this dictionary, the key is a magic byte string like
# b'\x03\xf3\r\n' and its value is a canonic version string, like
# '2.7'

by_version: in this dictionary, the key is a canonic version string like '2.7,
and its value is a magic byte string like b'\x03\xf3\r\n' canonic
name, like '2.7'

magicint2version:  in this dictionary, the key is an magic integer, e.g. 62211,
and the value is its canonic versions string, e.g. '2.7'

PYTHON_MAGIC_INT: The magic integer for the current running Python interpreter
"""

import re, struct, sys
from xdis import IS_PYPY

IS_PYPY3 = (48, 64, 112, 160, 192)


def add_magic_from_int(magic_int, version):
    magicint2version[magic_int] = version
    versions[int2magic(magic_int)] = version


def int2magic(magic_int):
    """Given a magic int like 62211, compute the corresponding magic byte string
     b'\x03\xf3\r\n' using the conversion method that does this.

    See also dictionary magic2nt2version which has precomputed these values
    for knonwn magic_int's.
    """

    if magic_int in (39170, 39171):
        return struct.pack("<H", magic_int) + "\x99\x00"
    if sys.version_info >= (3, 0):
        return struct.pack(
            "<Hcc", magic_int, bytes("\r", "utf-8"), bytes("\n", "utf-8")
        )
    else:
        return struct.pack("<Hcc", magic_int, "\r", "\n")


def magic2int(magic):
    """Given a magic byte string, e.g. b'\x03\xf3\r\n', compute the
    corresponding magic integer, e.g. 62211, using the conversion
    method that does this.

    See also dictionary magic2nt2version which has precomputed these values
    for knonwn magic_int's.

    """
    return struct.unpack("<Hcc", magic)[0]


def __by_version(magics):
    for m, v in list(magics.items()):
        if m not in by_magic:
            by_magic[m] = set([v])
        else:
            by_magic[m].add(v)
        by_version[v] = m
    return by_version


# Documentation for the below variables is above.
by_magic = {}
by_version = {}
magicint2version = {}
versions = {}

if sys.version_info >= (3, 4):
    import importlib

    MAGIC = importlib.util.MAGIC_NUMBER
    PYTHON_MAGIC_INT = magic2int(MAGIC)
else:
    import imp

    MAGIC = imp.get_magic()
    PYTHON_MAGIC_INT = magic2int(MAGIC)

# The magic word is used to reject .pyc files generated by other
# Python versions.  It should change for each incompatible change to
# the bytecode.
#
# The value of CR and LF is incorporated so if you ever read or write
# a .pyc file in text mode the magic number will be wrong; also, the
# Apple MPW compiler swaps their values, botching string constants.
#
# The magic numbers must be spaced apart at least 2 values, as the
# -U interpeter flag will cause MAGIC+1 being used. They have been
# odd numbers for some time now.
#
# There were a variety of old schemes for setting the magic number.
# The current working scheme is to increment the previous value by
# 10.
#
# Starting with the adoption of PEP 3147 in Python 3.2, every bump in magic
# number also includes a new "magic tag", i.e. a human readable string used
# to represent the magic number in __pycache__ directories.  When you change
# the magic number, you must also set a new unique magic tag.  Generally this
# can be named after the Python major version of the magic number bump, but
# it can really be anything, as long as it's different than anything else
# that's come before.  The tags are included in the following table, starting
# with Python 3.2a0.

# The below is taken from from Python/import.c, and more recently
# Lib/importlib/_bootstrap.py and other sources

#                  magic,  canonic version number
add_magic_from_int(39170, "1.0")
add_magic_from_int(39171, "1.1")  # covers 1.2 as well
add_magic_from_int(11913, "1.3")
add_magic_from_int(5892, "1.4")

# 1.5, 1.5.1, 1.5.2
add_magic_from_int(20121, "1.5")  # 1.5.1, 1.5.2
add_magic_from_int(50428, "1.6")  # 1.6

add_magic_from_int(50823, "2.0")  # 2.0, 2.0.1
add_magic_from_int(60202, "2.1")  # 2.1, 2.1.1, 2.1.2
add_magic_from_int(60717, "2.2")  # 2.2

# Two magics one version!
add_magic_from_int(62011, "2.3a0")
add_magic_from_int(62021, "2.3a0")  # two distinct magics for the same release

add_magic_from_int(62041, "2.4a0")
add_magic_from_int(62051, "2.4a3")
add_magic_from_int(62061, "2.4b1")
add_magic_from_int(62071, "2.5a0")
add_magic_from_int(62081, "2.5a0")  # ast-branch
add_magic_from_int(62091, "2.5a0")  # with
add_magic_from_int(62092, "2.5a0")  # changed WITH_CLEANUP opcode
add_magic_from_int(62101, "2.5b3")  # fix wrong code: for x, in ...
add_magic_from_int(62111, "2.5b3")  # fix wrong code: x += yield

# Fix wrong lnotab with for loops and storing constants that should
# have been removed
add_magic_from_int(62121, "2.5c1")

# Fix wrong code: "for x, in ..." in listcomp/genexp)
add_magic_from_int(62131, "2.5c2")

# Dropbox-modified Python 2.5 used in versions 1.1x and before of Dropbox
add_magic_from_int(62135, "2.5dropbox")

add_magic_from_int(62151, "2.6a0")  # peephole optimizations & STORE_MAP
add_magic_from_int(62161, "2.6a1")  # WITH_CLEANUP optimization

# Optimize list comprehensions/change LIST_APPEND
add_magic_from_int(62171, "2.7a0")

# Optimize conditional branches: introduce POP_JUMP_IF_FALSE and
# POP_JUMP_IF_TRUE
add_magic_from_int(62181, "2.7a0+1")

add_magic_from_int(62191, "2.7a0+2")  # introduce SETUP_WITH
add_magic_from_int(62201, "2.7a0+3")  # introduce BUILD_SET
add_magic_from_int(62211, "2.7")  # introduce MAP_ADD and SET_ADD

add_magic_from_int(2657, "2.7pyston-0.6.1")

# PyPy including pypy-2.6.1, pypy-5.0.1 PyPy adds 7 to the corresponding CPython nmber
add_magic_from_int(62211 + 7, "2.7pypy")

add_magic_from_int(3000, "3.000")
add_magic_from_int(3010, "3.000+1")  # removed UNARY_CONVERT
add_magic_from_int(3020, "3.000+2")  # added BUILD_SET
add_magic_from_int(3030, "3.000+3")  # added keyword-only parameters
add_magic_from_int(3040, "3.000+4")  # added signature annotations
add_magic_from_int(3050, "3.000+5")  # print becomes a function
add_magic_from_int(3060, "3.000+6")  # PEP 3115 metaclass syntax
add_magic_from_int(3061, "3.000+7")  # string literals become unicode
add_magic_from_int(3071, "3.000+8")  # PEP 3109 raise changes
add_magic_from_int(3081, "3.000+9")  # PEP 3137 make __file__ and __name__ unicode
add_magic_from_int(3091, "3.000+10")  # kill str8 interning
add_magic_from_int(3101, "3.000+11")  # merge from 2.6a0, see 62151
add_magic_from_int(3103, "3.000+12")  # __file__ points to source file
add_magic_from_int(3111, "3.0a4")  # WITH_CLEANUP optimization
add_magic_from_int(3131, "3.0a5")  # lexical exception stacking, including POP_EXCEPT)
add_magic_from_int(3141, "3.1a0")  # optimize list, set and dict comprehensions
add_magic_from_int(3151, "3.1a0+")  # optimize conditional branches
add_magic_from_int(3160, "3.2a0")  # add SETUP_WITH
add_magic_from_int(3170, "3.2a1")  # add DUP_TOP_TWO, remove DUP_TOPX and ROT_FOUR
add_magic_from_int(3180, "3.2a2")  # 3.2a2 (add DELETE_DEREF)

# Python 3.2.5 - PyPy 2.3.4 PyPy adds 7 to the corresponding CPython
# number
add_magic_from_int(3180 + 7, "3.2pypy")

add_magic_from_int(3190, "3.3a0")  # __class__ super closure changed
add_magic_from_int(3200, "3.3a0+")  # __qualname__ added
add_magic_from_int(3220, "3.3a1")  # changed PEP 380 implementation

# Added size modulo 2**32 to the pyc header
# NOTE: 3.3a2 is our name, other places call it 3.3
# but most 3.3 versions are 3.3a4 which comes next.
# FIXME: figure out what the history is and
# what the right thing to do if this isn't it.
add_magic_from_int(3210, "3.3a2")
add_magic_from_int(3230, "3.3a4")  # revert changes to implicit __class__ closure

# Evaluate positional default arg keyword-only defaults)
add_magic_from_int(3250, "3.4a1")

# Add LOAD_CLASSDEREF; add_magic_from_int locals, f class to override free vars
add_magic_from_int(3260, "3.4a1+1")

add_magic_from_int(3270, "3.4a1+2")  # various tweaks to the __class__ closure
add_magic_from_int(3280, "3.4a1+3")  # remove implicit class argument
add_magic_from_int(3290, "3.4a4")  # changes to __qualname__ computation
add_magic_from_int(3300, "3.4a4+")  # more changes to __qualname__ computation
add_magic_from_int(3310, "3.4rc2")  # alter __qualname__ computation
add_magic_from_int(3320, "3.5a0")  # matrix multiplication operator
add_magic_from_int(3330, "3.5b1")  # pep 448: additional unpacking generalizations
add_magic_from_int(3340, "3.5b2")  # fix dictionary display evaluation order #11205
add_magic_from_int(3350, "3.5")  # add GET_YIELD_FROM_ITER opcode #24400 (also 3.5b2)
add_magic_from_int(
    3351, "3.5.2"
)  # fix BUILD_MAP_UNPACK_WITH_CALL opcode #27286; 3.5.3, 3.5.4, 3.5.5
add_magic_from_int(3360, "3.6a0")  # add FORMAT_VALUE opcode #25483
add_magic_from_int(3361, "3.6a0+1")  # lineno delta of code.co_lnotab becomes signed
add_magic_from_int(3370, "3.6a1")  # 16 bit wordcode
add_magic_from_int(3371, "3.6a1+1")  # add BUILD_CONST_KEY_MAP opcode #27140
add_magic_from_int(
    3372, "3.6a1+2"
)  # MAKE_FUNCTION simplification, remove MAKE_CLOSURE #27095
add_magic_from_int(3373, "3.6b1")  # add BUILD_STRING opcode #27078
add_magic_from_int(
    3375, "3.6b1+1"
)  # add SETUP_ANNOTATIONS and STORE_ANNOTATION opcodes #27985
add_magic_from_int(
    3376, "3.6b1+2"
)  # simplify CALL_FUNCTIONs & BUILD_MAP_UNPACK_WITH_CALL
add_magic_from_int(3377, "3.6b1+3")  # set __class__ cell from type.__new__ #23722
add_magic_from_int(3378, "3.6b2")  # add BUILD_TUPLE_UNPACK_WITH_CALL #28257
add_magic_from_int(3379, "3.6rc1")  # more thorough __class__ validation #23722
add_magic_from_int(3390, "3.7.0alpha0")
add_magic_from_int(3391, "3.7.0alpha3")

# Initial PEP 552 - Deterministic pycs #31650
# Additional word in header and possibly no timestamp
add_magic_from_int(3392, "3.7.0beta2")

# Final PEP 552: timestamp + size field or no timestamp + SipHash
# remove STORE_ANNOTATION opcode #3255
add_magic_from_int(3393, "3.7.0beta3")

# restored docstring as the first stmt in the body; this might
# affected the first line number #32911)
add_magic_from_int(3394, "3.7.0")

# move frame block handling to compiler #17611
add_magic_from_int(3400, "3.8.0a1")

# add END_ASYNC_FOR #33041
add_magic_from_int(3401, "3.8.0a3+")

# PEP570 Python Positional-Only Parameters #36540
add_magic_from_int(3410, "3.8.0a1+")

# Reverse evaluation order of key: value in dict comprehensions
# #35224
add_magic_from_int(3411, "3.8.0b2+")

# Swap the position of positional args and positional only args in
# ast.arguments #37593)
add_magic_from_int(3412, "3.8.0beta2")

# Fix "break" and "continue" in "finally" #37830
add_magic_from_int(3413, "3.8.0rc1+")

# add LOAD_ASSERTION_ERROR #34880
add_magic_from_int(3420, "3.9.0a0")

# simplified bytecode for with blocks #32949
add_magic_from_int(3421, "3.9.0a0")

# Remove BEGIN_FINALLY, END_FINALLY, CALL_FINALLY, POP_FINALLY bytecodes #33387
add_magic_from_int(3422, "3.9.0alpha1")

# add IS_OP, CONTAINS_OP and JUMP_IF_NOT_EXC_MATCH bytecodes #39156
add_magic_from_int(3423, "3.9.0a0")

# simplify bytecodes for *value unpacking
add_magic_from_int(3424, "3.9.0a2")

# simplify bytecodes for **value unpacking
add_magic_from_int(3425, "3.9.0beta5")

# Weird ones
# WTF? Python 3.2.5 and PyPy have weird magic numbers

add_magic_from_int(48, "3.2a2")
add_magic_from_int(64, "3.3pypy")
add_magic_from_int(112, "3.5pypy")  # pypy3.5-c-jit-latest
add_magic_from_int(160, "3.6.1pypy")  # '3.6.1 ... PyPy 7.1.0-beta0'
add_magic_from_int(192, "3.6pypy")  # '3.6.9 ... PyPy 7.1.0-beta0'
add_magic_from_int(1011, "2.7.1b3Jython")  # jython
add_magic_from_int(22138, "2.7.7Pyston")  # 2.7.8pyston, pyston-0.6.0


magics = __by_version(versions)

# From a Python version given in sys.info, e.g. 3.6.1,
# what is the "canonic" version number, e.g. '3.6.0rc1'
canonic_python_version = {}


def add_canonic_versions(versions, canonic):
    for v in versions.split():
        canonic_python_version[v] = canonic
        magics[v] = magics[canonic]
        try:
            magics[float(v)] = magics[canonic]
        except:
            pass
        pass

    return


add_canonic_versions("1.5.1 1.5.2", "1.5")
add_canonic_versions("2.0.1", "2.0")
add_canonic_versions("2.1.1 2.1.2 2.1.3", "2.1")
add_canonic_versions("2.2.3", "2.2")
add_canonic_versions("2.3 2.3.7", "2.3a0")
add_canonic_versions("2.4 2.4.0 2.4.1 2.4.2 2.4.3 2.4.5 2.4.6", "2.4b1")
add_canonic_versions("2.5 2.5.0 2.5.1 2.5.2 2.5.3 2.5.4 2.5.5 2.5.6", "2.5c2")
add_canonic_versions("2.6 2.6.6 2.6.7 2.6.8 2.6.9", "2.6a1")
add_canonic_versions(
    "2.7.0 2.7.1 2.7.2 2.7.2 2.7.3 2.7.4 2.7.5 2.7.6 2.7.7 "
    "2.7.8 2.7.9 2.7.10 2.7.11 2.7.12 2.7.13 2.7.14 2.7.15 "
    "2.7.15candidate1 "
    "2.7.16 "
    "2.7.17rc1 2.7.17candidate1 2.7.17 2.7.18 2.7.18candidate1",
    "2.7",
)
add_canonic_versions("3.0 3.0.0 3.0.1", "3.0a5")
add_canonic_versions("3.1 3.1.0 3.1.1 3.1.2 3.1.3 3.1.4 3.1.5", "3.1a0+")
add_canonic_versions("3.2 3.2.0 3.2.1 3.2.2 3.2.3 3.2.4 3.2.5 3.2.6", "3.2a2")
add_canonic_versions(
    "3.3 3.3.0 3.3.1 3.3.2 3.3.3 3.3.4 3.3.5 3.3.6 3.3.7rc1 3.3.7", "3.3a4"
)
add_canonic_versions(
    "3.4 3.4.0 3.4.1 3.4.2 3.4.3 3.4.4 3.4.5 3.4.6 3.4.7 3.4.8 3.4.9 3.4.10", "3.4rc2"
)
add_canonic_versions("3.5 3.5.0 3.5.1", "3.5")
add_canonic_versions("3.5.2 3.5.3 3.5.4 3.5.5 3.5.6 3.5.7 3.5.8 3.5.9 3.5.10", "3.5.2")
add_canonic_versions(
    "3.6b2 3.6 3.6.0 3.6.1 3.6.2 3.6.3 3.6.4 3.6.5 3.6.6 3.6.7 3.6.8 3.6.9 3.6.10 3.6.11 3.6.12",
    "3.6rc1",
)

add_canonic_versions("3.7b1", "3.7.0beta3")
add_canonic_versions("3.8a1", "3.8.0beta2")

add_canonic_versions("2.7.10pypy 2.7.13pypy", "2.7pypy")
add_canonic_versions("2.7.3b0Jython", "2.7.1b3Jython")
add_canonic_versions("3.2.5pypy", "3.2pypy")
add_canonic_versions("3.3.5pypy", "3.3pypy")
add_canonic_versions("3.5.3pypy", "3.5pypy")
add_canonic_versions("3.6.9pypy", "3.6pypy")
add_canonic_versions("2.7.8Pyston", "2.7.7Pyston")
add_canonic_versions("3.7.0alpha3", "3.7.0alpha3")
add_canonic_versions(
    "3.7 3.7.0beta5 3.7.1 3.7.2 3.7.3 3.7.4 3.7.5 3.7.6 3.7.7 3.7.8 3.7.9", "3.7.0"
)
add_canonic_versions("3.8.0alpha0 3.8.0alpha3 3.8.0a0", "3.8.0a3+")
add_canonic_versions("3.8b4 3.8.0candidate1 3.8 3.8.0 3.8.1 3.8.2 3.8.3 3.8.4 3.8.5 3.8.6 3.8.7", "3.8.0rc1+")
add_canonic_versions(
    "3.9 3.9.0 3.9.0a1+ 3.9.0a2+ 3.9.0alpha1 3.9.0alpha2", "3.9.0alpha1"
)
add_canonic_versions(
    "3.9 3.9.0 3.9.1 3.9.0b5+", "3.9.0beta5"
)

# The canonic version for a canonic version is itself
for v in versions.values():
    canonic_python_version[v] = v
# A set of all Python versions we know about
python_versions = set(canonic_python_version.keys())


def __show(text, magic):
    print(text, struct.unpack("BBBB", magic), struct.unpack("<HBB", magic))


def magic_int2float(magic_int):
    """Convert a Python magic int into a 'canonic' floating-point number,
    e.g. 2.7, 3.7. runtime error is raised if "version" is not found.

    Note that there can be several magic_int's that map to a single floating-
    point number. For example 3320 (3.5.a0), 3340 (3.5b1), and 3351 (3.5.2)
    all map to 3.5.
    """
    return py_str2float(magicint2version[magic_int])


def py_str2float(orig_version):
    """Convert a Python version into a two-digit 'canonic' floating-point number,
    e.g. 2.5, 3.6.

    A runtime error is raised if "version" is not found.

    Note that there can be several strings that map to a single floating-
    point number. For example 3.2a1, 3.2.0, 3.2.2, 3.2.6 among others all map to
    3.2.
    """
    version = re.sub(r"(pypy|dropbox)$", "", orig_version)
    if version in magics:
        magic = magics[version]
        for v, m in list(magics.items()):
            if m == magic:
                try:
                    return float(canonic_python_version[v])
                except:
                    try:
                        m = re.match(r"^(\d\.)(\d+)\.(\d+)", v)
                        if m:
                            return float(m.group(1) + m.group(2))
                        else:
                            # Match things like 3.5a0, 3.5b2, 3.6a1+1, 3.6rc1, 3.7.0beta3
                            m = re.match(r"^(\d\.)(\d)(\d+)?[abr]", v)
                            if m:
                                return float(m.group(1) + m.group(2))
                            pass
                    except:
                        pass
                    pass
                pass
            pass
    raise RuntimeError(
        "Can't find a valid Python version for version %s" % orig_version
    )
    return


def sysinfo2float(version_info=sys.version_info):
    """Convert a sys.versions_info-compatible list into a 'canonic'
    floating-point number which that can then be used to look up a
    magic number.  Note that this can only be used for released version
    of C Python, not interim development versions, since we can't
    represent that as a floating-point number.

    For handling Pypy, pyston, jython, etc. and interim versions of
    C Python, use sysinfo2magic.
    """
    vers_str = ".".join([str(v) for v in version_info[0:3]])
    if version_info[3] != "final":
        vers_str += "." + "".join([str(i) for i in version_info[3:]])

    if IS_PYPY:
        vers_str += "pypy"
    else:
        try:
            import platform

            platform = platform.python_implementation()
            if platform in ("Jython", "Pyston"):
                vers_str += platform
                pass
        except ImportError:
            # Python may be too old, e.g. < 2.6 or implementation may
            # just not have platform
            pass
        except AttributeError:
            pass
    return py_str2float(vers_str)


def sysinfo2magic(version_info=sys.version_info):
    """Convert a list sys.versions_info compatible list into a 'canonic'
    floating-point number which that can then be used to look up a
    magic number.  Note that this can raise an exception.
    """

    # FIXME: DRY with sysinfo2float()
    vers_str = ".".join([str(v) for v in version_info[0:3]])
    if version_info[3] != "final":
        vers_str += "".join([str(v) for v in version_info[3:]])

    if IS_PYPY:
        vers_str += "pypy"

    return magics[vers_str]


def test():
    magic_20 = magics["2.0"]
    magic_current = by_magic[MAGIC]
    print(type(magic_20), len(magic_20), repr(magic_20))
    print()
    print("This Python interpreter has version", magic_current)
    print("Magic code: ", PYTHON_MAGIC_INT)
    print(type(magic_20), len(magic_20), repr(magic_20))
    print(sysinfo2float())
    assert sysinfo2magic() == MAGIC


if __name__ == "__main__":
    test()
