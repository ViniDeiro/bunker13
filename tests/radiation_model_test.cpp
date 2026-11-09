#include "Survival/BunkerRadiationModel.h"
#include <cstdlib>
#include <iostream>
#include <limits>

using namespace C13::Radiation;
static int Checks = 0;
static void Check(bool Pass, const char* Name)
{
    ++Checks;
    if (!Pass) { std::cerr << "FAIL " << Name << '\n'; std::exit(1); }
}
static bool Near(double A, double B) { return std::abs(A-B) < 1.e-8; }
int main()
{
    const Parameters Rules{.8, 1, 30, 2};
    auto Bare = Advance({0,100}, Rules, 10, 2, false);
    Check(Bare.Accepted && Near(Bare.Next.Burden,20), "unprotected exposure");
    Check(Near(Bare.Next.ProtectionCondition,100), "unequipped item does not wear");
    auto Protected = Advance({0,100}, Rules, 10, 2, true);
    Check(Near(Protected.Next.Burden,4), "protection reduces exposure");
    Check(Near(Protected.Next.ProtectionCondition,90), "protection wears");
    auto Exhausted = Advance({0,3}, Rules, 10, 2, true);
    Check(Near(Exhausted.Next.Burden,15.2), "exhaustion halfway through frame");
    Check(Near(Exhausted.Next.ProtectionCondition,0), "condition bounded at zero");
    auto Broken = Advance({0,0}, Rules, 10, 2, true);
    Check(Near(Broken.Next.Burden,20), "broken equipment cannot protect");
    auto Safe = Advance({40,25}, Rules, 10, 0, true);
    Check(Near(Safe.Next.Burden,40) && Near(Safe.Next.ProtectionCondition,25), "return does not reset burden or wear equipment");
    Check(Near(Safe.Damage,20), "symptoms persist in shelter");
    auto Crossing = Advance({20,0}, Rules, 10, 2, false);
    Check(Near(Crossing.Damage,10), "threshold crossing integrated");
    auto Ceiling = Advance({95,0}, Rules, 10, 2, false);
    Check(Near(Ceiling.Next.Burden,100), "burden bounded at 100");
    auto Zero = Advance({12,25}, Rules, 0, 2, true);
    Check(Zero.Accepted && Near(Zero.Next.Burden,12) && Near(Zero.Damage,0), "zero elapsed time");
    auto Treatment = Treat({40,25}, 15);
    Check(Treatment.Accepted && Near(Treatment.Next.Burden,25) && Near(Treatment.Next.ProtectionCondition,25), "treatment preserves condition");
    Check(!Treat({0,25},15).Accepted, "no treatment at zero burden");
    Check(Treat({10,25},15).Next.Burden==0, "treatment bounded at zero");
    const double Nan=std::numeric_limits<double>::quiet_NaN();
    const double Inf=std::numeric_limits<double>::infinity();
    Check(!Advance({Nan,20},Rules,1,1,true).Accepted, "NaN state rejected");
    Check(!Advance({0,20},Rules,-1,1,true).Accepted, "negative time rejected");
    Check(!Advance({0,20},Rules,1,Inf,true).Accepted, "infinite rate rejected");
    Check(!Advance({0,20},{1.1,1,30,2},1,1,true).Accepted, "invalid protection rejected");
    Check(!Advance({0,101},Rules,1,1,true).Accepted, "invalid condition rejected");
    Check(!Treat({40,25},Nan).Accepted, "NaN treatment rejected");
    Check(!Treat({40,25},-1).Accepted, "negative treatment rejected");
    Check(!Advance({0,20},Rules,1.e308,1.e308,true).Accepted, "overflow rejected");
    auto Rejected=Advance({12,20},Rules,1,-1,true);
    Check(!Rejected.Accepted && Near(Rejected.Next.Burden,12) && Near(Rejected.Next.ProtectionCondition,20), "invalid update is atomic");
    auto Whole=Advance({20,3},Rules,60,2,true);
    State Split{20,3}; double Damage=0;
    for(int I=0;I<600;++I) {auto Step=Advance(Split,Rules,.1,2,true);Split=Step.Next;Damage+=Step.Damage;}
    Check(Near(Whole.Next.Burden,Split.Burden) && Near(Whole.Next.ProtectionCondition,Split.ProtectionCondition) && Near(Whole.Damage,Damage), "frame subdivision invariance through exhaustion threshold and cap");
    std::cout << "C13_RADIATION_MODEL checks=" << Checks << " passed=1\n";
}
