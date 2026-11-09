#include "BunkerRadiationModel.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FC13RadiationModelTest, "C13.Unit.Radiation.Model",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FC13RadiationModelTest::RunTest(const FString& Parameters)
{
    using namespace C13::Radiation;
    const C13::Radiation::Parameters Rules{.8, 1, 30, 2};
    const auto Exhausted=Advance({0,3},Rules,10,2,true);
    TestTrue(TEXT("Protection exhausts during the step"),Exhausted.Accepted && std::abs(Exhausted.Next.Burden-15.2)<1.e-8 && Exhausted.Next.ProtectionCondition==0);
    const auto Shelter=Advance({40,25},Rules,10,0,true);
    TestTrue(TEXT("Returning preserves exposure and symptoms"),Shelter.Next.Burden==40 && Shelter.Next.ProtectionCondition==25 && Shelter.Damage==20);
    TestTrue(TEXT("Treatment does not repair equipment"),Treat({40,25},15).Next.ProtectionCondition==25);
    TestFalse(TEXT("Invalid time cannot update state"),Advance({40,25},Rules,-1,2,true).Accepted);
    return true;
}
#endif
