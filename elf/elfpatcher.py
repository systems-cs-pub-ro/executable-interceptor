#!/usr/bin/python

# -----------------------------------------------------------------------------
# Simple application that injects a given interceptor into an ELF executable
#
# Author: Octavian Crintea
# -----------------------------------------------------------------------------

from io import SEEK_CUR
import subprocess
import sys

from utils import bytes_to_int32
from utils import int32_to_bytes
from xelffile import XELFFile


def create_patcher(elf_filename):
    elf = XELFFile(open(elf_filename, 'r+b'))
    arch = elf.get_machine_arch()

    if arch == 'x86':
        return ELFPatcher_x86(elf)
    elif arch == 'x64':
        return ELFPatcher_x64(elf)
    elif arch == 'ARM':
        return ELFPatcher_ARM(elf)
    else:
        return None


class ELFPatcher(object):

    def __init__(self, elf):
        self.elf = elf
        self.stream = elf.stream

    def __del__(self):
        self.stream.close()

    def inject(self, obj_filename):
        pass


class ELFPatcher_x86(ELFPatcher):

    def __init__(self, elf):
        ELFPatcher.__init__(self, elf)

    def modify_got(self, dynamic_linker_addr):
        got = self.elf.get_got_section()
        for i in xrange(got.first_entry(), got.num_entries()):
            got.seek_for_entry(i)
            dynamic_linker_addr_bytes = int32_to_bytes(dynamic_linker_addr)
            self.stream.write(dynamic_linker_addr_bytes)

    def modify_plt(self, run_interceptor_offset):
        plt = self.elf.get_plt_section()
        for i in xrange(plt.first_entry(), plt.num_entries()):
            plt.seek_for_entry(i)
            self.stream.write('\xff\x35')  # opcode for push on i386
            self.stream.seek(10, SEEK_CUR)
            interceptor_rel_off = run_interceptor_offset - \
                self.stream.tell() - 4
            interceptor_rel_off_bytes = int32_to_bytes(interceptor_rel_off)
            self.stream.write(interceptor_rel_off_bytes)  # jmp interceptor

    def inject_code(self, code):
        self.stream.seek(self.elf.get_padding_offset())
        self.stream.write(code)

    def inject(self, interceptor_obj):

        PLT_ADDR = self.elf.get_plt_section()['sh_addr']
        REL_PLT_ADDR = self.elf.get_rel_plt_section()['sh_addr']
        DYNSYM_ADDR = self.elf.get_section_by_name('.dynsym')['sh_addr']
        DYNSTR_ADDR = self.elf.get_section_by_name('.dynstr')['sh_addr']
        ENTRY_ADDR = self.elf['e_entry']
        ADDITIONAL_DATA_ADDR = self.elf.get_section_by_name('.bss').end_addr()

        subprocess.call(['make',
                         '-f',
                         'Makefile.x86',
                         'PLT0=' + str(PLT_ADDR),
                         'REL_PLT=' + str(REL_PLT_ADDR),
                         'DYN_SYM=' + str(DYNSYM_ADDR),
                         'DYN_STR=' + str(DYNSTR_ADDR),
                         'ENTRY=' + str(ENTRY_ADDR),
                         'ADDITIONAL_DATA=' + str(ADDITIONAL_DATA_ADDR),
                         'INTERCEPTOR_OBJ=' + interceptor_obj])

        with open('all.out', 'rb') as all_out_stream:
            all_out = XELFFile(all_out_stream)
            text = all_out.get_section_by_name('.text')

            dynamic_linker = all_out.get_static_symbol('dynamic_linker')
            dynamic_linker_off = dynamic_linker['st_value'] - text['sh_addr']
            dynamic_linker_addr = self.elf.get_padding_addr() \
                + dynamic_linker_off
            self.modify_got(dynamic_linker_addr)

            run_interceptor = all_out.get_static_symbol('run_interceptor')
            run_interceptor_off = run_interceptor['st_value'] - text['sh_addr']
            run_interceptor_offset = \
                self.elf.get_padding_offset() + run_interceptor_off
            self.modify_plt(run_interceptor_offset)

            pre_main = all_out.get_static_symbol('pre_main')
            pre_main_off = pre_main['st_value'] - text['sh_addr']
            pre_main_addr = self.elf.get_padding_addr() + pre_main_off

            # update the entry point
            self.elf.header.e_entry = pre_main_addr
            self.elf.update_header()

            # update _start label, if any
            _start = self.elf.get_static_symbol('_start')
            if _start is not None:
                _start.entry.st_value = pre_main_addr
                self.elf.update_symbol(_start)

            # inject code
            code = text.data()
            self.inject_code(code)

            self.elf.increase_section('.bss', 8)

        subprocess.call(['make', '-f', 'Makefile.x86', 'clean'])


