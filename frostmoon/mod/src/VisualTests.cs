using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Screens.MainMenu;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Saves;
using MegaCrit.Sts2.Core.Rooms;
using MegaCrit.Sts2.Core.Models.Encounters;
using MegaCrit.Sts2.Core.Nodes.Screens.CharacterSelect;
namespace Frostmoon;
[HarmonyPatch(typeof(NMainMenu),nameof(NMainMenu._Ready))]
static class VisualTests
{
    static bool started;
    static void Postfix(NMainMenu __instance)
    {
        if(started || !CommandLineHelper.HasArg("frostmoon-test") || (!CommandLineHelper.HasArg("frostmoon-visual-test") && !CommandLineHelper.HasArg("frostmoon-select-test")))return;
        started=true;TaskHelper.RunSafely(Run(__instance));
    }
    static async Task Wait(float seconds) => await NGame.Instance!.ToSignal(NGame.Instance.GetTree().CreateTimer(seconds),"timeout");
    static async Task Run(NMainMenu menu)
    {
        try
        {
            await Wait(5);
            SaveManager.Instance.SetFtuesEnabled(false);PlaytestConfig.StartingDeck=1;
            var game=NGame.Instance!;
            if(CommandLineHelper.HasArg("frostmoon-select-test"))
            {
                var screen=menu.SubmenuStack.GetSubmenuType<NCharacterSelectScreen>();screen.InitializeSingleplayer();menu.SubmenuStack.Push(screen);
                await Wait(1);
                var originalPanelPosition=screen.GetNode<Control>("InfoPanel").Position;
                var button=(NCharacterSelectButton)screen.FindChild("FROSTMOON-FROSTMOON_CHARACTER_button",true,false);
                button.Select();await Wait(3);
                var panel=screen.GetNode<Control>("InfoPanel");
                GD.Print($"[FrostmoonVisual] Select layout: screen={screen.Size}, panel={panel.Position}/{panel.Size}; title={ModelDb.Character<FrostmoonCharacter>().Title.GetFormattedText()}");
                if(panel.Position.X < screen.Size.X*.5f || panel.Position.X+panel.Size.X > screen.Size.X)throw new Exception("Character information panel is outside the right half.");
                if(ModelDb.Character<FrostmoonCharacter>().Title.GetFormattedText()!="小木曾和纱")throw new Exception("Character name was not localized.");
                var vanilla=screen.FindChildren("*","",true,false).OfType<NCharacterSelectButton>().First(b=>!b.IsRandom && !b.IsLocked && b.Character is not FrostmoonCharacter);
                vanilla.Select();await Wait(.7f);
                if(!panel.Position.IsEqualApprox(originalPanelPosition))throw new Exception("Native character information panel did not return to its original position.");
                button.Select();await Wait(.7f);
                GD.Print("[FrostmoonVisual] Native character layout restored and custom cover reselected.");
                RenderingServer.ForceDraw();
                game.GetViewport().GetTexture().GetImage().SavePng(CommandLineHelper.GetValue("frostmoon-screenshot")!);
                GD.Print("[FrostmoonVisual] Character select screenshot saved.");game.GetTree().Quit();return;
            }
            var run=await game.StartNewSingleplayerRun(ModelDb.Character<FrostmoonCharacter>(),false,ActModel.GetDefaultList(),[],"FROSTMOON",GameMode.Standard);
            await RunManager.Instance.EnterRoomDebug(RoomType.Monster,model:ModelDb.Encounter<SlimesWeak>().ToMutable());
            for(int i=0;i<120 && (run.Players[0].PlayerCombatState?.Phase!=PlayerTurnPhase.Play || PileType.Hand.GetPile(run.Players[0]).Cards.Count<5);i++)await Wait(.1f);
            await Wait(2);
            if(run.Players[0].PlayerCombatState?.Phase!=PlayerTurnPhase.Play || PileType.Hand.GetPile(run.Players[0]).Cards.Count!=5)throw new Exception("Opening hand did not finish drawing.");
            var s=run.Players[0].Creature.GetPower<FrostmoonState>();
            GD.Print($"[FrostmoonVisual] Combat loaded. HP={run.Players[0].Creature.CurrentHp}; Frost={s?.Frost}; hand={PileType.Hand.GetPile(run.Players[0]).Cards.Count}");
            if(CommandLineHelper.HasArg("frostmoon-status-test"))
                await StatusVisualTests.Run(run.Players[0],CommandLineHelper.GetValue("frostmoon-status-dir") ?? throw new ArgumentException("--frostmoon-status-dir is required"));
            var output=CommandLineHelper.GetValue("frostmoon-screenshot");
            if(output!=null) {RenderingServer.ForceDraw();game.GetViewport().GetTexture().GetImage().SavePng(output);GD.Print("[FrostmoonVisual] Screenshot saved.");}
            if(CommandLineHelper.HasArg("frostmoon-visual-exit")){await Wait(1);game.GetTree().Quit();}
        }
        catch(Exception e){GD.PrintErr("[FrostmoonVisual] FAILED "+e);NGame.Instance!.GetTree().Quit(2);}
    }
}
