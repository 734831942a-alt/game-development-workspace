using MegaCrit.Sts2.Core.Modding;
using System.Reflection;
namespace Frostmoon;

[ModInitializer(nameof(Initialize))]
public static class Entry
{
    public static void Initialize()
    {
        BaseLib.Config.ModConfigRegistry.Register("Frostmoon",new PlaytestConfig());
        if(MegaCrit.Sts2.Core.Helpers.CommandLineHelper.HasArg("frostmoon-test"))
        {
            if(!OS.GetUserDataDir().Contains("FrostmoonIsolatedPlaytest"))throw new InvalidOperationException("Playtest requires isolated user directory.");
            var saves = new MegaCrit.Sts2.Core.Saves.SaveManager(new MegaCrit.Sts2.Core.Saves.GodotFileIo("user://frostmoon-test"));
            MegaCrit.Sts2.Core.Saves.SaveManager.MockInstanceForTesting(saves);
            saves.InitSettingsDataForTest();
            saves.SettingsSave.ModSettings = new MegaCrit.Sts2.Core.Modding.ModSettings { PlayerAgreedToModLoading = true };
            saves.SettingsSave.SkipIntroLogo = true;
            saves.SettingsSave.SeenEaDisclaimer = true;
            saves.SettingsSave.Fullscreen = false;
            saves.SettingsSave.WindowSize = new Vector2I(1280,720);
            GD.Print("[Frostmoon] Isolated local-only playtest storage enabled.");
        }
        new Harmony("ayanami.frostmoon").PatchAll(Assembly.GetExecutingAssembly());
        GD.Print("[Frostmoon] v0.2.2 loaded; 64 cards + 2 tokens; game target 0.107.1");
    }
}

// Attach the intrinsic state independently of the removable starter relic.
[HarmonyPatch(typeof(CombatManager), nameof(CombatManager.SetUpCombat))]
static class CombatSetupPatch
{
    static void Postfix(CombatState state)
    {
        foreach (var p in state.Players.Where(p => p.Character is FrostmoonCharacter))
        {
            if (p.Creature.GetPower<FrostmoonState>() != null) continue;
            var s = (FrostmoonState)ModelDb.Power<FrostmoonState>().ToMutable();
            s.Applier = p.Creature;
            s.Frost = p.Relics.Any(r => r is TwinPhasePendant) ? 2 : 0;
            s.ApplyInternal(p.Creature, 1, true);
        }
    }
}

// Reuse the actual action context for choices made by BeforeCardPlayed.
[HarmonyPatch(typeof(CardModel), nameof(CardModel.OnPlayWrapper))]
static class CardContextPatch
{
    internal static readonly Dictionary<Player, Stack<PlayerChoiceContext>> Contexts = new();
    internal static PlayerChoiceContext? Current(Player p) => Contexts.TryGetValue(p, out var s) && s.Count > 0 ? s.Peek() : null;
    static void Prefix(CardModel __instance, PlayerChoiceContext choiceContext)
    {
        var p = __instance.Owner;
        if (!Contexts.TryGetValue(p, out var stack)) Contexts[p] = stack = new();
        stack.Push(choiceContext);
    }
    static void Postfix(CardModel __instance, ref Task __result) => __result = Finish(__result, __instance.Owner);
    static async Task Finish(Task task, Player p)
    {
        try
        {
            await task;
            if(Contexts.TryGetValue(p,out var stack) && stack.Count==1 && CombatManager.Instance.IsInProgress && !CombatManager.Instance.IsEnding)
            {
                var state=p.Creature.GetPower<FrostmoonState>();
                if(state!=null)await state.CheckBlood(stack.Peek());
            }
        }
        finally { if (Contexts.TryGetValue(p, out var s) && s.Count > 0) s.Pop(); }
    }
}

// This point is after setup, draw, late start hooks, orb effects and automatic pre-play.
[HarmonyPatch(typeof(CombatManager),"RunAutoPrePlayPhase")]
static class TurnReadyPatch
{
    static void Postfix(Player player,HookPlayerChoiceContext playerChoiceContext,ref Task __result)
        => __result=AfterReady(__result,player,playerChoiceContext);
    static async Task AfterReady(Task task,Player p,PlayerChoiceContext ctx)
    {
        await task;
        if(CombatManager.Instance.IsInProgress && !CombatManager.Instance.IsEnding && p.Creature.GetPower<FrostmoonState>() is { } s)
            await s.CheckBlood(ctx);
    }
}

// Vanilla's healing hook reports requested healing; use the real HP delta instead.
[HarmonyPatch(typeof(Creature), nameof(Creature.HealInternal))]
static class HealLedgerPatch
{
    static void Prefix(Creature __instance, out int __state) => __state = __instance.CurrentHp;
    static void Postfix(Creature __instance, int __state)
    {
        var s = __instance.GetPower<FrostmoonState>();
        if (s != null) { s.Debt = Math.Max(0, s.Debt - Math.Max(0, __instance.CurrentHp - __state)); s.Rearm(); }
    }
}
