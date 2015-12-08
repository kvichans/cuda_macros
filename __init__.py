''' Plugin for CudaText editor
Authors:
    Andrey Kvichansky    (kvichans on githab.com)
Version:
    '0.9.1 2015-12-08'
ToDo: (see end of file)
'''

import  os, json, random
import  cudatext        as app
from    cudatext    import ed
import  cudatext_cmd    as cmds
import  cudax_lib       as apx
from    cudax_lib   import log

pass;                           # Logging
pass;                           LOG = (-2== 2)  # Do or dont logging.

JSON_FORMAT_VER = '20151204'
MACROS_JSON     = app.app_path(app.APP_DIR_SETTINGS)+os.sep+'macros.json'

class Command:
    CMD_ID2NM   = {}    # {val: name} from cudatext_cmd.py

    macros      = []    # Main list [macro]
    mcr4id      = {}    # Derived dict {id:macro}
    
    id_menu     = 0
    
    def __init__(self):
        cmd_nms         = [nm                               for nm in dir(cmds) 
                            if nm.startswith('cCommand_') or nm.startswith('cmd_')]
        cmd_nm2id       = {nm:eval('cmds.{}'.format(nm))    for nm in cmd_nms}
        self.CMD_ID2NM  = {str(cmd_id):nm                   for nm,cmd_id in cmd_nm2id.items()}
        if len(self.CMD_ID2NM) < len(cmd_nm2id):
            app.msg_status('Repeated values in cudatext_cmd.py')
        pass;                  #LOG and log('cmd_nm2id={}',cmd_nm2id)
        pass;                  #LOG and log('CMD_ID2NM={}',self.CMD_ID2NM)
        
        ver_macros      = apx._json_loads(open(MACROS_JSON).read()) if os.path.exists(MACROS_JSON) else {'ver':JSON_FORMAT_VER, 'list':[]}
        if ver_macros['ver'] < JSON_FORMAT_VER:
            # Adapt to new format
            pass
        self.macros     = ver_macros['list']
        self.mcr4id     = {str(mcr['id']):mcr for mcr in self.macros}
       #def __init__
       
    def on_start(self, ed_self):
        self._do_acts(acts='|reg|menu|')
       #def on_start
        
    def _adapt_menu(self):
        ''' Add or change top-level menu Macros
        '''
        if 0==self.id_menu:
            # Create
            top_nms = app.app_proc(app.PROC_MENU_ENUM, 'top').splitlines()
            pass;              #LOG and log('top_nms={}',top_nms)
            plg_ind = top_nms.index('&Plugins|')        ##?? 
            self.id_menu  = app.app_proc( app.PROC_MENU_ADD, '{};{};{};{}'.format('top', 0, '&Macros', plg_ind))
        else:
            # Clear old
            app.app_proc(app.PROC_MENU_CLEAR, self.id_menu)

        # Fill
        if 0==len(self.macros):
            if not ed.get_prop(app.PROP_MACRO_REC):
                app.app_proc(app.PROC_MENU_ADD, '{};{};{}'.format(self.id_menu, cmds.cmd_MacroStart, 'Start record'))
            else:
                app.app_proc(app.PROC_MENU_ADD, '{};{};{}'.format(self.id_menu, cmds.cmd_MacroStop,  'Stop record'))
                app.app_proc(app.PROC_MENU_ADD, '{};{};{}'.format(self.id_menu, cmds.cmd_MacroCancel,'Cancel record'))
            return
        app.app_proc(app.PROC_MENU_ADD, '{};cuda_macros,dlg_config;{}'.format(self.id_menu, 'Co&nfig...'))
        app.app_proc(app.PROC_MENU_ADD, '{};;-'.format(self.id_menu))
        for mcr in self.macros:
            app.app_proc(app.PROC_MENU_ADD, '{};cuda_macros,run,{};{}'.format(self.id_menu, mcr['id'], mcr['nm']))
       #def _adapt_menu
        
    def dlg_config(self):
        ''' Show dlg for change macros list.
        '''
