using UnrealBuildTool;

public class Condominio13EditorTarget : TargetRules
{
    public Condominio13EditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("Condominio13");
    }
}
