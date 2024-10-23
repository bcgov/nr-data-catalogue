SELECT DISTINCT DECODE(DiagVer.Name,'WASTE(FOR)','WASTE',DiagVer.Name) application
     , EntVer.Table_Name
  FROM app_erstudio.diagram      diag
     , app_erstudio.diagram_ver  diagver
     , app_erstudio.entity       ent
     , app_erstudio.entity_ver   entver
     , app_erstudio.model        mdl
     , app_erstudio.model_ver    mdlver
     , app_erstudio.submodel_ver smdlver
     , app_erstudio.submodel     smdl
     , app_erstudio.entity_display     entd
     , app_erstudio.entity_display_ver entdver
WHERE ent.latest_version_id   = entver.entity_ver_id
   AND mdl.model_id            = ent.model_id
   AND smdl.latest_version_id  = smdlver.submodel_ver_id
   AND mdl.model_id            = smdl.model_id
   AND diagver.diagram_id      = mdl.diagram_id
   AND mdl.latest_version_id   = mdlver.model_ver_id
   AND diag.latest_version_id  = diagver.diagram_ver_id
   AND ent.entity_id           = entd.entity_id
   AND entdver.entity_display_ver_id = entd.latest_version_id
   AND diag.is_deleted         = 0
   AND DiagVer.Name = :application                                                 -- A Given application
   AND mdlver.name LIKE '%Physical'                                                -- Filter only physical model by using naming pattern  
   AND entdver.backgroundcolor <> 16764057                                         -- Excludes external data assets                    
   AND EntVer.Table_Name NOT IN ('SDE_LOGFILES','SDE_LOGFILE_DATA','CG_REF_CODES') -- Some models include these SDE objects and other
   AND SUBSTR(EntVer.Table_Name,1,5) NOT IN ('MDXT_','MDRT_','RUPD$','MLOG$')      -- Exclude MViews and MView Logs existing in some models
   ORDER BY 1, 2