#       macros  = self.macros
        acts= []
        if False:pass
        elif ed.get_prop(app.PROP_MACRO_REC):
            acts= ['Stop record'
                  ,'Cancel record']
        elif 0==len(self.macros) and not ed.get_prop(app.PROP_MACRO_REC):
            acts= ['Start record']
        else:
            acts= ['View macro actions...'
                  ,'Rename macro...'
                  ,'Run macro...'
                  ,'Delete macro...'
                  ,'-----'
                  ,'Start record'
                  ]
        while True:
            act_ind = app.dlg_menu(app.MENU_LIST, '\n'.join(acts))
            if act_ind is None or acts[act_ind][0]=='-': return
            act     = acts[act_ind]
            act     = act[:(act+' ').index(' ')]    # first word

            if act in 'Start Stop Cancel':
                if False:pass
                elif act=='Start'                       and not ed.get_prop(app.PROP_MACRO_REC): 
                    return ed.cmd(cmds.cmd_MacroStart)
                elif act=='Stop'                        and     ed.get_prop(app.PROP_MACRO_REC):
                    return ed.cmd(cmds.cmd_MacroStop)
                elif act=='Cancel'                      and     ed.get_prop(app.PROP_MACRO_REC):
                    return ed.cmd(cmds.cmd_MacroCancel)
                return
            
        
            keys_json   = app.app_path(app.APP_DIR_SETTINGS)+os.sep+'keys.json'
            keys        = apx._json_loads(open(keys_json).read()) if os.path.exists(keys_json) else {}
            nms         = [mcr['nm'] for mcr in self.macros]
            kys         = []
            for mcr in self.macros:
                mcr_key = 'cuda_macros,run,{}'.format(mcr['id'])
                mcr_keys= keys.get(mcr_key, {})
                kys    += ['/'.join([' * '.join(mcr_keys.get('s1', []))
                                    ,' * '.join(mcr_keys.get('s2', []))
                                    ]).strip('/')
                          ]
            mcr     = ''
            if 1==len(nms):
                mcr_ind = 0
            else:
                mcr_ind = app.dlg_menu(app.MENU_LIST
                        , '\n'.join('{}: {}\t{}'.format(a,n,k) for (a,n,k) in list(zip([act]*len(nms), nms, kys)))
                        )
                if mcr_ind is None: continue # while
            mcr     = self.macros[mcr_ind]
            mcr_keys= '('+kys[mcr_ind]+')' if ''!=kys[mcr_ind] else ''

            what    = ''        
            if False:pass
            elif act=='Rename': 
                #Rename
                mcr_nm      = app.dlg_input('New name for: {} {}'.format(
                                                mcr['nm']
                                              , mcr_keys)
                                           ,mcr['nm'])
                if mcr_nm is None or mcr_nm==mcr['nm']:     continue # while
                while mcr_nm in nms:
                    app.msg_box('Select other name.\nMacro names now are:\n\n'+'\n'.join(nms), app.MB_OK)
                    mcr_nm  = app.dlg_input('New name for: {} {}'.format(
                                                mcr['nm']
                                              , mcr_keys)
                                           ,mcr_nm)
                    if mcr_nm is None or mcr_nm==mcr['nm']: break # while mcr_nm
                if mcr_nm is None or mcr_nm==mcr['nm']:     continue # while
                what        = 'rename'
                mcr['nm']   = mcr_nm
            elif act=='Delete': 
                #Delete
                if app.msg_box( 'Delete macro\n    {} {}'.format(
                                nms[mcr_ind]
                              , mcr_keys)
                              , app.MB_YESNO)!=app.ID_YES:  continue # while
                what    = 'delete:'+str(mcr['id'])
                del self.macros[mcr_ind]
            elif act=='View': 
                #View
                app.msg_box(    'Actions for macro\n    {} {}\n\n{}'.format(
                                nms[mcr_ind].expandtabs(8)
                              , mcr_keys
                              , '\n'.join(mcr['evl']))
                              , app.MB_OK)
                return
            elif act=='Run': 
                return self.run(mcr['id'])

            self._do_acts(what)
            break #while
           #while
       #def dlg_config
       
    def on_macro(self, ed_self, mcr_record):
        ''' Finish for macro-recording.
            Params
                mcr_record   "\n"-separated list of
                                number
                                number,string
                                py:string_module,string_method,string_param
        '''
        pass;                   LOG and log('mcr_record={}',mcr_record)
        if ''==mcr_record:   return
        def_nm      = ''
        nms     = [mcr['nm'] for mcr in self.macros]
        for num in range(1,1000):
            def_nm  = 'Macro{}'.format(num)
            if def_nm not in nms:
                break #for num
        mcr_nm      = app.dlg_input('Name for new macro', def_nm)
        if mcr_nm is None:   return
        while mcr_nm in nms:
            app.msg_box('Select other name.\nMacros names now:\n\n'+'\n'.join(nms), app.MB_OK)
            mcr_nm  = app.dlg_input('Name for new macro', mcr_nm)
            if mcr_nm is None:   return
        
        # Parse
        mcr_cmds    = self._record_data_to_cmds(mcr_record)
        
        self.macros += [{'id' :random.randint(10000, 99999)     ##?? conflicts?
                        ,'nm' :mcr_nm
                        ,'rec':mcr_record
                        ,'evl':mcr_cmds
                        }]
        self._do_acts('add')
       #def on_macro

    def _do_acts(self, what='', acts='|save|second|reg|keys|menu|'):
        ''' Use macro list '''
        pass;                   LOG and log('what, acts={}',(what, acts))
        # Save
        if '|save|' in acts:
            open(MACROS_JSON, 'w').write(json.dumps({'ver':JSON_FORMAT_VER, 'list':self.macros}, indent=4))
        
        # Secondary data
        if '|second|' in acts:
