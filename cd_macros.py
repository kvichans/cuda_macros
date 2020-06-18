''' Plugin for CudaText editor
Authors:
    Andrey Kvichansky    (kvichans on github.com)
    Alexey Torgashin (CudaText)
Version:
    '1.1.7 2020-06-18'
ToDo: (see end of file)
'''

import  os, json, random, datetime, re
import  cudatext            as app
from    cudatext        import ed
import  cudatext_cmd        as cmds
import  cudax_lib           as apx
from    cudax_lib       import log
from    .cd_plug_lib    import *

# I18N
_       = get_translation(__file__)

pass;                           # Logging
pass;                           LOG = (-2== 2)  # Do or dont logging.

FROM_API_VERSION = '1.0.114'
FROM_API_VERSION = '1.0.172' # menu_proc() <== PROC_MENU_*
FROM_API_VERSION = '1.0.185' # menu_proc() with hotkey, tag

VERSION     = re.split('Version:', __doc__)[1].split("'")[1]
VERSION_V,  \
VERSION_D   = VERSION.split(' ')

JSON_FORMAT_VER = '20151204'
MACROS_JSON     = app.app_path(app.APP_DIR_SETTINGS)+os.sep+'macros.json'

C1      = chr(1)
C2      = chr(2)
POS_FMT = 'pos={l},{t},{r},{b}'.format
GAP     = 5

#at4chk  = top_plus_for_os('check')
#at4lbl  = top_plus_for_os('label')
#at4btn  = top_plus_for_os('button')

class Command:
    CMD_ID2NM   = {}    # {val: name} from cudatext_cmd.py

    macros      = []    # Main list [macro]
    mcr4id      = {}    # Derived dict {str_id:macro}

