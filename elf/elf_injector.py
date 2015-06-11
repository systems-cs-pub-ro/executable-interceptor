#!/usr/bin/python

# -----------------------------------------------------------------------------
# Simple application that injects a given interceptor into an ELF32 executable
#
# Author: Octavian Crintea
# -----------------------------------------------------------------------------

from subprocess import call
import struct
import sys

from elftools.elf.elffile import ELFFile


class ELF_Injector(ELFFile):

    def __init__(self, elf_filename):
        ELFFile.__init__(self, open(elf_filename, 'r+b'))

        got = self.get_section_by_name('.got.plt')
        self.GOT_OFFSET = got['sh_offset']
        self.GOT_SIZE = got['sh_size']
        self.GOT_ENTRY_SIZE = got['sh_entsize']
        self.GOT_NUM_ENTRIES = self.GOT_SIZE / self.GOT_ENTRY_SIZE
        self.GOT_FIRST_ENTRY = 3

        plt = self.get_section_by_name('.plt')
        self.PLT_ADDR = plt['sh_addr']
        self.PLT_OFFSET = plt['sh_offset']
        self.PLT_SIZE = plt['sh_size']
        self.PLT_FIRST_ENTRY = 1

        # PLT_ENTRY_SIZE cannot be retrieved from plt['sh_entsize']
        self.PLT_NUM_ENTRIES = \
            self.GOT_NUM_ENTRIES - self.GOT_FIRST_ENTRY + self.PLT_FIRST_ENTRY
        self.PLT_ENTRY_SIZE = self.PLT_SIZE / self.PLT_NUM_ENTRIES

        text_seg = self.get_segment(2)

        # TODO: extract the offset of dynamic linker from the object file
        self.DYNAMIC_LINKER_ADDR = text_seg['p_vaddr'] + text_seg['p_memsz']
        self.DYNAMIC_LINKER_OFFSET = \
            text_seg['p_offset'] + text_seg['p_filesz']

        # TODO: extract the offset of interceptor from the object file
        self.interceptor_offset = self.DYNAMIC_LINKER_OFFSET + 8

        self.REL_PLT_ADDR = self.section_addr('.rel.plt')
        self.DYNSYM_ADDR = self.section_addr('.dynsym')
        self.DYNSTR_ADDR = self.section_addr('.dynstr')

    def __del__(self):
        self.stream.close()

    def section_addr(self, section):
        return self.get_section_by_name(section)['sh_addr']

    def section_offset(self, section):
        return self.get_section_by_name(section)['sh_offset']

    def section_size(self, section):
        return self.get_section_by_name(section)['sh_size']

    def got_entry_offset(self, i):
        return self.GOT_OFFSET + i * self.GOT_ENTRY_SIZE

    def seek_for_got_entry(self, i):
        self.stream.seek(self.got_entry_offset(i))

    def plt_entry_offset(self, i):
        return self.PLT_OFFSET + i * self.PLT_ENTRY_SIZE

    def seek_for_plt_entry(self, i):
        self.stream.seek(self.plt_entry_offset(i))

    def modify_got(self):
        for i in xrange(self.GOT_FIRST_ENTRY, self.GOT_NUM_ENTRIES):
            self.modify_got_entry(i)

    def modify_got_entry(self, i):
        self.seek_for_got_entry(i)
        dynamic_linker_addr_bytes = int32_to_bytes(self.DYNAMIC_LINKER_ADDR)
        self.stream.write(dynamic_linker_addr_bytes)

    def modify_plt(self):
        for i in xrange(self.PLT_FIRST_ENTRY, self.PLT_NUM_ENTRIES):
            self.modify_plt_entry(i)

    def modify_plt_entry(self, i):
        self.seek_for_plt_entry(i)
        self.stream.write('\xff\x35')  # opcode for push on i386

        # TODO: these numbers will differ for another architecture
        self.stream.seek(10, 1)
        interceptor_rel_off = self.interceptor_offset - self.stream.tell() - 4
        interceptor_rel_off_bytes = int32_to_bytes(interceptor_rel_off)
        self.stream.write(interceptor_rel_off_bytes)  # jmp interceptor

    def inject_code(self, interceptor_code):
        self.stream.seek(self.DYNAMIC_LINKER_OFFSET)
        self.stream.write(interceptor_code)

    def inject(self, interceptor_obj):
        call(['make',
              '-f',
              'Makefile.interceptor',
              'PLT0=' + str(self.PLT_ADDR),
              'REL_PLT=' + str(self.REL_PLT_ADDR),
              'DYN_SYM=' + str(self.DYNSYM_ADDR),
              'DYN_STR=' + str(self.DYNSTR_ADDR),
              'INTERCEPTOR_OBJ=' + interceptor_obj])
        self.modify_got()
        self.modify_plt()
        self.inject_code(readfile('run.hex'))
        call(['make', '-f', 'Makefile.interceptor', 'clean'])


def int32_to_bytes(num):
    return struct.pack('i', num)


def readfile(filename):
    with open(filename, 'rb') as stream:
        return stream.read()


def inject(elf_filename, interceptor_obj):
    elf = ELF_Injector(elf_filename)
    elf.inject(interceptor_obj)


def usage(name):
    print 'Usage: %s elf-file interceptor-obj' % name


def main(args):
    if len(args) != 3:
        usage(args[0])
        sys.exit(1)

    inject(args[1], args[2])


if __name__ == '__main__':
    main(sys.argv)
