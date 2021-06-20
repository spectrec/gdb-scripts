# For auto load, add into `.gdbinit': `source path-to-this-script.py`

from __future__ import print_function
import sys
import subprocess

print("Loading global optimized-out variables support.", file=sys.stderr)

def searchAddressFor(objdump_output, symbol):
	for line in objdump_output.splitlines():
		chunks = line.split()

		if len(chunks) != 6:
			# 00000000002a9ae0 l     O .data  0000000000000010              fibers
			continue

		if chunks[-1] == symbol:
			return int(chunks[0], 16)

		# hack for symbol.lto_priv.0`'
		if chunks[-1].startswith(symbol + "."):
			return int(chunks[0], 16)

	return None


class DetectSymbolAddressCmd(gdb.Command):
	"""Detect `optimized out' symbol address, using address of the `known' symbol from the same elf.
Usage: detect-symbol-address <optimized out name> <known symbol name>"""

	def __init__(self):
		gdb.Command.__init__(self, "detect-symbol-address", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL)

	def invoke(self, arg, _from_tty):
		args = gdb.string_to_argv(arg)
		if len(args) != 2:
			print("Invalid usage: expected 2 arguments, got {}".format(len(args)))
			return

		# output: `fibers in section .data of /usr/local/lib64/libmescalito.69a361d.20210602.2110.1.el7.so`
		symbol_info = gdb.execute('info symbol &{}'.format(args[1]), False, True)
		elf_path = symbol_info.split()[-1]

		p = subprocess.Popen(['objdump', '-tT', elf_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		if p.returncode != 0:
			print("objump failed: ", err)
			return

		known_var_elf_address = searchAddressFor(out, args[1])
		if known_var_elf_address is None:
			print("Can't detect elf address for variable `{}' from file `{}'".format(args[1], elf_path))
			return

		unknown_var_elf_address = searchAddressFor(out, args[0])
		if unknown_var_elf_address is None:
			print("Can't detect elf address for variable `{}' from file `{}'".format(args[0], elf_path))
			return

		# output: `Symbol "fibers" is static storage at address 0x7f725f413ae0.`
		out = gdb.execute('info address {}'.format(args[1]), False, True)
		known_var_gdb_address_str = out.split()[-1]
		known_var_gdb_address = int(known_var_gdb_address_str[:len(known_var_gdb_address_str) - 1], 16)

		unknown_var_gdb_address = known_var_gdb_address - known_var_elf_address + unknown_var_elf_address
		print("Variable `{}' is located at {}".format(args[0], hex(unknown_var_gdb_address)))

#
# Register CLI commands
#

DetectSymbolAddressCmd()