#   id_menu     = 0

    def __init__(self):
        cmd_nms         = [nm                               for nm in dir(cmds)
                            if nm.startswith('cCommand_') or nm.startswith('cmd_')]
        cmd_nm2id       = {nm:eval('cmds.{}'.format(nm))    for nm in cmd_nms}
        self.CMD_ID2NM  = {str(cmd_id):nm                   for nm,cmd_id in cmd_nm2id.items()}
        if False and len(self.CMD_ID2NM) < len(cmd_nm2id):
            app.msg_status('Repeated values in cudatext_cmd.py')
            ddnms   = [nm for nm,id in cmd_nm2id.items() if nm not in self.CMD_ID2NM.values()]
            pass;               log('CMD names with eq values {}',(ddnms))
        pass;                  #LOG and log('cmd_nm2id={}',cmd_nm2id)
        pass;                  #LOG and log('CMD_ID2NM={}',self.CMD_ID2NM)

        ver_macros      = apx._json_loads(open(MACROS_JSON).read()) if os.path.exists(MACROS_JSON) else {'ver':JSON_FORMAT_VER, 'list':[]}
        if ver_macros['ver'] < JSON_FORMAT_VER:
            # Adapt to new format
            pass
        self.tm_ctrl    = ver_macros.get('tm_ctrl', {})
        self.dlg_prs    = ver_macros.get('dlg_prs', {})
        self.macros     = ver_macros['list']
        self.mcr4id     = {str(mcr['id']):mcr for mcr in self.macros}

        self.need_dlg   = False
        self.last_mcr_id= 0

        pass;                   LOG and log('\n\n\nMacros start',)
       #def __init__

    def on_start(self, ed_self):
        self._do_acts(acts='|reg|menu|')
       #def on_start

    def adapt_menu(self, id_menu=0):
        ''' Add or change top-level menu Macros
            Param id_menu points to exist menu item (ie by ConfigMenu) for filling
        '''
        if app.app_api_version()<FROM_API_VERSION:  return app.msg_status(_('Need update CudaText'))
        pass;                  #LOG and log('id_menu={}',id_menu)
        PLUG_AUTAG  = 'auto_config:cuda_macros,adapt_menu'    # tag for ConfigMenu to call this method
        if id_menu!=0:
            # Use this id
            app.menu_proc(              id_menu, app.MENU_CLEAR)
        else:
            top_its = app.menu_proc(    'top', app.MENU_ENUM)
            if PLUG_AUTAG in [it['tag'] for it in top_its]:
                # Reuse id from 'top'
                id_menu = [it['id'] for it in top_its if it['tag']==PLUG_AUTAG][0]
                app.menu_proc(          id_menu, app.MENU_CLEAR)
            else:
                # Create BEFORE Plugins
                plg_ind = [ind for ind,it in enumerate(top_its) if 'plugins' in it['hint']][0]
                id_menu = app.menu_proc('top', app.MENU_ADD, tag=PLUG_AUTAG, index=plg_ind,     caption=_('&Macros'))
        # Fill
        app.menu_proc(      id_menu, app.MENU_ADD, command=self.dlg_config,                     caption=_('&Macros...')
                     , hotkey=get_hotkeys_desc(    'cuda_macros,dlg_config'))
        app.menu_proc(      id_menu, app.MENU_ADD,                                              caption='-')
        app.menu_proc(      id_menu, app.MENU_ADD, command=cmds.cmd_MacroStart,                 caption=_('&Start record')
                     , hotkey=get_hotkeys_desc(            cmds.cmd_MacroStart))
        app.menu_proc(      id_menu, app.MENU_ADD, command=cmds.cmd_MacroStop,                  caption=_('St&op record')
                     , hotkey=get_hotkeys_desc(            cmds.cmd_MacroStop))
        app.menu_proc(      id_menu, app.MENU_ADD, command=cmds.cmd_MacroCancel,                caption=_('&Cancel record')
                     , hotkey=get_hotkeys_desc(            cmds.cmd_MacroCancel))
        app.menu_proc(      id_menu, app.MENU_ADD,                                              caption='-')
        app.menu_proc(      id_menu, app.MENU_ADD, command=self.dlg_export,                     caption=_('&Export...')
                     , hotkey=get_hotkeys_desc(    'cuda_macros,dlg_export'))
        app.menu_proc(      id_menu, app.MENU_ADD, command=self.dlg_import,                     caption=_('&Import...')
                     , hotkey=get_hotkeys_desc(    'cuda_macros,dlg_import'))
        if 0==len(self.macros): return
        app.menu_proc(      id_menu, app.MENU_ADD,                                              caption='-')
        def call_with(call,p):
            return lambda:call(p)
        for mcr in self.macros:
            app.menu_proc(  id_menu,app.MENU_ADD, command=call_with(self.run,    mcr['id']),    caption=mcr['nm']
                         , hotkey=get_hotkeys_desc(         'cuda_macros,run,{}',mcr['id']))
       #def adapt_menu

    def dlg_export(self):
        ''' Show dlg for export some macros.
        '''
        if app.app_api_version()<FROM_API_VERSION:  return app.msg_status(_('Need update CudaText'))
        if 0==len(self.macros):                     return app.msg_status(_('No macros for export'))
        exp_file= app.dlg_file(False, '', '', 'CudaText macros|*.cuda-macros')
        exp_file= '' if exp_file is None else exp_file
        exp_file= exp_file+('' if ''==exp_file or exp_file.endswith('.cuda-macros') else '.cuda-macros')
        (WD_LST
        ,HT_LST)= (500
                  ,500)

        lmcrs   = len(self.macros)
        crt,sels= '0', ['0'] * lmcrs
        while True:
            pass;               LOG and log('sels={}',sels)

            cnts    = ([
  dict(              tp='lb'    ,tid='file'         ,l=GAP             ,w=70            ,cap=_('Export &to')                    )
 ,dict(cid='file'   ,tp='ed'    ,t=GAP              ,l=GAP+70          ,r=GAP+WD_LST-35 ,en='0'                                 )
 ,dict(cid='brow'   ,tp='bt'    ,tid='file'         ,l=GAP+HT_LST-35   ,r=GAP+WD_LST    ,cap=_('&...')                          )
 ,dict(cid='mcrs'   ,tp='ch-lbx',t=35   ,h=HT_LST   ,l=GAP             ,w=    WD_LST    ,items=[mcr['nm'] for mcr in self.macros])
 ,dict(cid='ch-a'   ,tp='bt'    ,t=GAP+35+HT_LST    ,l=GAP*1           ,w=100           ,cap=_('Check &all')                    )
 ,dict(cid='ch-n'   ,tp='bt'    ,t=GAP+35+HT_LST    ,l=GAP*2+100       ,w=100           ,cap=_('U&ncheck all')                  )
 ,dict(cid='expo'   ,tp='bt'    ,t=GAP+35+HT_LST    ,l=    WD_LST-70*2 ,w=70            ,cap=_('&Export')       ,props='1'      )   # default
 ,dict(cid='-'      ,tp='bt'    ,t=GAP+35+HT_LST    ,l=GAP+WD_LST-70*1 ,w=70            ,cap=_('Close')                         )
                    ])
            vals    = dict( file=exp_file
                           ,mcrs=(crt, sels)
                        )
            btn,    \
            vals,   \
            chds    = dlg_wrapper(_('Export macros')   ,GAP+WD_LST+GAP, GAP*5+HT_LST+25*2-GAP, cnts, vals, focus_cid='mrcs')
            if btn is None or btn=='-': return
            crt,sels= vals['mcrs']
            pass;               LOG and log('sels={}',sels)
            if False:pass
            elif btn=='brow': #ans_s=='file':
                new_exp_file= app.dlg_file(False, '', '', 'CudaText macros|*.cuda-macros')
                if new_exp_file is not None:
                    exp_file    = new_exp_file
                    exp_file    = exp_file+('' if ''==exp_file or exp_file.endswith('.cuda-macros') else '.cuda-macros')
            elif btn=='ch-a': #ans_s=='all':
                sels    = ['1'] * lmcrs
            elif btn=='ch-n': #ans_s=='no':
                sels    = ['0'] * lmcrs
            elif btn=='expo': #ans_s=='exp':
                if '1' not in sels:
                    app.msg_box(_('Select some names'), app.MB_OK)
                    continue
                self.export_to_file(exp_file, [mcr for (ind, mcr) in enumerate(self.macros) if sels[ind]=='1'])
                return
           #while True:
       #def dlg_export

    def dlg_import_choose_mcrs(self):
        l,lt    = '\n', '\n  '
        while True:
            imp_file= app.dlg_file(True, '', '', 'CudaText macros|*.cuda-macros|All file|*.*')
            if imp_file is None:
                return (None, None)
            vers_mcrs   = apx._json_loads(open(imp_file).read())
            if vers_mcrs is None:
                if app.ID_OK != app.msg_box(_('No macros in file\n  {}\n\nChoose another file?').format(imp_file)
                    ,app.MB_OKCANCEL):
                    return (None, None)
                continue #while
            vers        = vers_mcrs.get('vers', {})
            if (app.app_api_version() < vers.get('ver-api', app.app_api_version())
            and app.ID_OK != app.msg_box(
                        _('Macros from')
                    +lt+imp_file
                    +l+ _('are recorded in CudaText with version')
                    +lt+    '"{}"'
                    +l+ _('Your CudaText has older version')
                    +lt+    '"{}"'
                    +l+ ''
                    +l+ _('No guarantee of correct working!')
                    +l+ ''
                    +l+ _('Continue import?').format(vers['ver-app'], app.app_exe_version())
                    ,   app.MB_OKCANCEL)):
                return (None, None)
            mcrs    = vers_mcrs.get('macros', [])
            if 0!=len(mcrs):
                break #while
            if app.ID_OK != app.msg_box(_('No macros in file\n  {}\n\nChoose another file?').format(imp_file)
                ,app.MB_OKCANCEL):
                return (None, None)
           #while True:
        return (imp_file, mcrs)
       #def dlg_import_choose_mcrs

    def dlg_import(self):
        ''' Show dlg for import some macros.
        '''
        if app.app_api_version()<FROM_API_VERSION:  return app.msg_status(_('Need update CudaText'))
        (imp_file
        ,mcrs)  = self.dlg_import_choose_mcrs()
        if imp_file is None:    return
        lmcrs   = len(mcrs)

        WD_LST, \
        HT_LST  = (500
                  ,500)
        crt,sels= '0', ['1'] * lmcrs
        while True:

            cnts    = ([
  dict(              tp='lb'    ,tid='file'         ,l=GAP             ,w=85            ,cap=_('Import &from')              )
 ,dict(cid='file'   ,tp='ed'    ,t=GAP              ,l=GAP+85          ,r=GAP+WD_LST-35 ,en='0'                             )
 ,dict(cid='brow'   ,tp='bt'    ,tid='file'         ,l=GAP+HT_LST-35   ,r=GAP+WD_LST    ,cap=_('&...')                      )
 ,dict(cid='mcrs'   ,tp='ch-lbx',t=35  ,h=HT_LST    ,l=GAP             ,w=    WD_LST    ,items=[mcr['nm'] for mcr in mcrs]  )
 ,dict(cid='ch-a'   ,tp='bt'    ,t=GAP+35+HT_LST    ,l=GAP*1           ,w=100           ,cap=_('Check &all')                )
 ,dict(cid='ch-n'   ,tp='bt'    ,t=GAP+35+HT_LST    ,l=GAP*2+100       ,w=100           ,cap=_('U&ncheck all')              )
 ,dict(cid='impo'   ,tp='bt'    ,t=GAP+35+HT_LST    ,l=    WD_LST-70*2 ,w=70            ,cap=_('&Import')       ,props='1'  )   # default
 ,dict(cid='-'      ,tp='bt'    ,t=GAP+35+HT_LST    ,l=GAP+WD_LST-70*1 ,w=70            ,cap=_('Close')                     )
                    ])
            vals    = dict( file=imp_file
                           ,mcrs=(crt, sels)
                        )
            btn,    \
            vals,   \
            chds    = dlg_wrapper(_('Import macros'), GAP+WD_LST+GAP, GAP*4+HT_LST+25*2, cnts, vals, focus_cid='mrcs')
            if btn is None or btn=='-': return
            crt,sels= vals['mcrs']
            pass;               LOG and log('sels={}',sels)
            if False:pass
            elif btn=='brow': #ans_s=='file':
                (new_imp_file
                ,new_mcrs)  = self.dlg_import_choose_mcrs()
                if new_imp_file is None:    continue #while
                imp_file    = new_imp_file
                mcrs        = new_mcrs
                lmcrs       = len(mcrs)
                crt,sels    = '0', ['1'] * lmcrs
            elif btn=='ch-a': #ans_s=='all':
                sels    = ['1'] * lmcrs
            elif btn=='ch-n': #ans_s=='no':
                sels    = ['0'] * lmcrs
            elif btn=='impo': #ans_s=='imp':
                if '1' not in sels:
                    app.msg_box(_('Select some names'), app.MB_OK)
                    continue
                (good_nms
                ,fail_nms) = self.import_from_list([mcr for (ind, mcr) in enumerate(mcrs) if sels[ind]=='1'])
                l,lt    = '\n', '\n      '
                app.msg_box(   _('Import macros:')     +lt+lt.join(good_nms)
                            +l+''
                            +l+_('Skip duplicates:')   +lt+lt.join(fail_nms)
                           ,app.MB_OK)
