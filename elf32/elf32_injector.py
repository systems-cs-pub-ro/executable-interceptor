#!/usr/bin/python

#------------------------------------------------------------------------------
# Simple application that injects a given interceptor into an ELF32 executable
#
# Author: Octavian Crintea
#------------------------------------------------------------------------------

import sys
import os
import struct
from subprocess import call
from elftools.elf.elffile import ELFFile


class ELF32_Injector:

    _GOT_ENTRY_SIZE = 0x04
    _PLT_ENTRY_SIZE = 0x10
    _DYN_CODE_SIZE = 6          # size of the code that jumps to PLT[0]
    _GOT_FIRST_ENTRY = 3
    _PLT_FIRST_ENTRY = 1

    def __init__(self, elf_filename):
        self._elf_stream = open(elf_filename, 'r+b')
        elf = ELFFile(self._elf_stream)
        self._got_offset = ELF32_Injector._section_offset(elf, '.got.plt')
        self._got_size = ELF32_Injector._section_size(elf, '.got.plt')
        self._got_num_entries = self._got_size / ELF32_Injector._GOT_ENTRY_SIZE
        self._plt_offset = ELF32_Injector._section_offset(elf, '.plt')
        self._plt_size = ELF32_Injector._section_size(elf, '.plt')
        self._plt_num_entries = self._plt_size / ELF32_Injector._PLT_ENTRY_SIZE

        eh_frame_addr = ELF32_Injector._section_addr(elf, '.eh_frame')
        eh_frame_offset = ELF32_Injector._section_offset(elf, '.eh_frame')
        eh_frame_size = ELF32_Injector._section_size(elf, '.eh_frame')
        self._dyn_addr = eh_frame_addr + eh_frame_size
        self._dyn_offset = eh_frame_offset + eh_frame_size
        self._intcerp_offset = self._dyn_offset + ELF32_Injector._DYN_CODE_SIZE

        init_array_offset = ELF32_Injector._section_offset(elf, '.init_array')
        self._intcerp_max_size = init_array_offset - self._intcerp_offset

        self._rel_plt_addr = ELF32_Injector._section_addr(elf, '.rel.plt')
        self._dynsym_addr = ELF32_Injector._section_addr(elf, '.dynsym')
        self._dynstr_addr = ELF32_Injector._section_addr(elf, '.dynstr')

    def __del__(self):
        self._elf_stream.close()

    @staticmethod
    def _get_section(elf, section):
        return elf.get_section_by_name(section)

    @staticmethod
    def _section_addr(elf, section):
        return ELF32_Injector._get_section(elf, section)['sh_addr']

    @staticmethod
    def _section_offset(elf, section):
        return ELF32_Injector._get_section(elf, section)['sh_offset']

    @staticmethod
    def _section_size(elf, section):
        return ELF32_Injector._get_section(elf, section)['sh_size']

    def _got_entry_offset(self, i):
        return self._got_offset + i * ELF32_Injector._GOT_ENTRY_SIZE

    def _seek_for_got_entry(self, i):
        self._elf_stream.seek(self._got_entry_offset(i), 0)

    def _plt_entry_offset(self, i):
        return self._plt_offset + i * ELF32_Injector._PLT_ENTRY_SIZE

    def _seek_for_plt_entry(self, i):
        self._elf_stream.seek(self._plt_entry_offset(i), 0)

    def _modify_got(self):
        for i in xrange(ELF32_Injector._GOT_FIRST_ENTRY,
                        self._got_num_entries):
            self._modify_got_entry(i)

    def _modify_got_entry(self, i):
        self._seek_for_got_entry(i)
        dyn_addr_bytes = int32_to_bytes(self._dyn_addr)
        self._elf_stream.write(dyn_addr_bytes)

    def _modify_plt(self):
        for i in xrange(ELF32_Injector._PLT_FIRST_ENTRY,
                        self._plt_num_entries):
            self._modify_plt_entry(i)

    def _modify_plt_entry(self, i):
        self._seek_for_plt_entry(i)
        self._elf_stream.write('\xff\x35')  # opcode for push

        self._elf_stream.seek(10, 1)
        intcerp_offset = self._intcerp_offset - self._elf_stream.tell() - 4
        intcerp_offset_bytes = int32_to_bytes(intcerp_offset)
        self._elf_stream.write(intcerp_offset_bytes)  # jmp interceptor

    def _inject_code(self, intcerp_code):
        self._elf_stream.seek(self._dyn_offset, 0)
        self._elf_stream.write('\x50')        # push eax
        plt0_offset = self._plt_offset - self._elf_stream.tell() - 5
        plt0_offset_bytes = int32_to_bytes(plt0_offset)
        self._elf_stream.write('\xe9' + plt0_offset_bytes)  # jmp PLT[0]

        self._elf_stream.seek(self._intcerp_offset, 0)
        self._elf_stream.write(intcerp_code)  # interceptor code

    def inject_direct(self, intcerp_code):
        self._modify_got()
        self._modify_plt()
        self._inject_code(intcerp_code)

    def inject(self, intcerp_obj):
        call(['make',
              '-f',
              'Makefile.interceptor',
              'REL_PLT=' + str(self._rel_plt_addr),
              'DYN_SYM=' + str(self._dynsym_addr),
              'DYN_STR=' + str(self._dynstr_addr),
              'INTERCEPTOR_OBJ=' + intcerp_obj])
        self.inject_direct(readfile('run.hex'))
        call(['make', '-f', 'Makefile.interceptor', 'clean'])


def int32_to_bytes(num):
    return struct.pack('i', num)


def readfile(filename):
    with open(filename, 'rb') as stream:
        return stream.read()


def inject_direct(elf_filename, intcerp_filename):
    elf = ELF32_Injector(elf_filename)
    elf.inject_direct(readfile(intcerp_filename))


def inject(elf_filename, intcerp_obj):
    elf = ELF32_Injector(elf_filename)
    elf.inject(intcerp_obj)


def usage(name):
    print 'Usage: %s elf32-file intcerp-obj' % name
    print '       %s --direct elf32-file intcerp-file' % name


def main(args):
    if len(args) < 3 or len(args) > 4:
        usage(args[0])
        sys.exit(1)

    if len(args) == 4 and args[1] != '--direct':
        usage(args[0])
        sys.exit(1)

    if len(args) == 3:
        inject(args[1], args[2])
    else:
        inject_direct(args[2], args[3])

if __name__ == '__main__':
    main(sys.argv)