#           self.mcr4nm     = {mcr['nm']:mcr for mcr in self.macros}
            self.mcr4id     = {str(mcr['id']):mcr for mcr in self.macros}
        
        # Register new subcommands
        if '|reg|' in acts:
            reg_subs        = 'cuda_macros;run;{}'.format('\n'.join(
                             'macro: {}\t{}'.format(mcr['nm'],mcr['id']) 
                                 for mcr in self.macros)
                             )
            pass;               LOG and log('reg_subs={}',reg_subs)
            app.app_proc(app.PROC_SET_SUBCOMMANDS, reg_subs)
        
        # Clear keys.json
        if '|keys|' in acts and ':' in what:
            # Need delete a key 'cuda_macros,run,NNNNN'
            mcr_id      = what[1+what.index(':'):]
            mcr_key     = 'cuda_macros,run,{}'.format(mcr_id)
            keys_json   = app.app_path(app.APP_DIR_SETTINGS)+os.sep+'keys.json'
            if not os.path.exists(keys_json): return
            keys        = apx._json_loads(open(keys_json).read())
            pass;              #LOG and log('??? key={}',mcr_key)
            if keys.pop(mcr_key, None) is not None:
                pass;          #LOG and log('del key={}',mcr_key)
                open(keys_json, 'w').write(json.dumps(keys, indent=2))
        
        # [Re]Build menu
        if '|menu|' in acts:
            self._adapt_menu()
       #def _do_acts

    def run(self, mcr_id):
        ''' Main (and single) way to run any macro
        '''
        mcr_id  = str(mcr_id)
        pass;                  #LOG and log('mcr_id={}',mcr_id)
        mcr     = self.mcr4id.get(str(mcr_id))
        if mcr is None:
            return app.msg_status('No macros: {}'.format(mcr_id))
        cmds4eval   = ';'.join(mcr['evl'])
        pass;                   LOG and log('nm, cmds4eval={}',(mcr['nm'], cmds4eval))
        exec(cmds4eval)
       #def run
       
    def _record_data_to_cmds(self, rec_data):
        ''' Coverting from record data to list of API command
            Param
                rec_data    "\n"-separated list of
                                number
                                number,string
                                py:string_module,string_method,string_param
        '''
        evls    = []
        rcs     = rec_data.splitlines()
        for rc in rcs:
            if False:pass
            elif rc[0] in '0123456789':
                if rc in self.CMD_ID2NM:
                    # For ed.cmd(id)
                    evls += ['ed.cmd(cmds.{})'.format(self.CMD_ID2NM[rc])]
                    continue #for rc
                if ',' in rc:
                    (id_cmd
                    ,tx_cmd)= rc[0:rc.index(',')], rc[1+rc.index(','):]
                    if ''==id_cmd.strip('0123456789') and id_cmd in self.CMD_ID2NM:
                        # For ed.cmd(id, text)
                        evls += ["ed.cmd(cmds.{},{})".format(self.CMD_ID2NM[id_cmd], repr(tx_cmd))]
                        continue #for rc
            elif rc.startswith('py:cuda_macros,dlg_config'):
                # Skip macro-tools
                continue #for rc
            elif rc[0:3]=='py:':
                # Plugin cmd
                evls += ["app.app_proc(app.PROC_EXEC_PLUGIN, '{}')".format(rc[3:])]
                continue #for rc
            pass;               LOG and log('unknown rec-item: {}',rc)
        return evls
       #def _record_data_to_cmds

   #class Command

'''
ToDo
[+][kv-kv][04dec15] Set stable part for run, use free part for name
[ ][at-kv][04dec15] Store in folder settings\macros for easy copy
[ ][at-kv][04dec15] Run multuple times
[ ][kv-kv][04dec15] Optimize: replace ed.cmd() to direct API-function
[ ][kv-kv][08dec15] Skip commands in rec: start_rec, ??
[ ][kv-kv][08dec15] Test rec: call plug, call macro, call menu
'''