#               self.dlg_config()
#               return
       #def dlg_import

    def dlg_config(self):
        ''' Show dlg for change macros list.
        '''
        if app.app_api_version()<FROM_API_VERSION:  return app.msg_status(_('Need update CudaText'))
        keys_json   = app.app_path(app.APP_DIR_SETTINGS)+os.sep+'keys.json'
        keys        = apx._json_loads(open(keys_json).read()) if os.path.exists(keys_json) else {}

        ids     = [mcr['id'] for mcr in self.macros]
        mcr_ind = ids.index(self.last_mcr_id) if self.last_mcr_id in ids else -1
        pass;                   LOG and log('self.last_mcr_id, mcr_ind={}',(self.last_mcr_id,mcr_ind))
        times   = 1
        waits   = 5
        chngs   = '0'
        endln   = '0'
        while True:
            WD_LST, \
            HT_LST  = (self.dlg_prs.get('w_list', 300)
                      ,self.dlg_prs.get('h_list', 500))
            WD_ACTS,\
            HT_ACTS = (self.dlg_prs.get('w_acts', 300)
                      ,self.dlg_prs.get('h_acts', 500))
            WD_BTN, \
            HT_BTN  = (self.dlg_prs.get('w_btn', 150), 24)
            WD_BTN_3= int(WD_BTN/3)
            l_btn   = GAP+WD_LST+GAP
            l_acts  = GAP+WD_LST+GAP+WD_BTN+GAP

            vw_acts = (WD_ACTS>0)
            WD_ACTS = max(0, WD_ACTS)
            rec_on  = ed.get_prop(app.PROP_MACRO_REC)
            lmcrs   = len(self.macros)
            pass;               LOG and log('mcr_ind,vw_acts,rec_on={}',(mcr_ind,vw_acts,rec_on))

            nmkys   = []
            for mcr in self.macros:
                mcr_cid = 'cuda_macros,run,{}'.format(mcr['id'])
                mcr_keys= keys.get(mcr_cid, {})
                kys     = '/'.join([' * '.join(mcr_keys.get('s1', []))
                                   ,' * '.join(mcr_keys.get('s2', []))
                                   ]).strip('/')
                nmkys  += [mcr['nm'] + (' ['+kys+']' if kys else '')]

            mcr_acts= ['']
