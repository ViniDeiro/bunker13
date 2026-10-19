"""Author gameplay numbers as an editable Data Asset and type the existing resources."""
import unreal as u
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
DEST='/Game/Bunker/Data';u.EditorAssetLibrary.make_directory(DEST)
rules=u.load_asset(DEST+'/DA_SurvivalRules')
created=not rules
if created:
    factory=u.DataAssetFactory();factory.set_editor_property('data_asset_class',u.BunkerSurvivalRules)
    rules=u.AssetToolsHelpers.get_asset_tools().create_asset('DA_SurvivalRules',DEST,u.BunkerSurvivalRules,factory)
assert rules
values={'max_weight_kg':20.0,'max_slots':12,'food_loss_per_minute':.6,'water_loss_per_minute':1.0,'energy_loss_per_minute':.4,'rest_gain_per_minute':15.0,'starvation_damage_per_minute':4.0,'action_interval':.2,'tired_action_interval':.6,'tired_threshold':15.0,'inventory_action_interval':.3}
if created:
    for key,value in values.items():rules.set_editor_property(key,value)
else:
    values={key:rules.get_editor_property(key) for key in values}
definitions=[]
for name,weight,food,water,health in [('Generic',.25,0,0,0),('Water',.6,0,35,0),('Food',.4,35,0,0),('Medkit',.8,0,0,40),('Battery',.2,0,0,0),('Tool',1.5,0,0,0)]:
    row=u.BunkerItemDefinition()
    for key,value in {'item_type':name,'weight_kg':weight,'food_gain':food,'water_gain':water,'health_gain':health}.items():row.set_editor_property(key,value)
    definitions.append(row)
if created:rules.set_editor_property('items',definitions)
u.EditorAssetLibrary.save_loaded_asset(rules)
level=u.get_editor_subsystem(u.LevelEditorSubsystem);level.load_level('/Game/Bunker/Lvl_Bunker')
labels={'INT_Water_01':'Water','INT_Water_02':'Water','INT_Can_01':'Food','INT_Medkit':'Medkit','INT_Battery':'Battery','INT_Tool':'Tool'}
updated=[]
for a in u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors():
    if a.get_actor_label() in labels:
        a.set_editor_property('item_type',labels[a.get_actor_label()]);updated.append(a.get_actor_label())
assert len(updated)==6,updated
level.save_current_level()
(ROOT/'logs/survival_rules.json').write_text(json.dumps({'data_asset':DEST+'/DA_SurvivalRules','parameters':values,'item_types':6,'typed_world_items':updated,'balance':'Prototype; not tuned for 60-120 minute sessions'},indent=2))
u.log('C13_SURVIVAL_RULES_OK')
