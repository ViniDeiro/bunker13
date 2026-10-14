using UnrealBuildTool;

public class Condominio13Target : TargetRules
{
    public Condominio13Target(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        IncludeOrderVersion = EngineIncludeOrderVersion.Latest;
        ExtraModuleNames.Add("Condominio13");
    }
}
