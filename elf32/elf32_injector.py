#!/usr/bin/python

#-------------------------------------------------------------------------------
# Simple application that injects a given interceptor into an ELF32 executable
#
# Author: Octavian Crintea
#-------------------------------------------------------------------------------

import sys
import os
import struct
from elftools.elf.elffile import ELFFile

class ELF32_Injector:
    def __init__(self, elf_filename):
        self._elf_stream = open(elf_filename, 'r+b')
        elf = ELFFile(self._elf_stream)
        self._got_offset = ELF32_Injector._section_offset(elf, '.got.plt')
        self._got_size = ELF32_Injector._section_size(elf, '.got.plt')
        self._got_num_entries = self._got_size / 0x04
        self._plt_offset = ELF32_Injector._section_offset(elf, '.plt')
        self._plt_size = ELF32_Injector._section_size(elf, '.plt')
        self._plt_num_entries = self._plt_size / 0x10
        self._intcerp_offset = ELF32_Injector._section_offset(elf, '.eh_frame') + ELF32_Injector._section_size(elf, '.eh_frame')
        self._intcerp_max_size = ELF32_Injector._section_offset(elf, '.init_array') - self._intcerp_offset

    def __del__(self):
        self._elf_stream.close()

    @staticmethod
    def _get_section(elf, section):
        return elf.get_section_by_name(section)

    @staticmethod
    def _section_offset(elf, section):
        return ELF32_Injector._get_section(elf, section)['sh_offset']

    @staticmethod
    def _section_size(elf, section):
        return ELF32_Injector._get_section(elf, section)['sh_size']

    def _got_entry_offset(self, i):
        return self._got_offset + i * 0x04

    def _seek_for_got_entry(self, i):
        self._elf_stream.seek(self._got_entry_offset(i), 0)

    def _plt_entry_offset(self, i):
        return self._plt_offset + i * 0x10

    def _seek_for_plt_entry(self, i):
        self._elf_stream.seek(self._plt_entry_offset(i), 0)

    def _modify_got(self, int_code):
        for i in xrange(3, self._got_num_entries):
            self._modify_got_entry(i, len(int_code))

    def _modify_got_entry(self, i, int_size):
        self._seek_for_got_entry(i)

        # the offset of 'push eax' instruction after the interceptor code
        offset = struct.pack('i', 0x08048000 + self._intcerp_offset + int_size + 2)
        self._elf_stream.write(offset)

    def _modify_plt(self):
        for i in xrange(1, self._plt_num_entries):
            self._modify_plt_entry(i)

    def _modify_plt_entry(self, i):
        self._seek_for_plt_entry(i)
        self._elf_stream.write('\xff\x35') # opcode for push
        self._elf_stream.seek(10, 1)
        intcerp_offset = struct.pack('i', self._intcerp_offset - self._elf_stream.tell() - 4)
        self._elf_stream.write(intcerp_offset) # jmp interceptor

    def _inject_code(self, intcerp_code):
        self._elf_stream.seek(self._intcerp_offset, 0)
        self._elf_stream.write(intcerp_code) # interceptor code
        self._elf_stream.write('\x58')       # pop eax
        self._elf_stream.write('\xc3')       # ret
        self._elf_stream.write('\x50')       # push eax
        plt0_offset = struct.pack('i', self._plt_offset - self._elf_stream.tell() - 5)
        self._elf_stream.write('\xe9' + plt0_offset) # jmp PLT[0]

    def inject(self, intcerp_code):
        self._modify_got(intcerp_code)
        self._modify_plt()
        self._inject_code(intcerp_code)

def inject(elf_filename, intcerp_filename):
    with open(intcerp_filename, 'rb') as intcerp_stream:
        intcerp_code = intcerp_stream.read()

    elf = ELF32_Injector(elf_filename)
    elf.inject(intcerp_code)

def main(args):
    if len(args) != 3:
        print 'Usage: %s <elf32-file> <intcerp-file>' % args[0]
        sys.exit(1)

    inject(args[1], args[2])

if __name__ == '__main__':
    main(sys.argv)
