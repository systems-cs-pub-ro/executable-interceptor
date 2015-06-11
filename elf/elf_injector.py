#!/usr/bin/python

# -----------------------------------------------------------------------------
# Simple application that injects a given interceptor into an ELF32 executable
#
# Author: Octavian Crintea
# -----------------------------------------------------------------------------

from io import SEEK_CUR
import struct
import subprocess
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

        # TODO: magic number 2
        text_seg = self.get_segment(2)
        self.TEXT_SEG_END_ADDR = text_seg['p_vaddr'] + text_seg['p_memsz']
        self.TEXT_SEG_END_OFFSET = text_seg['p_offset'] + text_seg['p_filesz']

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

    def modify_got(self, dynamic_linker_addr):
        for i in xrange(self.GOT_FIRST_ENTRY, self.GOT_NUM_ENTRIES):
            self.modify_got_entry(i, dynamic_linker_addr)

    def modify_got_entry(self, i, dynamic_linker_addr):
        self.seek_for_got_entry(i)
        dynamic_linker_addr_bytes = int32_to_bytes(dynamic_linker_addr)
        self.stream.write(dynamic_linker_addr_bytes)

    def modify_plt(self, interceptor_offset):
        for i in xrange(self.PLT_FIRST_ENTRY, self.PLT_NUM_ENTRIES):
            self.modify_plt_entry(i, interceptor_offset)

    def modify_plt_entry(self, i, run_interceptor_offset):
        self.seek_for_plt_entry(i)
        self.stream.write('\xff\x35')  # opcode for push on i386

        # TODO: these numbers will differ for another architecture
        self.stream.seek(10, SEEK_CUR)
        interceptor_rel_off = run_interceptor_offset - self.stream.tell() - 4
        interceptor_rel_off_bytes = int32_to_bytes(interceptor_rel_off)
        self.stream.write(interceptor_rel_off_bytes)  # jmp interceptor

    def inject_code(self, code):
        self.stream.seek(self.TEXT_SEG_END_OFFSET)
        self.stream.write(code)

    def inject(self, interceptor_obj):
        subprocess.call(['make',
                         '-f',
                         'Makefile.interceptor',
                         'PLT0=' + str(self.PLT_ADDR),
                         'REL_PLT=' + str(self.REL_PLT_ADDR),
                         'DYN_SYM=' + str(self.DYNSYM_ADDR),
                         'DYN_STR=' + str(self.DYNSTR_ADDR),
                         'INTERCEPTOR_OBJ=' + interceptor_obj])

        with open('all.out', 'rb') as all_out_stream:
            all_out = ELFFile(all_out_stream)
            text = all_out.get_section_by_name('.text')
            symtab = all_out.get_section_by_name('.symtab')

            dynamic_linker = symtab.get_symbol_by_name('dynamic_linker')[0]
            dynamic_linker_off = dynamic_linker['st_value'] - text['sh_addr']
            dynamic_linker_addr = self.TEXT_SEG_END_ADDR + dynamic_linker_off
            self.modify_got(dynamic_linker_addr)

            run_interceptor = symtab.get_symbol_by_name('run_interceptor')[0]
            run_interceptor_off = run_interceptor['st_value'] - text['sh_addr']
            run_interceptor_offset = \
                self.TEXT_SEG_END_OFFSET + run_interceptor_off
            self.modify_plt(run_interceptor_offset)

            code = text.data()
            self.inject_code(code)

            subprocess.call(['make', '-f', 'Makefile.interceptor', 'clean'])


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
