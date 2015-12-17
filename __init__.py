''' Plugin for CudaText editor
Authors:
    Andrey Kvichansky    (kvichans on github.com)
Version:
    '0.9.2 2015-12-15'
'''

from .cd_macros import Command as CommandRLS

RLS  = CommandRLS()
class Command:
    def on_start(self, ed_self):                return RLS.on_start(ed_self)
    def dlg_config(self):                       return RLS.dlg_config()
    def on_macro(self, ed_self, mcr_record):    return RLS.on_macro(ed_self, mcr_record)
    def run(self, mcr_id):                      return RLS.run(mcr_id)
    #class Command
