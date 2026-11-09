#pragma once

#include <algorithm>
#include <cmath>

// Engine-independent gameplay policy. The server adapter must supply elapsed time,
// zone rate and the condition of the SAME inventory GUID; this model owns no items.
namespace C13::Radiation
{
struct State
{
    double Burden = 0;
    double ProtectionCondition = 0;
};

struct Parameters
{
    double ProtectionFraction;
    double ProtectionWearPerSecond;
    double SymptomThreshold;
    double DamagePerSecond;
};

struct Result
{
    State Next;
    double Damage = 0;
    bool Accepted = false;
};

inline bool Bounded(double Value, double Min, double Max)
{
    return std::isfinite(Value) && Value >= Min && Value <= Max;
}

inline bool Valid(State Value)
{
    return Bounded(Value.Burden, 0, 100) && Bounded(Value.ProtectionCondition, 0, 100);
}

inline bool Valid(Parameters Value)
{
    return Bounded(Value.ProtectionFraction, 0, 1) &&
        std::isfinite(Value.ProtectionWearPerSecond) && Value.ProtectionWearPerSecond >= 0 &&
        Bounded(Value.SymptomThreshold, 0, 100) &&
        std::isfinite(Value.DamagePerSecond) && Value.DamagePerSecond >= 0;
}

inline Result Advance(State Current, Parameters Rules, double Seconds,
                      double ZoneBurdenPerSecond, bool Equipped)
{
    Result Out{Current};
    if (!Valid(Current) || !Valid(Rules) || !std::isfinite(Seconds) || Seconds < 0 ||
        !std::isfinite(ZoneBurdenPerSecond) || ZoneBurdenPerSecond < 0)
        return Out;
    // Reject arithmetic overflow before mutating state, including symptom damage.
    if (!std::isfinite(Seconds * ZoneBurdenPerSecond) ||
        !std::isfinite(Seconds * Rules.DamagePerSecond))
        return Out;

    double ProtectedSeconds = 0;
    if (Equipped && Current.ProtectionCondition > 0 && ZoneBurdenPerSecond > 0)
        ProtectedSeconds = Rules.ProtectionWearPerSecond > 0 ?
            std::min(Seconds, Current.ProtectionCondition / Rules.ProtectionWearPerSecond) : Seconds;

    auto Integrate = [&](double Duration, double Rate)
    {
        // Integrate across the symptom threshold exactly; a long frame must not
        // protect a player for longer than the remaining equipment condition.
        double SymptomaticSeconds = 0;
        if (Out.Next.Burden >= Rules.SymptomThreshold)
            SymptomaticSeconds = Duration;
        else if (Rate > 0)
            SymptomaticSeconds = std::max(0.0, Duration - (Rules.SymptomThreshold - Out.Next.Burden) / Rate);
        Out.Damage += SymptomaticSeconds * Rules.DamagePerSecond;
        Out.Next.Burden = std::min(100.0, Out.Next.Burden + Rate * Duration);
    };
    Integrate(ProtectedSeconds, ZoneBurdenPerSecond * (1 - Rules.ProtectionFraction));
    Integrate(Seconds - ProtectedSeconds, ZoneBurdenPerSecond);
    Out.Next.ProtectionCondition = std::max(0.0, Current.ProtectionCondition -
        ProtectedSeconds * Rules.ProtectionWearPerSecond);
    Out.Accepted = true;
    return Out;
}

// A game treatment lowers persistent burden, never restores protection or health.
// The authoritative adapter must first validate and consume a unique resource.
inline Result Treat(State Current, double Reduction)
{
    Result Out{Current};
    if (!Valid(Current) || !std::isfinite(Reduction) || Reduction <= 0 || Current.Burden <= 0)
        return Out;
    Out.Next.Burden = std::max(0.0, Current.Burden - Reduction);
    Out.Accepted = true;
    return Out;
}
}
