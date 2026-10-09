using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Cards;
using MegaCrit.Sts2.Core.Nodes.Screens.MainMenu;
namespace Frostmoon;

// Explicit isolated visual export. Uses the actual game's card node, fonts and rarity frames.
[HarmonyPatch(typeof(NMainMenu),nameof(NMainMenu._Ready))]
static class ArtGalleryTests
{
    static bool started;
    static void Postfix()
    {
        if(started || !CommandLineHelper.HasArg("frostmoon-test") || !CommandLineHelper.HasArg("frostmoon-art-gallery"))return;
        started=true;TaskHelper.RunSafely(Run());
    }
    static async Task Wait(double seconds) => await NGame.Instance!.ToSignal(NGame.Instance.GetTree().CreateTimer(seconds),"timeout");
    static async Task Run()
    {
        try
        {
            await Wait(5);
            string output=CommandLineHelper.GetValue("frostmoon-art-dir") ?? throw new ArgumentException("--frostmoon-art-dir is required");
            Directory.CreateDirectory(output);
            var codes=CommandLineHelper.GetValue("frostmoon-art-codes")?.Split(',') ?? CardCatalog.All.Keys.Where(c=>!c.StartsWith("Q")).ToArray();
            var viewport=new SubViewport { Size=new Vector2I(420,570),TransparentBg=true,RenderTargetUpdateMode=SubViewport.UpdateMode.Always,OwnWorld3D=true };
            NGame.Instance!.AddChild(viewport);
            int count=0;
            foreach(string code in codes)
            {
                var original=(FrostmoonCard)CardCatalog.Canonical(code);
                if(!ResourceLoader.Exists(original.CustomPortraitPath))throw new Exception($"Missing art: {code} {original.CustomPortraitPath}");
                var portrait=ResourceLoader.Load<Texture2D>(original.CustomPortraitPath);
                if(portrait==null || portrait.GetWidth()<512 || portrait.GetHeight()<512)throw new Exception("Invalid texture: "+code);
                foreach(bool upgraded in new[]{false,true})
                {
                    var model=(CardModel)original.ToMutable();
                    if(upgraded)CardCmd.Upgrade(model);
                    var card=NCard.Create(model) ?? throw new Exception("NCard.Create returned null");
                    viewport.AddChild(card);
                    card.Position=new Vector2(210,285);card.Scale=new Vector2(1.15f,1.15f);
                    card.SetForceUnpoweredPreview(true);
                    card.UpdateVisuals(PileType.None,CardPreviewMode.Normal);
                    await Wait(.12);
                    // macOS can stop automatic draws while the test window is covered.
                    RenderingServer.ForceDraw();
                    string name=code+(upgraded?"-upgrade":"-base")+".png";
                    var result=viewport.GetTexture().GetImage().SavePng(Path.Combine(output,name));
                    if(result!=Error.Ok)throw new Exception($"Save failed: {name} {result}");
                    card.QueueFree();await Wait(.03);count++;
                }
                GD.Print($"[FrostmoonArt] PASS {code} {CardCatalog.Get(code).Name} {portrait.GetWidth()}x{portrait.GetHeight()}");
            }
            var vanilla=ModelDb.AllCards.First(c=>c is not FrostmoonCard && c.Type==CardType.Attack && c.Rarity==CardRarity.Basic);
            var reused=NCard.Create((CardModel)vanilla.ToMutable())!;viewport.AddChild(reused);
            var reusedPortrait=reused.GetNode<TextureRect>("%Portrait");
            var originalStretch=reusedPortrait.StretchMode;var originalFilter=reusedPortrait.TextureFilter;
            reused.Model=(CardModel)CardCatalog.Canonical("B01").ToMutable();
            if(reusedPortrait.StretchMode!=TextureRect.StretchModeEnum.KeepAspectCovered)throw new Exception("Frostmoon crop not applied");
            reused.Model=(CardModel)vanilla.ToMutable();
            if(reusedPortrait.StretchMode!=originalStretch || reusedPortrait.TextureFilter!=originalFilter)throw new Exception("Vanilla card layout not restored");
            reused.QueueFree();
            GD.Print("[FrostmoonArt] PASS pooled card restores original vanilla layout and filtering.");
            foreach(var code in new[]{"Q00","Q02","Q04","QIC","QMO"})
                if(!ResourceLoader.Exists(((FrostmoonCard)CardCatalog.Canonical(code)).CustomPortraitPath))throw new Exception("Missing choice art: "+code);
            GD.Print($"[FrostmoonArt] COMPLETE {codes.Length} portraits, {count} native card renders, 5 choice portraits.");
            viewport.QueueFree();NGame.Instance.GetTree().Quit();
        }
        catch(Exception e){GD.PrintErr("[FrostmoonArt] FAILED "+e);NGame.Instance!.GetTree().Quit(2);}
    }
}
