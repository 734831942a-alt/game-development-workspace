using System.Reflection;
using System.Runtime.CompilerServices;
using MegaCrit.Sts2.Core.Nodes.Combat;
namespace Frostmoon;

// Render small status symbols from vector sources. Textures are shared, state is per power instance.
static class StatusTextures
{
    static readonly Dictionary<string,Texture2D> cache=new();
    public static int MoonStage(int amount)=>Math.Clamp(amount,0,8);
    public static Texture2D Moon(int amount,bool large=false)=>Get($"moon-{MoonStage(amount)}",large);
    public static Texture2D Frost=>Get("frost");
    public static Texture2D LargeFrost=>Get("frost",true);
    static Texture2D Get(string name,bool large=false)
    {
        string key=name+(large?"-256":"-64");
        if(cache.TryGetValue(key,out var texture))return texture;
        string svg=Godot.FileAccess.GetFileAsString($"res://Frostmoon/ui/status-v3/{name}.svg");
        using var image=new Image();
        if(image.LoadSvgFromString(svg,large?1f:.25f)!=Error.Ok)throw new InvalidOperationException("Invalid status icon: "+name);
        return cache[key]=ImageTexture.CreateFromImage(image);
    }
}

[HarmonyPatch]
static class StatusTextureOverride
{
    static IEnumerable<MethodBase> TargetMethods()
    {
        yield return AccessTools.PropertyGetter(typeof(PowerModel),nameof(PowerModel.Icon));
        yield return AccessTools.PropertyGetter(typeof(PowerModel),nameof(PowerModel.BigIcon));
    }
    static bool Prefix(PowerModel __instance,ref Texture2D __result)
    {
        // Preserve the original 64px runtime icon dimensions; 256px exports are for visual inspection.
        if(__instance is MoonMark){__result=StatusTextures.Moon(__instance.IsCanonical?8:__instance.Amount);return false;}
        if(__instance is FrostmoonState){__result=StatusTextures.Frost;return false;}
        return true;
    }
}

[HarmonyPatch(typeof(NPower),"RefreshAmount")]
static class StatusAmountPresentation
{
    sealed class Seen { public PowerModel? Model; public int Amount; }
    static readonly ConditionalWeakTable<NPower,Seen> previous=new();
    static void Postfix(NPower __instance)
    {
        if(!__instance.IsNodeReady())return;
        var model=__instance.Model;
        if(model is not MoonMark && model is not FrostmoonState)return;
        var icon=__instance.GetNode<TextureRect>("%Icon");
        icon.Texture=model.Icon;icon.TextureFilter=CanvasItem.TextureFilterEnum.Linear;
        __instance.GetNode<CpuParticles2D>("%PowerFlash").Texture=model is MoonMark?StatusTextures.Moon(8):StatusTextures.Frost;
        var seen=previous.GetOrCreateValue(__instance);
        int before=ReferenceEquals(seen.Model,model)?seen.Amount:0;
        seen.Model=model;seen.Amount=model.Amount;
        if(model is MoonMark && model.Amount>=8 && before<8)PulseFullMoon(__instance,icon);
    }
    static void PulseFullMoon(NPower power,TextureRect icon)
    {
        // Keep the completed moon visible briefly even when consuming 8 removes the native power node.
        // This is a detached visual only: no waits, stack changes or combat timing changes.
        var transform=icon.GetGlobalTransformWithCanvas();
        var pulse=new TextureRect { Name="FrostmoonFullMoonPulse",ExpandMode=TextureRect.ExpandModeEnum.IgnoreSize,
            Texture=StatusTextures.Moon(8),Position=transform.Origin,Scale=transform.Scale.Abs(),Size=icon.Size,
            StretchMode=TextureRect.StretchModeEnum.KeepAspectCentered,
            TextureFilter=CanvasItem.TextureFilterEnum.Linear,MouseFilter=Control.MouseFilterEnum.Ignore,ZIndex=100 };
        power.GetTree().Root.AddChild(pulse);
        pulse.PivotOffset=icon.Size/2;
        var tween=pulse.CreateTween();
        tween.TweenProperty(pulse,"scale",pulse.Scale*1.18f,.12);
        tween.TweenInterval(.12);
        tween.TweenProperty(pulse,"modulate:a",0f,.24);
        tween.TweenCallback(Callable.From(pulse.QueueFree));
    }
}
