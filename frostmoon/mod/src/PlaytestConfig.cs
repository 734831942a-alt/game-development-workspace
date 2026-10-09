using BaseLib.Config;
namespace Frostmoon;
public class PlaytestConfig : SimpleModConfig
{
    [ConfigSlider(0,4,1)] public static int StartingDeck { get; set; }
}
[HarmonyPatch(typeof(Player), "PopulateStartingDeck")]
static class PresetUpgradePatch
{
    static void Postfix(Player __instance)
    {
        if(__instance.Character is not FrostmoonCharacter || PlaytestConfig.StartingDeck is <1 or >4)return;
        var entries=CardCatalog.Presets[PlaytestConfig.StartingDeck-1];
        for(int i=0;i<Math.Min(entries.Length,__instance.Deck.Cards.Count);i++)
            if(entries[i].Up){__instance.Deck.Cards[i].UpgradeInternal();__instance.Deck.Cards[i].FinalizeUpgradeInternal();}
    }
}