#           mcr_acts= ''
            if vw_acts and mcr_ind in range(lmcrs):
                mcr     = self.macros[mcr_ind]
                mcr_acts=           ['# '+nmkys[mcr_ind]] + mcr['evl']
#               mcr_acts= '\t'.join(['# '+nmkys[mcr_ind]] + mcr['evl'])

            act4mrcs    = '1' if vw_acts else '0'
            def_stst    = '1' if                     rec_on or 0==lmcrs else '0'
            n_edable    = '0' if                     rec_on or 0==lmcrs else '1'
            n_vwable    = '1' if not vw_acts and not rec_on else '0'
            only_rec_off= '0' if                     rec_on else '1'
            only_rec_on = '1' if                     rec_on else '0'
            tims_props  = '0,{},1'.format(self.dlg_prs.get('times',  1000))
            stst_cap    = _('&Stop record') if       rec_on else _('&Start record')
            cnts        = ([]
 +[dict(cid='mrcs'   ,tp='lbx'  ,t=GAP  ,h=HT_LST       ,l=GAP                  ,w=WD_LST   ,items=nmkys            ,act=act4mrcs  ,en=only_rec_off    )]
#+(
# [dict(cid='view'   ,tp='bt'   ,t=GAP* 1+HT_BTN* 0     ,l=l_btn                ,w=WD_BTN   ,cap=_('&View actions') ,props=n_edable,en=n_edable         )]  # default
# if vw_acts else [])
 +[dict(cid='keys'   ,tp='bt'   ,t=GAP* 1+HT_BTN* 0     ,l=l_btn                ,w=WD_BTN   ,cap=_('Hot&keys...')                   ,en=n_edable        )]
 +[dict(cid='renm'   ,tp='bt'   ,t=GAP* 2+HT_BTN* 1     ,l=l_btn                ,w=WD_BTN   ,cap=_('Re&name...')                    ,en=n_edable        )]
 +[dict(cid='del'    ,tp='bt'   ,t=GAP* 3+HT_BTN* 2     ,l=l_btn                ,w=WD_BTN   ,cap=_('&Delete...')                    ,en=n_edable        )]
 +[dict(cid='run'    ,tp='bt'   ,t=GAP* 5+HT_BTN* 4     ,l=l_btn                ,w=WD_BTN   ,cap=_('&Run!')         ,props=n_vwable ,en=n_edable        )]  # default
 +[dict(              tp='lb'   ,tid='times'            ,l=l_btn                ,w=WD_BTN_3 ,cap=_('&Times')                                            )]
 +[dict(cid='times'  ,tp='sp-ed',t=GAP* 6+HT_BTN* 5     ,l=l_btn+WD_BTN_3+GAP   ,r=l_btn+WD_BTN                     ,props=tims_props,en=only_rec_off   )]  # min,max,step
 +[dict(              tp='lb'   ,tid='waits'            ,l=l_btn                ,w=WD_BTN_3 ,cap=_('&Wait')                                             )]
 +[dict(cid='waits'  ,tp='sp-ed',t=GAP* 7+HT_BTN* 6     ,l=l_btn+WD_BTN_3+GAP   ,r=l_btn+WD_BTN-40                  ,props='1,3600,1',en=only_rec_off   )]  # min,max,step
 +[dict(              tp='lb'   ,tid='waits'            ,l=l_btn+WD_BTN-40+GAP  ,w=WD_BTN   ,cap=_('sec')                                               )]
 +[dict(cid='chngs'  ,tp='ch'   ,t=GAP* 8+HT_BTN* 7     ,l=l_btn                ,w=WD_BTN   ,cap=_('While text c&hanges')                               )]
 +[dict(cid='endln'  ,tp='ch'   ,t=GAP* 9+HT_BTN* 8     ,l=l_btn                ,w=WD_BTN   ,cap=_('Until c&aret on last line')                         )]
 +[dict(cid='stst'   ,tp='bt'   ,t=GAP*11+HT_BTN*10     ,l=l_btn                ,w=WD_BTN   ,cap=stst_cap           ,props=def_stst                     )]
 +[dict(cid='canc'   ,tp='bt'   ,t=GAP*12+HT_BTN*11     ,l=l_btn                ,w=WD_BTN   ,cap=_('Canc&el record')                ,en=only_rec_on     )]
 +[dict(cid='view'   ,tp='ch'   ,t=GAP*14+HT_BTN*13     ,l=l_btn                ,w=WD_BTN   ,cap=_('Show actions')                                      )]
 +[dict(cid='adju'   ,tp='bt'   ,t=    HT_LST-HT_BTN*2  ,l=l_btn                ,w=WD_BTN   ,cap=_('Ad&just...')                    ,en=only_rec_off    )]
 +[dict(cid='-'      ,tp='bt'   ,t=GAP+HT_LST-HT_BTN*1  ,l=l_btn                ,w=WD_BTN   ,cap=_('Close')                                             )]
 +(
  [dict(cid='acts'   ,tp='me'   ,t=GAP  ,h=HT_ACTS      ,l=l_acts               ,w=WD_ACTS                          ,props='1,1,1'                      )]  # ro,mono,border
  if vw_acts else [])
                    )
            vals    = dict( mrcs=mcr_ind
                           ,times=times
                           ,waits=waits
                           ,chngs=chngs
                           ,endln=endln
                           ,view=vw_acts
                        )
            if vw_acts: vals.update(
                      dict( acts=mcr_acts
                        ))
            btn,    \
            vals,   \
            chds    = dlg_wrapper(f('{} ({})', _('Macros'), VERSION_V), GAP+WD_LST+GAP+WD_BTN+GAP+WD_ACTS+GAP,GAP+HT_LST+GAP, cnts, vals, focus_cid='mrcs')
            if btn is None or btn=='-': return
            mcr_ind = vals['mrcs']
            times   = vals['times']
            waits   = vals['waits']
            chngs   = vals['chngs']
            endln   = vals['endln']
            vw_acts = vals['view']
            pass;               LOG and log('mcr_ind,times,waits,chngs,endln={}',(mcr_ind,times,waits,chngs,endln))

            if 0!=lmcrs and mcr_ind in range(lmcrs):
                mcr     = self.macros[mcr_ind]
                self.last_mcr_id = mcr['id']

