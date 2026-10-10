using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Combat;
using MegaCrit.Sts2.Core.Nodes.Rooms;
namespace Frostmoon;

// Called only by the explicit isolated visual-test command.
static class StatusVisualTests
{
    static async Task Wait(double seconds)=>await NGame.Instance!.ToSignal(NGame.Instance.GetTree().CreateTimer(seconds),"timeout");
    static IEnumerable<Node> Descendants(Node node)
    {
        foreach(var child in node.GetChildren()){yield return child;foreach(var next in Descendants(child))yield return next;}
    }
    static NPower NodeFor(PowerModel model)=>Descendants(NCombatRoom.Instance!).OfType<NPower>().Single(n=>ReferenceEquals(n.Model,model));
    static void Check(bool condition,string message)
    {if(!condition)throw new Exception(message);GD.Print("[FrostmoonStatus] PASS "+message);}
    static async Task Screenshot(string output,string name)
    {
        await Wait(.01);
        RenderingServer.ForceDraw();
        var result=NGame.Instance!.GetViewport().GetTexture().GetImage().SavePng(Path.Combine(output,name+".png"));
        Check(result==Error.Ok,"saved "+name);
    }
    public static async Task Run(Player player,string output)
    {
        Directory.CreateDirectory(output);
        var state=player.Creature.GetPower<FrostmoonState>()!;
        // Exercise the contextual UI in the real game, then restore the opening state.
        var original=(state.FormValue,state.Debt,state.Armed,state.BlockedThrough,state.EmberTurn);
        async Task ShowState(string name)
        {
            NCombatRoom.Instance!.GetCreatureNode(player.Creature)!.ShowHoverTips(state.HoverTips);
            await Screenshot(output,name);
            NCombatRoom.Instance!.GetCreatureNode(player.Creature)!.HideHoverTips();
        }
        Check(state.CompactReadout=="冰 · 霜 2/6" && state.Description.GetFormattedText().Split('\n').Length==3,"opening UI has one readout line and three tooltip lines");
        await ShowState("tooltip-ice");
        state.FormValue=(int)Form.Moon;state.Debt=5;
        Check(state.CompactReadout.Contains("回生 5") && state.Description.GetFormattedText().Contains("攻击附痕") && !state.Description.GetFormattedText().Contains("技能生霜"),"moon shows recovery and only its active passive counter");
        await ShowState("tooltip-moon");
        state.FormValue=(int)Form.Blood;state.Armed=false;state.BlockedThrough=state.Turn+1;
        Check(state.Description.GetFormattedText().Contains("×2") && !state.Description.GetFormattedText().Contains("准备"),"active Blood Moon shows its effect instead of rearm instructions");
        await ShowState("tooltip-blood");
        state.FormValue=(int)Form.Ice;state.EmberTurn=state.Turn+1;
        Check(state.Description.GetFormattedText().Contains("冷却中") && state.Description.GetFormattedText().Contains("≥40") && state.Description.GetFormattedText().Contains("余烬覆雪"),"cooldown preserves recovery threshold and next-turn reminder");
        await ShowState("tooltip-cooldown");
        state.Armed=true;
        Check(state.Description.GetFormattedText().Contains("冷却中") && !state.Description.GetFormattedText().Contains("时触发"),"rearmed state still reports cooldown without promising a trigger");
        (state.FormValue,state.Debt,state.Armed,state.BlockedThrough,state.EmberTurn)=original;
        Check(state.Frost==2 && NodeFor(state).GetNode("%AmountLabel").Get("text").AsString()=="2","opening frost counter shows the starter relic's 2 frost");
        var combat=state.CombatState;
        var enemies=combat.Enemies.Where(e=>e.IsAlive).Take(2).ToArray();
        foreach(var enemy in enemies){enemy.SetMaxHpInternal(1000);enemy.SetCurrentHpInternal(1000);}
        var ctx=new BlockingPlayerChoiceContext();var source=combat.CreateCard<FmC05>(player);
        var other=await PowerCmd.Apply<MoonMark>(ctx,enemies[1],4,player.Creature,source);
        state.AddFrost(3);
        Check(ReferenceEquals(NodeFor(state).GetNode<TextureRect>("%Icon").Texture,StatusTextures.Frost),"bright frost texture loaded in native power node");
        for(int i=0;i<=8;i++)
            Check(StatusTextures.Moon(i,true).GetImage().SavePng(Path.Combine(output,$"moon-{i}.png"))==Error.Ok,$"export moon stage {i}");
        StatusTextures.LargeFrost.GetImage().SavePng(Path.Combine(output,"frost.png"));
        MoonMark? current=null;
        for(int i=1;i<=8;i++)
        {
            current=await PowerCmd.Apply<MoonMark>(ctx,enemies[0],1,player.Creature,source);
            await Wait(.04);
            Check(current!.DisplayAmount==i && ReferenceEquals(NodeFor(current).GetNode<TextureRect>("%Icon").Texture,StatusTextures.Moon(i)), $"native icon follows {i}/8 and keeps numeric counter");
            Check(other!.Amount==4 && ReferenceEquals(NodeFor(other).GetNode<TextureRect>("%Icon").Texture,StatusTextures.Moon(4)),"second enemy remains 4/8");
            Check(current.BigIcon.GetSize()==new Vector2(64,64),"native application effect keeps original texture size");
            if(i==8)
            {
                var pulse=Descendants(NGame.Instance!.GetTree().Root).OfType<TextureRect>().FirstOrDefault(n=>n.Name=="FrostmoonFullMoonPulse");
                Check(pulse!=null && pulse.Size.X<=NodeFor(current).GetNode<TextureRect>("%Icon").Size.X+1,"full-moon pulse stays at status-icon size");
            }
            if(i is 1 or 4 or 7 or 8)await Screenshot(output,"combat-moon-"+i);
        }
        int hp=enemies[0].CurrentHp;
        await state.Mark(ctx,enemies[0],2,source);
        Check(state.Marks(enemies[0])?.Amount==2 && enemies[0].CurrentHp==hp-16,"10 stacks resolve one Eclipse and retain 2 stacks");
        current=state.Marks(enemies[0])!;
        Check(ReferenceEquals(NodeFor(current).GetNode<TextureRect>("%Icon").Texture,StatusTextures.Moon(2)),"rollover icon returns to 2/8");
        await Screenshot(output,"combat-rollover");
        await PowerCmd.ModifyAmount(ctx,current,-2,player.Creature,source);
        Check(state.Marks(enemies[0])==null,"zero stacks remove the status normally");
        await Wait(.6);
        Check(!Descendants(NGame.Instance!.GetTree().Root).Any(n=>n.Name=="FrostmoonFullMoonPulse"),"full-moon pulse frees itself");
        await state.Mark(ctx,enemies[0],7,source);await Wait(.2);
        await Screenshot(output,"combat-final");
        GD.Print("[FrostmoonStatus] COMPLETE native 1..8 icons, independent enemies, rollover, removal and pulse cleanup.");
    }
}
