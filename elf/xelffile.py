from elftools.elf.elffile import ELFFile
from elftools.elf.sections import Section

from xsections import GOTSection, PLTSection_x86_x64, PLTSection_ARM,\
    XSection
import resource


class XELFFile(ELFFile):

    PF_R = 0x4
    PF_W = 0x2
    PF_X = 0x1

    PAGE_SIZE = resource.getpagesize()

    def __init__(self, stream):
        ELFFile.__init__(self, stream)
        self._dynamic_functions_name_to_num = None
        self.num_extra_pages = 0

    def get_static_symbol(self, symbol):
        symtab = self.get_section_by_name('.symtab')
        if symtab is None:
            return None

        syms = symtab.get_symbol_by_name(symbol)
        if syms is None:
            return None

        return syms[0]

    def get_static_symbol_num(self, symbol):
        symtab = self.get_section_by_name('.symtab')
        if symtab is None:
            return None

        if symtab._symbol_name_map is None:
            # fill the map
            symtab.get_symbol_by_name(symbol)

        nums = symtab._symbol_name_map.get(symbol)
        if nums is None:
            return None

        return nums[0]

    def update_symbol(self, symbol):
        symtab = self.get_section_by_name('.symtab')
        symbol_num = self.get_static_symbol_num(symbol.name)
        self.stream.seek(symtab['sh_offset'] +
                         symbol_num * symtab['sh_entsize'])
        self.structs.Elf_Sym.build_stream(symbol.entry, self.stream)

    def num_dynamic_functions(self):
        rel_plt = self.get_rel_plt_section()
        if rel_plt is None:
            return 0

        return rel_plt.num_relocations()

    def get_dynamic_function_symbol(self, n):
        rel_plt = self.get_rel_plt_section()
        dynsym = self.get_section_by_name('.dynsym')
        if rel_plt is None or dynsym is None:
            return None

        rel = rel_plt.get_relocation(n)
        return dynsym.get_symbol(rel['r_info_sym'])

    def get_dynamic_function_name(self, n):
        sym = self.get_dynamic_function_symbol(n)
        if sym is None:
            return None

        return sym.name

    def dynamic_functions(self):
        for i in xrange(self.num_dynamic_functions()):
            yield self.get_dynamic_function_name(i)

    def get_dynamic_function_num(self, f):
        if self._dynamic_functions_name_to_num is None:
            self._dynamic_functions_name_to_num = {}
            for i, f in enumerate(self.dynamic_functions()):
                self._dynamic_functions_name_to_num[f] = i

        return self._dynamic_functions_name_to_num.get(f)

    def get_text_segment_num(self):
        RX = self.PF_R | self.PF_X
        for i, seg in enumerate(self.iter_segments()):
            if seg['p_type'] == 'PT_LOAD' and seg['p_flags'] == RX:
                return i

        return None

    def get_text_segment(self):
        return self.get_segment(self.get_text_segment_num())

    def get_data_segment_num(self):
        RW = self.PF_R | self.PF_W
        for i, seg in enumerate(self.iter_segments()):
            if seg['p_type'] == 'PT_LOAD' and seg['p_flags'] == RW:
                return i

        return None

    def get_data_segment(self):
        return self.get_segment(self.get_data_segment_num())

    def get_segment_header_offset(self, n):
        return self._segment_offset(n)

    def update_segment(self, n, segment):
        self.stream.seek(self.get_segment_header_offset(n))
        self.structs.Elf_Phdr.build_stream(segment.header, self.stream)

    def increase_segment(self, n, delta, nobits=True):
        seg = self.get_segment(n)
        if not nobits:
            seg.header.p_filesz += delta
        seg.header.p_memsz += delta
        self.update_segment(n, seg)

    def get_section_by_name(self, name):
        sect = ELFFile.get_section_by_name(self, name)
        if type(sect) is Section:
            return XSection(sect)

        return sect

    def get_section_num(self, section):
        if self._section_name_map is None:
            # fill the map
            self.get_section_by_name(section)

        return self._section_name_map.get(section)

    def get_section_header_offset(self, n):
        return self._section_offset(n)

    def get_section_header_offset_by_name(self, section):
        n = self.get_section_num(section)
        if n is None:
            return None

        return self.get_section_header_offset(n)

    def get_section_segment(self, section):
        sect = self.get_section_by_name(section)
        for seg in self.iter_segments():
            if seg.section_in_segment(sect):
                return seg

        return None

    def update_section(self, section):
        self.stream.seek(self.get_section_header_offset_by_name(section.name))
        self.structs.Elf_Shdr.build_stream(section.header, self.stream)

    def increase_section(self, section, delta):
        sect = self.get_section_by_name(section)
        sect.header.sh_size += delta
        self.update_section(sect)

    def get_rel_plt_section(self):
        rel_plt = self.get_section_by_name('.rel.plt')
        if rel_plt is None:
            rel_plt = self.get_section_by_name('.rela.plt')

        return rel_plt

    def get_got_section(self):
        got = self.get_section_by_name('.got.plt')
        if got is None:
            got = self.get_section_by_name('.got')

        return GOTSection(got)

    def get_plt_section(self):
        arch = self.get_machine_arch()
        if arch == 'x86' or arch == 'x64':
            return PLTSection_x86_x64(self.get_section_by_name('.plt'))
        elif arch == 'ARM':
            return PLTSection_ARM(self.get_section_by_name('.plt'))

    def get_padding_offset(self):
        text = self.get_text_segment()
        return text['p_offset'] + text['p_filesz'] \
            - self.num_extra_pages * self.PAGE_SIZE

    def get_padding_addr(self):
        text = self.get_text_segment()
        return text['p_vaddr'] + text['p_memsz'] \
            - self.num_extra_pages * self.PAGE_SIZE

    def get_text_padding_size(self):
        data = self.get_data_segment()
        total = data['p_offset'] - self.get_padding_offset()
        maximum = self.PAGE_SIZE - self.get_padding_offset() % self.PAGE_SIZE

        return min(total, maximum)

    def get_max_extension_size(self):
        text = self.get_text_segment()
        data = self.get_data_segment()
        data_addr = (data['p_vaddr'] + self.PAGE_SIZE - 1) % self.PAGE_SIZE
        return data_addr - text['p_vaddr'] - text['p_memsz']

    def extend_padding(self, numpages, all_space):
        extrasize = numpages * self.PAGE_SIZE
        if all_space:
            extrasize += self.PAGE_SIZE

        text = self.get_text_segment()
        textnum = self.get_text_segment_num()

        # update segments
        for i in xrange(textnum + 1, self.num_segments()):
            seg = self.get_segment(i)
            seg.header.p_offset += extrasize
            self.update_segment(i, seg)

        first = True
        for i in xrange(0, self.num_sections()):
            sect = self.get_section(i)
            if text.section_in_segment(sect):
                first = False
            else:
                if not first:
                    break

        # update sections
        for i in xrange(i, self.num_sections()):
            sect = self.get_section(i)
            sect.header['sh_offset'] += extrasize
            self.update_section(sect)

        # update sections table offset
        self.header.e_shoff += extrasize
        self.update_header()

        # physically extend the file
        self.stream.seek(self.get_padding_offset())
        remaining = self.stream.read()
        self.stream.seek(self.get_padding_offset())
        for i in xrange(0, extrasize):
            self.stream.write('0')
        self.stream.write(remaining)

        # extend the text segment to take into account the new padding
        text.header.p_filesz += numpages * self.PAGE_SIZE
        text.header.p_memsz += numpages * self.PAGE_SIZE
        self.update_segment(textnum, text)

        self.num_extra_pages = numpages

        # reinitialize to acquire the new file
        ELFFile.__init__(self, self.stream)

    def update_header(self):
        self.stream.seek(0)
        self.structs.Elf_Ehdr.build_stream(self.header, self.stream)

    def is_pie(self):
        # TODO
        pass