#           if ans_s=='close':  break #while
            if btn=='adju': #ans_s=='custom': #Custom
                custs   = app.dlg_input_ex(5, _('Custom dialog Macros')
                    , _('Height of macro list (min 450)')          , str(self.dlg_prs.get('h_list', 400))
                    , _('Width of macro list (min 200)')           , str(self.dlg_prs.get('w_list', 500))
                    , _('Width of action list (min 200, <=0-hide)'), str(self.dlg_prs.get('w_acts', 500))
                    , _('Width of buttons (min 150)')              , str(self.dlg_prs.get('w_btn',  150))
                    , _('Max run times (min 100)')                 , str(self.dlg_prs.get('times',  1000))
                    )
                if custs is not None:
                    self.dlg_prs['h_list']  = max(450, int(custs[0]));  self.dlg_prs['h_acts'] = self.dlg_prs['h_list']
                    self.dlg_prs['w_list']  = max(200, int(custs[1]))
                    self.dlg_prs['w_acts']  = max(200, int(custs[2])) if int(custs[2])>0 else int(custs[2])
                    self.dlg_prs['w_btn']   = max(150, int(custs[3]))
                    self.dlg_prs['times']   = max(100, int(custs[4]))
                    open(MACROS_JSON, 'w').write(json.dumps({'ver':JSON_FORMAT_VER, 'list':self.macros, 'dlg_prs':self.dlg_prs}, indent=4))
                continue #while

            if btn!='stst' and mcr_ind not in range(lmcrs):
                app.msg_box(_('Select macro'), app.MB_OK)
                continue #while

            what    = ''
            changed = False
            if False:pass

            elif btn=='view': #ans_s=='view': #View
                continue #while

            elif btn=='renm': #ans_s=='rename': #Rename
                mcr_nm      = app.dlg_input(_('New name for: {}').format(nmkys[mcr_ind])
                                           ,mcr['nm'])
                if mcr_nm is None or mcr_nm==mcr['nm']:     continue #while
                while mcr_nm in [mcr['nm'] for mcr in self.macros]:
                    app.msg_box(_('Select other name.\nMacro names now are:\n\n')+'\n'.join(nmkys), app.MB_OK)
                    mcr_nm  = app.dlg_input(_('New name for: {}').format(nmkys[mcr_ind])
                                           ,mcr_nm)
                    if mcr_nm is None or mcr_nm==mcr['nm']: break #while mcr_nm
                if mcr_nm is None or mcr_nm==mcr['nm']:     continue #while
                what        = 'rename'
                mcr['nm']   = mcr_nm
                changed = True

            elif btn=='del': #ans_s=='delete': #Del
                if app.msg_box( _('Delete macro\n    {}').format(nmkys[mcr_ind])
                              , app.MB_YESNO+app.MB_ICONQUESTION)!=app.ID_YES:  continue #while
                what    = 'delete:'+str(mcr['id'])
                del self.macros[mcr_ind]
                mcr_ind = min(mcr_ind, len(self.macros)-1)
                changed = True

            elif btn=='keys': #ans_s=='hotkeys': #Hotkeys
                app.dlg_hotkeys('cuda_macros,run,'+str(mcr['id']))
                keys    = apx._json_loads(open(keys_json).read()) if os.path.exists(keys_json) else {}
                changed = True

            elif btn=='run': #ans_s=='run': #Run
                if (times==0
                and waits==0
                and chngs=='0'
                and endln=='0'):
                    app.msg_box(_('Select stop condition'), app.MB_OK)
                    continue
                self.run(mcr['id'], max(0, times), max(0, waits), chngs=='1', endln=='1')
                return

            elif btn=='stst'     and not rec_on: #Start record
