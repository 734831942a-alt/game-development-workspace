using System.Runtime.CompilerServices;
using MegaCrit.Sts2.Core.Nodes.Screens.CharacterSelect;
namespace Frostmoon;

// Keep the native panel clear of the character on the left and the moon above.
// Restore the original layout when another character is selected.
[HarmonyPatch(typeof(NCharacterSelectScreen),nameof(NCharacterSelectScreen.SelectCharacter))]
static class SelectPresentation
{
    sealed class Layout { public Vector2 Position; }
    static readonly ConditionalWeakTable<NCharacterSelectScreen,Layout> Layouts=new();
    static void Prefix(NCharacterSelectScreen __instance, CharacterModel characterModel,
        Control ____infoPanel, Tween? ____infoPanelTween, ref Vector2 ____infoPanelPosFinalVal)
    {
        var layout=Layouts.GetValue(__instance,_=>new Layout { Position=____infoPanel.Position });
        ____infoPanelTween?.Kill();
        var position=characterModel is FrostmoonCharacter
            ? new Vector2(__instance.Size.X*.54f,__instance.Size.Y*.43f)
            : layout.Position;
        ____infoPanel.Position=position;
        ____infoPanelPosFinalVal=position;
    }
    static void Postfix(NCharacterSelectScreen __instance,CharacterModel characterModel)
    {
        if(characterModel is not FrostmoonCharacter)return;
        var background=__instance.GetNode<Control>("AnimatedBg");
        var cover=background.GetChildren().OfType<Control>().Single();
        // Vanilla oversizes/offsets AnimatedBg for its animated artwork. Fit this
        // complete illustration to the screen instead of cropping its left edge.
        cover.SetAnchorsAndOffsetsPreset(Control.LayoutPreset.TopLeft);
        void Fit()
        {
            var transform=background.GetGlobalTransform().AffineInverse()*__instance.GetGlobalTransform();
            cover.Position=transform.Origin;cover.Scale=transform.Scale;cover.Size=__instance.Size;
        }
        Fit();__instance.Resized+=Fit;cover.TreeExiting+=()=>__instance.Resized-=Fit;
    }
}
