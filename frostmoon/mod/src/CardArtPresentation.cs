using System.Runtime.CompilerServices;
using MegaCrit.Sts2.Core.Nodes.Cards;
namespace Frostmoon;

[HarmonyPatch(typeof(NCard),"Reload")]
static class CardArtPresentation
{
    sealed record OriginalLayout(TextureRect.StretchModeEnum Stretch,CanvasItem.TextureFilterEnum Filter);
    static readonly ConditionalWeakTable<TextureRect,OriginalLayout> originals=new();
    static void Postfix(NCard __instance)
    {
        if(!__instance.IsNodeReady() || __instance.Model==null)return;
        var portrait=__instance.GetNode<TextureRect>("%Portrait");
        if(__instance.Model is FrostmoonCard)
        {
            originals.GetValue(portrait,p=>new OriginalLayout(p.StretchMode,p.TextureFilter));
            // The game supplies the type-specific portrait mask; fill it with the square master artwork.
            portrait.StretchMode=TextureRect.StretchModeEnum.KeepAspectCovered;
            portrait.TextureFilter=CanvasItem.TextureFilterEnum.Linear;
        }
        else if(originals.TryGetValue(portrait,out var original))
        {
            // Card nodes are pooled and may later display a vanilla card.
            portrait.StretchMode=original.Stretch;portrait.TextureFilter=original.Filter;
        }
    }
}
