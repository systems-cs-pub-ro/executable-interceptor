from elftools.elf.sections import Section


class XSection(Section):

    def __init__(self, section):
        Section.__init__(self, section.header, section.name, section.stream)

    def end_offset(self):
        return self['sh_offset'] + self['sh_size']

    def end_addr(self):
        return self['sh_addr'] + self['sh_size']


class GOTSection(XSection):

    def __init__(self, got):
        XSection.__init__(self, got)

    def num_entries(self):
        return self['sh_size'] / self['sh_entsize']

    def first_entry(self):
        return 3

    def entry_offset(self, i):
        return self['sh_offset'] + i * self['sh_entsize']

    def seek_for_entry(self, i):
        self.stream.seek(self.entry_offset(i))


class PLTSection(XSection):

    def __init__(self, plt):
        XSection.__init__(self, plt)

    def num_entries(self):
        pass

    def first_entry(self):
        return 1

    def entry_offset(self, i):
        pass

    def seek_for_entry(self, i):
        self.stream.seek(self.entry_offset(i))


class PLTSection_x86_x64(PLTSection):

    def __init__(self, plt):
        PLTSection.__init__(self, plt)
        self.ENTRY_SIZE = 0x10

    def num_entries(self):
        return self['sh_size'] / self.ENTRY_SIZE

    def entry_offset(self, i):
        return self['sh_offset'] + i * self.ENTRY_SIZE


class PLTSection_ARM(PLTSection):

    def __init__(self, plt):
        PLTSection.__init__(self, plt)
        self.ENTRY_SIZE = 0xc
        self.FIRST_ENTRY_SIZE = 0x14

    def num_entries(self):
        return self['sh_size'] / self.ENTRY_SIZE

    def entry_offset(self, i):
        return self['sh_offset'] + (i - 1) * self.ENTRY_SIZE \
            + self.FIRST_ENTRY_SIZE