class ELFPatcher_x64(ELFPatcher):

    def __init__(self, elf):
        ELFPatcher.__init__(self, elf)


class ELFPatcher_ARM(ELFPatcher):

    def __init__(self, elf):
        ELFPatcher.__init__(self, elf)

    def modify_plt(self, run_interceptor_offset):
        plt = self.elf.get_plt_section()
        for i in xrange(plt.first_entry(), plt.num_entries()):
            plt.seek_for_entry(i)
            self.stream.write(int32_to_bytes(0xe59fc000))  # mov ip, pc
            b = 0xea000000  # branch without offset
            b |= (run_interceptor_offset - self.stream.tell() - 8) >> 2
            self.stream.write(int32_to_bytes(b))
            self.stream.write(int32_to_bytes(i - 1))

    def inject_code(self, code):
        self.stream.seek(self.elf.get_padding_offset())
        self.stream.write(code)

    def inject(self, interceptor_obj):
        plt = self.elf.get_plt_section()
        plt.seek_for_entry(1)

        C2 = bytes_to_int32(self.stream.read(4)) & 0xff
        C1 = bytes_to_int32(self.stream.read(4)) & 0xff
        C0 = bytes_to_int32(self.stream.read(4)) & 0xfff
        C = (C2 << 20) + (C1 << 12) + C0
        text = self.elf.get_text_segment()
        C += plt.entry_offset(1) + text['p_vaddr'] - text['p_offset'] + 8

        VA = self.elf.get_padding_addr()
        REL_PLT_ADDR = self.elf.get_rel_plt_section()['sh_addr']
        DYNSYM_ADDR = self.elf.get_section_by_name('.dynsym')['sh_addr']
        DYNSTR_ADDR = self.elf.get_section_by_name('.dynstr')['sh_addr']

        subprocess.call(['make',
                         '-f'
                         'Makefile.arm',
                         'C=' + str(C),
                         'VA=' + str(VA),
                         'REL_PLT=' + str(REL_PLT_ADDR),
                         'DYNSYM=' + str(DYNSYM_ADDR),
                         'DYNSTR=' + str(DYNSTR_ADDR),
                         'INTERCEPTOR_OBJ=' + interceptor_obj])

        with open('all.out', 'rb') as all_out_stream:
            run_interceptor_offset = self.elf.get_padding_offset()
            self.modify_plt(run_interceptor_offset)

            all_out = XELFFile(all_out_stream)
            text = all_out.get_section_by_name('.text')
            code = text.data()
            self.inject_code(code)

        subprocess.call(['make', '-f', 'Makefile.arm', 'clean'])


def inject(elf_filename, interceptor_obj):
    patcher = create_patcher(elf_filename)
    patcher.inject(interceptor_obj)


def usage(name):
    print 'Usage: %s elf-file interceptor-obj' % name


def main(args):
    if len(args) != 3:
        usage(args[0])
        sys.exit(1)

    inject(args[1], args[2])


if __name__ == '__main__':
    main(sys.argv)
