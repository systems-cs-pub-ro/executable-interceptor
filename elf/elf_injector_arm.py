#!/usr/bin/python

# -----------------------------------------------------------------------------
# Simple application that injects a given interceptor into an ELF32 executable
#
# Author: Octavian Crintea
# -----------------------------------------------------------------------------

import struct
import subprocess
import sys

from elftools.elf.elffile import ELFFile


class ELF_Injector(ELFFile):

    def __init__(self, elf_filename):
        ELFFile.__init__(self, open(elf_filename, 'r+b'))

        plt = self.get_section_by_name('.plt')
        self.PLT_ADDR = plt['sh_addr'] + 8
        self.PLT_OFFSET = plt['sh_offset'] + 8
        self.PLT_SIZE = plt['sh_size'] - 8
        self.PLT_FIRST_ENTRY = 1
        self.PLT_ENTRY_SIZE = 12
        self.PLT_NUM_ENTRIES = self.PLT_SIZE / self.PLT_ENTRY_SIZE

        # TODO: magic number 3
        text_seg = self.get_segment(3)
        self.TEXT_SEG_END_ADDR = text_seg['p_vaddr'] + text_seg['p_memsz']
        self.TEXT_SEG_END_ADDR &= ~0x03
        self.TEXT_SEG_END_OFFSET = text_seg['p_offset'] + text_seg['p_filesz']
        self.TEXT_SEG_END_OFFSET &= ~0x03

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

    def modify_plt(self, interceptor_offset):
        for i in xrange(self.PLT_FIRST_ENTRY, self.PLT_NUM_ENTRIES):
            self.modify_plt_entry(i, interceptor_offset)

    def modify_plt_entry(self, i, run_interceptor_offset):
        self.seek_for_plt_entry(i)
        self.stream.write(int32_to_bytes(0xe59fc000))  # mov ip, pc
        b = 0xea000000  # branch without offset
        b |= (run_interceptor_offset - self.stream.tell() - 8) >> 2
        self.stream.write(int32_to_bytes(b))
        self.stream.write(int32_to_bytes(i - 1))

    def inject_code(self, code):
        self.stream.seek(self.TEXT_SEG_END_OFFSET)
        self.stream.write(code)

    def inject(self, interceptor_obj):
        self.stream.seek(self.plt_entry_offset(1))

        C2 = bytes_to_int32(self.stream.read(4)) & 0xff
        C1 = bytes_to_int32(self.stream.read(4)) & 0xff
        C0 = bytes_to_int32(self.stream.read(4)) & 0xfff
        C = (C2 << 20) + (C1 << 12) + C0
        C += self.plt_entry_offset(1) \
            + self.TEXT_SEG_END_ADDR - self.TEXT_SEG_END_OFFSET + 8
        VA = self.TEXT_SEG_END_ADDR

        subprocess.call(['cpp',
                         '-DC=' + str(C),
                         '-DVA=' + str(VA),
                         'run_interceptor_arm.s',
                         '-o',
                         'run.s~'])
        subprocess.call(['as',
                         'run.s~',
                         '-o',
                         'all.out~'])

        with open('all.out~', 'rb') as all_out_stream:
            run_interceptor_offset = self.TEXT_SEG_END_OFFSET
            self.modify_plt(run_interceptor_offset)

            all_out = ELFFile(all_out_stream)
            text = all_out.get_section_by_name('.text')
            code = text.data()
            self.inject_code(code)


def int32_to_bytes(num):
    return struct.pack('I', num)


def bytes_to_int32(s):
    return struct.unpack('I', s)[0]


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