#           elif ans_s=='rec'    and not rec_on: #Start record
                return ed.cmd(cmds.cmd_MacroStart)
            elif btn=='stst'     and     rec_on: #Stop record
#           elif ans_s=='rec'    and     rec_on: #Stop record
                self.need_dlg = True
                return ed.cmd(cmds.cmd_MacroStop)       # Return for clear rec-mode in StatusBar, will recall from on_macro
            elif btn=='canc'     and     rec_on: #Cancel record
#           elif ans_s=='cancel' and     rec_on: #Cancel record
                return ed.cmd(cmds.cmd_MacroCancel)     # Return for clear rec-mode in StatusBar

            if changed:
                self._do_acts(what)
           #while True
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
        if ''==mcr_record:   return app.msg_status(_('Empty record'))
        def_nm      = ''
        nms     = [mcr['nm'] for mcr in self.macros]
        for num in range(1,1000):
            def_nm  = 'Macro{}'.format(num)
            if def_nm not in nms:
                break #for num
        while True:
            mcr_nm      = app.dlg_input(_('Macro name. Tricks: "!NM" overwrite NM, "=NM" show NM in dialog'), def_nm)
            if mcr_nm is None:   return
            mcr_nm      = mcr_nm.strip()
            if ''==mcr_nm:  continue #while
            if mcr_nm[0]=='=':
                self.need_dlg = True
                mcr_nm  = mcr_nm[1:]
            use_old     = False
            if ''==mcr_nm:  continue #while
            if mcr_nm[0]=='!':
                use_old = True
                mcr_nm  = mcr_nm[1:]
            if ''!=mcr_nm:  break #while
        pass;                   LOG and log('self.need_dlg, use_old, mcr_nm={}',(self.need_dlg, use_old, mcr_nm))

        if use_old and mcr_nm in nms:
            mcr_ind     = nms.index(mcr_nm)
            self.macros[mcr_ind]['rec'] = mcr_record
            self.macros[mcr_ind]['evl'] = self._record_data_to_cmds(mcr_record)
            id4mcr      = self.macros[mcr_ind]['id']
        else:
            while mcr_nm in nms:
                app.msg_box(_('Select other name.\nMacros names now:\n\n')+'\n'.join(nms), app.MB_OK)
                mcr_nm  = app.dlg_input('Macro name', mcr_nm)
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
            self.dlg_config()
       #def on_macro

    def export_to_file(self, exp_file, mcrs):
        pass;                   LOG and log('exp_file, mcrs={}',(exp_file, mcrs))
        open(exp_file, 'w').write(json.dumps(
            {   'vers':{
                    'ver-mcr':JSON_FORMAT_VER
                ,   'ver-app':app.app_exe_version()
                ,   'ver-api':app.app_api_version()
                }
            ,   'macros':[{
                    'nm':   mcr['nm']
                 ,  'evl':  mcr['evl']
                    } for mcr in mcrs]
            }
        ,   indent=4))
       #def export_to_file

    def import_from_list(self, mcrs):
        pass;                   LOG and log('mcrs={}',(mcrs))
        good_nms    = []
        fail_nms    = []
        ids         = [mcr['id'] for mcr in self.macros]
        my_mcrs     = [{'nm' :mcr['nm'],'evl':mcr['evl']} for mcr in self.macros]
        for mcr in mcrs:
            if mcr in my_mcrs:
                fail_nms += [mcr['nm']]
                continue #for
            good_nms   += [mcr['nm']]
            id4mcr      = random.randint(10000, 99999)
            while id4mcr in ids:
                id4mcr  = random.randint(10000, 99999)
            ids += [id4mcr]
            self.macros+= [{'id' :id4mcr
                           ,'nm' :mcr['nm']
                           ,'evl':mcr['evl']
                           }]
        if good_nms:
            self._do_acts()
        return (good_nms, fail_nms)
       #def import_from_list

    def _do_acts(self, what='', acts='|save|second|reg|keys|menu|'):
        ''' Use macro list '''
        pass;                  #LOG and log('what, acts={}',(what, acts))
        # Save
        if '|save|' in acts:
            open(MACROS_JSON, 'w').write(json.dumps({
                 'ver':JSON_FORMAT_VER
                ,'list':self.macros
                ,'dlg_prs':self.dlg_prs
                ,'tm_ctrl':{'rp_ctrl':self.tm_ctrl.get('rp_ctrl', 1000)
                           ,'tm_wait':self.tm_ctrl.get('tm_wait', 10)}
                }, indent=4))

        # Secondary data
        if '|second|' in acts:
            self.mcr4id     = {str(mcr['id']):mcr for mcr in self.macros}

        # Register new subcommands
        if '|reg|' in acts:
            reg_subs        = 'cuda_macros;run;{}'.format('\n'.join(
                             'Macros: {}\t{}'.format(mcr['nm'],mcr['id'])
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
            self.adapt_menu()
       #def _do_acts

#   def run(self, mcr_id,    times=1, waits=0, while_chngs=False, till_endln=False):
    def run(self, info=None, times=1, waits=0, while_chngs=False, till_endln=False):
        ''' Main (and single) way to run any macro
        '''
        mcr_id  = info                  # For call as "module=cuda_exttools;cmd=run;info=id"
        pass;                   LOG and log('mcr_id, times, waits, while_chngs, till_endln={}',(mcr_id, times, waits, while_chngs, till_endln))
        mcr     = self.mcr4id.get(str(mcr_id))
        if mcr is None:
            pass;               LOG and log('no id',)
            return app.msg_status(_('No macros: {}').format(mcr_id))

        _mcr = mcr['evl']
        _mcr_s = ';'.join(_mcr)

        def _run_fast():
            exec(_mcr_s)

        def _run_chk():
            for s in _mcr:
                exec(s)
                if ed.get_carets()[0][1] >= ed.get_line_count()-1:
                    return True

        pass;                   LOG and log('nm, cmds4eval={}',(mcr['nm'], cmds4eval))
        how_t       = 'wait'
        rp_ctrl     = self.tm_ctrl.get('rp_ctrl', 1000)                     # testing one of 1000 execution
        tm_wait     = waits if waits>0 else self.tm_ctrl.get('tm_wait', 10) # sec
        start_t     = datetime.datetime.now()
        pre_body    = '' if not while_chngs else ed.get_text_all()
        _run        = _run_chk if till_endln else _run_fast

        cap_text =_('Macro "{}" playback time is too long'.format(mcr['nm']))
        cap_wait = _('Wait &another {} sec').format(tm_wait) # default
        cap_cont =_('Continue &without control')
        cap_stop =_('&Cancel playback [ESC]')

        for rp in range(times if times>0 else 0xffffffff):
            if _run():
                break   #for rp
            if while_chngs:
                new_body    = ed.get_text_all()
                if pre_body == new_body:
                    pass;       LOG and log('break no change',)
                    break   #for rp
                pre_body    = new_body
            if  (how_t=='wait'
            and (rp_ctrl-1) == rp % rp_ctrl
            and tm_wait < (datetime.datetime.now()-start_t).seconds):
                btn = app.msg_box_ex(
                    _('Macro playback'),
                    cap_text,
                    [cap_wait, cap_cont, cap_stop],
                    app.MB_ICONWARNING
                    )
                if btn is None or btn==2:
                    pass;       LOG and log('break by user',)
                    app.msg_status(_('Cancel playback macro: {}'.format(mcr['nm'])))
                    break   #for rp
                elif btn==1: #ans=='cont':
                    how_t   = 'work'
                elif btn==0: #ans=='wait':
                    start_t = datetime.datetime.now()
           #for rp
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
        # Native converting
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
            elif rc.startswith('py:cuda_macros,'):
                # Skip macro-tools
                continue #for rc
            elif rc[0:3]=='py:':
                # Plugin cmd
                evls += ["app.app_proc(app.PROC_EXEC_PLUGIN, '{}')".format(rc[3:])]
                continue #for rc
            pass;               LOG and log('unknown rec-item: {}',rc)

#       return evls

        # Optimization
        # (1) ed.cmd(cmds.cCommand_TextInsert,'A')
        #     ed.cmd(cmds.cCommand_TextInsert,'B')
        # convert to
        #     ed.cmd(cmds.cCommand_TextInsert,'AB')
        has_TI          = 1<len([evl for evl in evls
                      if                        'cmds.cCommand_TextInsert,' in evl])
        if has_TI:
            reTI2       = re.compile(  r"ed.cmd\(cmds.cCommand_TextInsert,'(.+)'\)"
                                    +   C1
                                    +  r"ed.cmd\(cmds.cCommand_TextInsert,'(.+)'\)")
            evls_c1     = C1.join(evls)
            (evls_c1
            ,rpls)      = reTI2.subn(  r"ed.cmd(cmds.cCommand_TextInsert,'\1\2')", evls_c1)
            while 0 < rpls:
                (evls_c1
                ,rpls)  = reTI2.subn(  r"ed.cmd(cmds.cCommand_TextInsert,'\1\2')", evls_c1)
            evls        = evls_c1.split(C1)
           #if has_TI
        pass;                   LOG and log('evls={}',evls)
        return evls
       #def _record_data_to_cmds

   #class Command

#if __name__ == '__main__' :     # Tests
def _testing():
    tm_wait = 100
    mcr     = {}
    mcr['nm']='Smth'
    cnts    = ([
  dict(              tp='lb'    ,t=GAP          ,l=GAP  ,w=400   ,cap=_('Macro "{}" playback time is too long'.format(mcr['nm'])))
 ,dict(cid='wait'   ,tp='bt'    ,t=GAP*2+25*1   ,l=GAP  ,w=400   ,cap=_('Wait &another {} sec').format(tm_wait)  ,props='1'      )   # default
 ,dict(cid='cont'   ,tp='bt'    ,t=GAP*3+25*2   ,l=GAP  ,w=400   ,cap=_('Continue &without control')                             )
 ,dict(cid='stop'   ,tp='bt'    ,t=GAP*6+25*3   ,l=GAP  ,w=400   ,cap=_('&Cancel playback [ESC]')                                )
                        ])
    btn,vals,chds= dlg_wrapper(_('Playback macro'), GAP*2+400, GAP*7+4*25, cnts)
#_testing()

'''
ToDo
[+][kv-kv][04dec15] Set stable part for run, use free part for name
[ ][at-kv][04dec15] Store in folder settings\macros for easy copy
[+][at-kv][04dec15] Run multuple times
[ ][kv-kv][04dec15] Optimize: replace ed.cmd() to direct API-function
[ ][kv-kv][08dec15] Skip commands in rec: start_rec, ??
[ ][kv-kv][08dec15] Test rec: call plug, call macro, call menu
[+][at-kv][18dec15] Check api-ver
[?][kv-kv][11jan16] Use PROC_SET_ESCAPE and progress
'''