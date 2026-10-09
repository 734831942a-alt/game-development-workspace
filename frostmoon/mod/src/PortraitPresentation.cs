using MegaCrit.Sts2.Core.Nodes.Screens.CharacterSelect;
namespace Frostmoon;

[HarmonyPatch(typeof(NCharacterSelectButton),nameof(NCharacterSelectButton.Init))]
static class PortraitPresentation
{
    static void Postfix(NCharacterSelectButton __instance,CharacterModel character)
    {
        if(character is not FrostmoonCharacter || !__instance.IsNodeReady())return;
        foreach(var path in new[]{"%Icon","%IconAdd"})
        {
            var icon=__instance.GetNode<TextureRect>(path);
            icon.ExpandMode=TextureRect.ExpandModeEnum.IgnoreSize;
            icon.StretchMode=TextureRect.StretchModeEnum.KeepAspectCovered;
            icon.TextureFilter=CanvasItem.TextureFilterEnum.Linear;
        }
    }
}
