''' Plugin for CudaText editor
Authors:
    Andrey Kvichansky    (kvichans on github.com)
Version:
    '0.9.5 2015-12-17'
ToDo: (see end of file)
'''

import  os, json, random
import  cudatext        as app
from    cudatext    import ed
import  cudatext_cmd    as cmds
import  cudax_lib       as apx
from    cudax_lib   import log

pass;                           # Logging
pass;                           LOG = (-2==-2)  # Do or dont logging.

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
        self.dlg_prs    = ver_macros.get('dlg_prs', {})
        self.macros     = ver_macros['list']
        self.mcr4id     = {str(mcr['id']):mcr for mcr in self.macros}
        
        self.need_dlg   = False
        self.last_mcr_id= 0
       #def __init__
       
    def on_start(self, ed_self):
        self._do_acts(acts='|reg|menu|')
       #def on_start
        
    def _adapt_menu(self):
        ''' Add or change top-level menu Macros
        '''
        id_menu     = 0
        if 'macros_id_menu' in dir(ed):                 ##?? dirty hack!
            id_menu = ed.macros_id_menu                 ##?? dirty hack!
            # Clear old
            app.app_proc(app.PROC_MENU_CLEAR, id_menu)
        else:
#       if 0==self.id_menu:
            # Create
            top_nms = app.app_proc(app.PROC_MENU_ENUM, 'top').splitlines()
            pass;              #LOG and log('top_nms={}',top_nms)
            plg_ind = top_nms.index('&Plugins|')        ##?? 
            id_menu  = app.app_proc( app.PROC_MENU_ADD, '{};{};{};{}'.format('top', 0, '&Macros', plg_ind))
            ed.macros_id_menu = id_menu                 ##?? dirty hack!

        # Fill
        if 0==len(self.macros):
            if not ed.get_prop(app.PROP_MACRO_REC):
                app.app_proc(app.PROC_MENU_ADD, '{};{};{}'.format(id_menu, cmds.cmd_MacroStart, 'Start record'))
            else:
                app.app_proc(app.PROC_MENU_ADD, '{};{};{}'.format(id_menu, cmds.cmd_MacroStop,  'Stop record'))
                app.app_proc(app.PROC_MENU_ADD, '{};{};{}'.format(id_menu, cmds.cmd_MacroCancel,'Cancel record'))
            return
        app.app_proc(app.PROC_MENU_ADD, '{};cuda_macros,dlg_config;{}'.format(id_menu, 'Co&nfig...'))
        app.app_proc(app.PROC_MENU_ADD, '{};;-'.format(id_menu))
        for mcr in self.macros:
            app.app_proc(app.PROC_MENU_ADD, '{};cuda_macros,run,{};{}'.format(id_menu, mcr['id'], mcr['nm']))
       #def _adapt_menu
        
    def dlg_config_custom(self):
        ''' Show dlg for change macros list.
        '''
        keys_json   = app.app_path(app.APP_DIR_SETTINGS)+os.sep+'keys.json'
        keys        = apx._json_loads(open(keys_json).read()) if os.path.exists(keys_json) else {}
        c1      = chr(1)
        c2      = chr(2)
        pos_fmt = 'pos={l},{t},{r},{b}'.format
        GAP     = 5
        
        ids     = [mcr['id'] for mcr in self.macros]
        mcr_ind = ids.index(self.last_mcr_id) if self.last_mcr_id in ids else -1
        pass;                   LOG and log('self.last_mcr_id, mcr_ind={}',(self.last_mcr_id,mcr_ind))
        while True:
            pass;               LOG and log('mcr_ind={}',(mcr_ind))
            (WD_LST
            ,HT_LST)= (self.dlg_prs.get('w_list', 300)
                      ,self.dlg_prs.get('h_list', 500))
            (WD_ACTS
            ,HT_ACTS)=(self.dlg_prs.get('w_acts', 300)
                      ,self.dlg_prs.get('h_acts', 500))
            (WD_BTN
            ,HT_BTN)= (self.dlg_prs.get('w_btn', 150), 25)
            l_btn   = GAP+WD_LST+GAP
            
            vw_acts = (WD_ACTS!=0)
            rec_on  = ed.get_prop(app.PROP_MACRO_REC)

            nmkys   = []
            for mcr in self.macros:
                mcr_cid = 'cuda_macros,run,{}'.format(mcr['id'])
                mcr_keys= keys.get(mcr_cid, {})
                kys     = '/'.join([' * '.join(mcr_keys.get('s1', []))
                                   ,' * '.join(mcr_keys.get('s2', []))
                                   ]).strip('/')
                nmkys  += [mcr['nm'] + (' ['+kys+']' if kys else '')]

            mcr_acts= ''
            if vw_acts and mcr_ind in range(len(self.macros)):
                mcr     = self.macros[mcr_ind]
                mcr_acts= '\t'.join(['# '+nmkys[mcr_ind]] + mcr['evl'])
            ans = app.dlg_custom('Macros'   ,GAP+WD_LST+GAP+WD_BTN+GAP+WD_ACTS+GAP,GAP+HT_LST+GAP, '\n'.join([]
            +[c1.join(['type=listbox'   ,pos_fmt(l=GAP,    t=GAP,           r=GAP+WD_LST,   b=GAP+HT_LST)
                      ,'items='+'\t'.join(nmkys)
                      ,'val='+str(mcr_ind)  # start sel
                      ,'en='+str(0 if rec_on else 1)
                      ] # i=0
             )]
            +([c1.join(['type=button'    ,pos_fmt(l=l_btn,  t=GAP*1+HT_BTN*0,    r=l_btn+WD_BTN, b=0)
                      ,'cap=&View actions...'
                      ,'props='+str(1 if vw_acts and not rec_on else 0)     # default
                      ,'en='+str(0 if rec_on else 1)
                      ] # i=1
             )] if vw_acts else [])
            +[c1.join(['type=button'    ,pos_fmt(l=l_btn,  t=GAP*2+HT_BTN*1,    r=l_btn+WD_BTN, b=0)
                      ,'cap=Hot&keys...'
                      ,'en='+str(0 if rec_on else 1)
                      ] # i=2 if vw_acts else i=1
             )]
            +[c1.join(['type=button'    ,pos_fmt(l=l_btn,  t=GAP*3+HT_BTN*2,    r=l_btn+WD_BTN, b=0)
                      ,'cap=Re&name...'
                      ,'en='+str(0 if rec_on else 1)
                      ] # i=3 if vw_acts else i=2
             )]
            +[c1.join(['type=button'    ,pos_fmt(l=l_btn,  t=GAP*4+HT_BTN*3,    r=l_btn+WD_BTN, b=0)
                      ,'cap=&Delete...'
                      ,'en='+str(0 if rec_on else 1)
                      ] # i=4 if vw_acts else i=3
             )]
            +[c1.join(['type=button'    ,pos_fmt(l=l_btn,  t=GAP*7+HT_BTN*6,    r=l_btn+WD_BTN, b=0)
                      ,'cap=&Run'
                      ,'props='+str(1 if not vw_acts and not rec_on else 0)     # default
                      ,'en='+str(0 if rec_on else 1)
                      ] # i=5 if vw_acts else i=4
             )]
            +[c1.join(['type=label'     ,pos_fmt(l=l_btn,               t=GAP*8+HT_BTN*7+3, r=l_btn+int(WD_BTN/3),b=0)
                      ,'cap=&Times'
                      ] # i=6 if vw_acts else i=5
             )]
            +[c1.join(['type=spinedit'  ,pos_fmt(l=l_btn+int(WD_BTN/3)+GAP,   t=GAP*8+HT_BTN*7,   r=l_btn+WD_BTN, b=0)
                      ,'props=1,{},1'.format(self.dlg_prs.get('times',  1000))
                      ,'en='+str(0 if rec_on else 1)
                      ] # i=7 if vw_acts else i=6
             )]
            +[c1.join(['type=button'    ,pos_fmt(l=l_btn,  t=GAP*10+HT_BTN*9,    r=l_btn+WD_BTN, b=0)
                      ,'cap='+('&Start record' if not rec_on else '&Stop record')
                      ,'props='+str(1 if rec_on else 0)     # default
                      ] # i=8 if vw_acts else i=7
             )]
            +[c1.join(['type=button'    ,pos_fmt(l=l_btn,  t=GAP*11+HT_BTN*10,    r=l_btn+WD_BTN, b=0)
                      ,'cap=Canc&el record'
                      ,'en='+str(1 if rec_on else 0)
                      ] # i=9 if vw_acts else i=8
             )]
            +[c1.join(['type=button'    ,pos_fmt(l=l_btn,  t=    HT_LST-HT_BTN*2, r=l_btn+WD_BTN, b=0)
                      ,'cap=C&ustom...'
                      ,'en='+str(0 if rec_on else 1)
                      ] # i=10 if vw_acts else i=9
             )]
            +[c1.join(['type=button'    ,pos_fmt(l=l_btn,  t=GAP+HT_LST-HT_BTN*1, r=l_btn+WD_BTN, b=0)
                      ,'cap=&Close'
                      ] # i=11 if vw_acts else i=10
             )]
            +([c1.join(['type=memo'      ,pos_fmt(l=GAP+WD_LST+GAP+WD_BTN+GAP,   t=GAP,  r=GAP+WD_LST+GAP+WD_BTN+GAP+WD_ACTS, b=GAP+HT_ACTS)
                      ,'val='+mcr_acts
                      ,'props=0,0,1'    # ro,mono,border
                      ] # i=12
             )] if vw_acts else [])
            ), apx.icase(                not rec_on, 0
                        ,    vw_acts and     rec_on, 8
                        ,not vw_acts and not rec_on, 7))    # start focus
            pass;              #LOG and log('ans={}',ans)
            if ans is None:  break #while
            (ans_i
            ,vals)  = ans
            ans_s   = apx.icase(    vw_acts and ans_i==1, 'view'
                               ,    vw_acts and ans_i==2, 'hotkeys'
                               ,    vw_acts and ans_i==3, 'rename'
                               ,    vw_acts and ans_i==4, 'delete'
                               ,    vw_acts and ans_i==5, 'run'
                               ,    vw_acts and ans_i==8, 'rec'
                               ,    vw_acts and ans_i==9, 'cancel'
                               ,    vw_acts and ans_i==10,'custom'
                               ,    vw_acts and ans_i==11,'close'
                              #,not vw_acts and ans_i==1, 'view'
                               ,not vw_acts and ans_i==1, 'hotkeys'
                               ,not vw_acts and ans_i==2, 'rename'
                               ,not vw_acts and ans_i==3, 'delete'
                               ,not vw_acts and ans_i==4, 'run'
                               ,not vw_acts and ans_i==7, 'rec'
                               ,not vw_acts and ans_i==8, 'custom'
                               ,not vw_acts and ans_i==9, 'close'
                               ,'?')
            mcr_ind = int(vals.splitlines()[0])
            times   = int(vals.splitlines()[7 if vw_acts else 6])

            mcr     = self.macros[mcr_ind]
            self.last_mcr_id = mcr['id']
            
            if ans_s=='close':  break #while
            
            what    = ''
            changed = False
            if False:pass
            elif ans_s=='custom': #Custom
                custs   = app.dlg_input_ex(5, 'Custom dialog Macros'
                    , 'Height of macro list (min 300)'        , str(self.dlg_prs.get('h_list', 300))
                    , 'Width of macro list (min 200)'         , str(self.dlg_prs.get('w_list', 500))
                    , 'Width of action list (min 200, 0-hide)', str(self.dlg_prs.get('w_acts', 500))
                    , 'Width of buttons (min 100)'            , str(self.dlg_prs.get('w_btn',  150))
                    , 'Max run times (min 100)'               , str(self.dlg_prs.get('times',  1000))
                    )
                if custs is not None:
                    self.dlg_prs['h_list']  = max(300, int(custs[0]));  self.dlg_prs['h_acts'] = self.dlg_prs['h_list']
                    self.dlg_prs['w_list']  = max(200, int(custs[1]))
                    self.dlg_prs['w_acts']  = max(200, int(custs[2])) if int(custs[2])!=0 else 0
                    self.dlg_prs['w_btn']   = max(100, int(custs[3]))
                    self.dlg_prs['times']   = max(100, int(custs[4]))
                    open(MACROS_JSON, 'w').write(json.dumps({'ver':JSON_FORMAT_VER, 'list':self.macros, 'dlg_prs':self.dlg_prs}, indent=4))
                continue #while
                
            elif ans_s=='view': #View
                continue #while

            elif ans_s=='rename': #Rename
                mcr_nm      = app.dlg_input('New name for: {}'.format(nmkys[mcr_ind])
                                           ,mcr['nm'])
                if mcr_nm is None or mcr_nm==mcr['nm']:     continue #while
                while mcr_nm in [mcr['nm'] for mcr in self.macros]:
                    app.msg_box('Select other name.\nMacro names now are:\n\n'+'\n'.join(nmkys), app.MB_OK)
                    mcr_nm  = app.dlg_input('New name for: {}'.format(nmkys[mcr_ind])
                                           ,mcr_nm)
                    if mcr_nm is None or mcr_nm==mcr['nm']: break #while mcr_nm
                if mcr_nm is None or mcr_nm==mcr['nm']:     continue #while
                what        = 'rename'
                mcr['nm']   = mcr_nm
                changed = True
                
            elif ans_s=='delete': #Del
                if app.msg_box( 'Delete macro\n    {}'.format(nmkys[mcr_ind])
                              , app.MB_YESNO)!=app.ID_YES:  continue #while
                what    = 'delete:'+str(mcr['id'])
                del self.macros[mcr_ind]
                mcr_ind = min(mcr_ind, len(self.macros)-1)
                changed = True
                
            elif ans_s=='hotkeys': #Hotkeys
                app.dlg_hotkeys('cuda_macros,run,'+str(mcr['id']))
                keys    = apx._json_loads(open(keys_json).read()) if os.path.exists(keys_json) else {}
                changed = True

            elif ans_s=='run': #Run
                times = max(1, times)
                for rp in range(times):
                    self.run(mcr['id'])
                return

            elif ans_s=='rec'    and not rec_on: #Start record
                return ed.cmd(cmds.cmd_MacroStart)
            elif ans_s=='rec'    and     rec_on: #Stop record
                self.need_dlg = True
                return ed.cmd(cmds.cmd_MacroStop)
            elif ans_s=='cancel' and     rec_on: #Cancel record
                ed.cmd(cmds.cmd_MacroCancel)
                
            if changed:
                self._do_acts(what)
           #while True
       #def dlg_config_custom
        
    def dlg_config(self):
        ''' Show dlg for change macros list.
        '''
        return self.dlg_config_custom()
       #def dlg_config
       
    def on_macro(self, ed_self, mcr_record):
        ''' Finish for macro-recording.
            Params
                mcr_record   "\n"-separated list of
                                number
                                number,string
                                py:string_module,string_method,string_param
        '''
        pass;                  #LOG and log('mcr_record={}',mcr_record)
        if ''==mcr_record:   return app.msg_status('Empty record')
        def_nm      = ''
        nms     = [mcr['nm'] for mcr in self.macros]
        for num in range(1,1000):
            def_nm  = 'Macro{}'.format(num)
            if def_nm not in nms:
                break #for num
        mcr_nm      = app.dlg_input('Macro name (tricks: "!NM" for rewrite, "=NM" for dialog)', def_nm)
        if mcr_nm is None:   return
        mcr_nm      = mcr_nm.strip()
        if mcr_nm[0]=='=':
            self.need_dlg = True
            mcr_nm  = mcr_nm[1:]
        use_old     = False
        if mcr_nm[0]=='!':
            use_old = True
            mcr_nm  = mcr_nm[1:]
        if ''==mcr_nm.strip():   return app.msg_status('Empty macro name')
        pass;                   LOG and log('self.need_dlg, use_old, mcr_nm={}',(self.need_dlg, use_old, mcr_nm))
        
        if use_old and mcr_nm in nms:
            mcr_ind     = nms.index(mcr_nm)
            self.macros[mcr_ind]['rec'] = mcr_record
            self.macros[mcr_ind]['evl'] = self._record_data_to_cmds(mcr_record)
            id4mcr      = self.macros[mcr_ind]['id']
        else:
            while mcr_nm in nms:
                app.msg_box('Select other name.\nMacros names now:\n\n'+'\n'.join(nms), app.MB_OK)
                mcr_nm  = app.dlg_input('Name for new macro', mcr_nm)
                if mcr_nm is None:   return
        
            id4mcr      = random.randint(10000, 99999)
            while id4mcr in self.mcr4id:
                id4mcr  = random.randint(10000, 99999)
            self.macros += [{'id' :id4mcr       ##?? conflicts?
                            ,'nm' :mcr_nm
                            ,'rec':mcr_record
                            ,'evl':self._record_data_to_cmds(mcr_record)
                            }]
        self._do_acts()
        
        if self.need_dlg:
            self.need_dlg   = False
            self.last_mcr_id= id4mcr
            self.dlg_config_custom()
       #def on_macro

    def _do_acts(self, what='', acts='|save|second|reg|keys|menu|'):
        ''' Use macro list '''
        pass;                  #LOG and log('what, acts={}',(what, acts))
        # Save
        if '|save|' in acts:
            open(MACROS_JSON, 'w').write(json.dumps({'ver':JSON_FORMAT_VER, 'list':self.macros, 'dlg_prs':self.dlg_prs}, indent=4))
        
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
            pass;              #LOG and log('reg_subs={}',reg_subs)
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
                pass;          #LOG and log('UPD keys.json deleted key={}',mcr_key)
                open(keys_json, 'w').write(json.dumps(keys, indent=2))
        
        # [Re]Build menu
        if '|menu|' in acts:
            self._adapt_menu()
       #def _do_acts

    def run(self, mcr_id):
        ''' Main (and single) way to run any macro
        '''
#       mcr_id  = str(mcr_id)
        pass;                  #LOG and log('mcr_id={}',mcr_id)
        mcr     = self.mcr4id.get(str(mcr_id))
        if mcr is None:
            return app.msg_status('No macros: {}'.format(mcr_id))
        cmds4eval   = ';'.join(mcr['evl'])
        pass;                  #LOG and log('nm, cmds4eval={}',(mcr['nm'], cmds4eval))
        exec(cmds4eval)
        self.last_mcr_id = mcr_id
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


