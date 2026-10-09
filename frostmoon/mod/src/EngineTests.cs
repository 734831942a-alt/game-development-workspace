using MegaCrit.Sts2.Core.Helpers;
using MegaCrit.Sts2.Core.Nodes;
using MegaCrit.Sts2.Core.Nodes.Screens.MainMenu;
using MegaCrit.Sts2.Core.Runs;
using MegaCrit.Sts2.Core.Multiplayer;
using MegaCrit.Sts2.Core.TestSupport;
using MegaCrit.Sts2.Core.Unlocks;
using MegaCrit.Sts2.Core.Models.Monsters;
using MegaCrit.Sts2.Core.Entities.CardRewardAlternatives;
using System.Reflection;
namespace Frostmoon;

// Explicit opt-in, isolated application only. No execution in a user's normal game.
[HarmonyPatch(typeof(NMainMenu),nameof(NMainMenu._Ready))]
static class EngineTests
{
    static bool started;
    static void Postfix()
    {
        if(started || !CommandLineHelper.HasArg("frostmoon-test") || !CommandLineHelper.HasArg("frostmoon-engine-tests"))return;
        started=true; TaskHelper.RunSafely(Run());
    }
    sealed class Selector : ICardSelector
    {
        public string? Choice;
        public Task<IEnumerable<CardModel>> GetSelectedCards(IEnumerable<CardModel> options,int min,int max)
        {
            var list=options.ToList();var chosen=list.FirstOrDefault(c=>c is FrostmoonCard f && f.Code==Choice);
            return Task.FromResult<IEnumerable<CardModel>>(chosen!=null ? [chosen] : list.Take(Math.Max(1,min)).ToList());
        }
        public CardRewardSelection GetSelectedCardReward(IReadOnlyList<CardCreationResult> options,IReadOnlyList<CardRewardAlternative> alternatives)=>throw new NotSupportedException();
    }
    static int passed;
    static void Check(bool test,string message) { if(!test)throw new Exception("ASSERT: "+message);passed++;GD.Print("[FrostmoonTest] PASS "+message); }
    static async Task Run()
    {
        try
        {
            await NGame.Instance!.ToSignal(NGame.Instance.GetTree().CreateTimer(4),"timeout");
            TestMode.IsOn=true;
            var selector=new Selector();using var selection=CardSelectCmd.UseSelector(selector);
            PlaytestConfig.StartingDeck=0;
            var p=Player.CreateForNewRun<FrostmoonCharacter>(UnlockState.all,1);
            var run=RunState.CreateForTest([p],seed:"FROSTMOON");
            RunManager.Instance.SetUpTest(run,new NetSingleplayerGameService());
            var combat=new CombatState(runState:run);
            combat.AddPlayer(p);
            var enemy=combat.CreateCreature(ModelDb.Monster<BigDummy>().ToMutable(),CombatSide.Enemy,null);
            combat.AddCreature(enemy);enemy.SetMaxHpInternal(100000);enemy.SetCurrentHpInternal(100000);
            CombatManager.Instance.SetUpCombat(combat);
            AccessTools.Property(typeof(CombatManager),nameof(CombatManager.IsInProgress)).SetValue(CombatManager.Instance,true);
            var ctx=new BlockingPlayerChoiceContext();
            FrostmoonState State()=>p.Creature.GetPower<FrostmoonState>()!;
            async Task<FrostmoonCard> Play(string code,bool up=false)
            {
                var card=(FrostmoonCard)combat.CreateCard(CardCatalog.Canonical(code),p);
                if(up)CardCmd.Upgrade(card);
                await CardPileCmd.Add(card,PileType.Hand);
                if(card.EnergyCost.CostsX)card.EnergyCost.CapturedXValue=3;
                await card.OnPlayWrapper(ctx,card.TargetType==TargetType.AnyEnemy?enemy:null,false,new ResourceInfo { EnergySpent=3,EnergyValue=3,StarsSpent=0,StarValue=0 },true);
                return card;
            }
            async Task Reset()
            {
                p.Creature.RemoveAllPowersInternalExcept();enemy.RemoveAllPowersInternalExcept();
                p.Creature.SetCurrentHpInternal(72);p.Creature.LoseBlockInternal(p.Creature.Block);enemy.LoseBlockInternal(enemy.Block);
                p.PlayerCombatState!.Phase=PlayerTurnPhase.Play;
                var s=await PowerCmd.Apply<FrostmoonState>(ctx,p.Creature,1,p.Creature,null);s!.Turn=1;s.Frost=2;
                foreach(var pile in new[]{PileType.Hand,PileType.Draw,PileType.Discard,PileType.Exhaust})
                    foreach(var c in pile.GetPile(p).Cards.ToArray())await CardPileCmd.RemoveFromCombat(c,true);
                for(int i=0;i<8;i++)await CardPileCmd.Add(combat.CreateCard<FmB01>(p),PileType.Draw);
                await CardPileCmd.Add(combat.CreateCard<FmB02>(p),PileType.Discard);
                await CardPileCmd.Add(combat.CreateCard<FmC09>(p),PileType.Discard);
                await PlayerCmd.SetEnergy(3,p);
            }
            await Reset();
            await Play("B02");await Play("B02");await Play("B02");
            Check(State().Frost==4,"Ice grants frost only for first two skills");
            await Reset();await Play("B03");var hp=p.Creature.CurrentHp;await Play("C06");
            Check(State().Form==Form.Moon && p.Creature.CurrentHp==hp-1 && State().Debt==1 && State().Frost==1,"Moon pays once and consumes one frost");
            Check(State().Marks(enemy)?.Amount==6,"Moon marks resolve after text");
            await Reset();p.Creature.SetCurrentHpInternal(30);await Play("C01");
            Check(State().Form==Form.Blood && p.Creature.CurrentHp==28,"Threshold card triggers Blood after its text");
            int ehp=enemy.CurrentHp;await Play("B01");Check(ehp-enemy.CurrentHp==12,"Blood doubles following attack");
            await State().BeforeSideTurnEnd(ctx,CombatSide.Player,[p.Creature]);Check(State().Form==Form.Ice && State().EmberTurn==2,"Blood exits and schedules recovery token");
            await State().BeforeSideTurnStart(ctx,CombatSide.Player,[p.Creature],combat);await State().AfterPlayerTurnStartLate(ctx,p);
            Check(PileType.Hand.GetPile(p).Cards.OfType<FrostmoonCard>().Any(c=>c.Code=="T01"),"Ember generated next turn");
            Check(State().Form==Form.Ice,"Next turn remains on cooldown");
            await Reset();await Play("C12");Check(State().Debt==3,"Explicit HP payment adds recoverable debt");
            await CreatureCmd.Heal(p.Creature,99);Check(State().Debt==0 && p.Creature.CurrentHp==72,"Overheal removes only actual debt");
            await Reset();p.Creature.SetCurrentHpInternal(50);State().Debt=4;await State().Recover(8);Check(p.Creature.CurrentHp==54 && State().Debt==0,"Recovery cannot repair enemy damage");
            await Reset();ehp=enemy.CurrentHp;await State().Mark(ctx,enemy,10,combat.CreateCard<FmC05>(p));Check(ehp-enemy.CurrentHp==16 && State().Marks(enemy)?.Amount==2,"Eight marks consume threshold and preserve overflow");
            await Reset();State().FormValue=(int)Form.Blood;ehp=enemy.CurrentHp;await State().Mark(ctx,enemy,8,combat.CreateCard<FmC05>(p));Check(ehp-enemy.CurrentHp==32,"Blood Eclipse is doubled exactly once");
            await Reset();selector.Choice="Q04";await Play("U22");Check(p.Creature.CurrentHp==68 && State().Debt==4,"Bloodline selected payment is implemented");selector.Choice=null;
            await Reset();p.Creature.SetCurrentHpInternal(3);var costly=combat.CreateCard<FmC12>(p);
            Check(!costly.CanPlay(out _,out _),"Lethal primary HP payment is rejected before play");
            await Reset();State().FormValue=(int)Form.Moon;p.Creature.SetCurrentHpInternal(3);await Play("C01");
            Check(p.Creature.CurrentHp==1 && State().Debt==2 && State().MoonAttacks==0,"Unsafe Moon surcharge is skipped without spending its quota");
            await Reset();State().FormValue=(int)Form.Moon;await Play("C17");Check(State().MoonAttacks==0 && State().Debt==0,"AOE attack does not consume Moon passive");
            await Reset();State().FormValue=(int)Form.Moon;await Play("C02");Check(State().Debt==1 && State().MoonAttacks==1,"Multi-hit attack pays Moon surcharge once");
            await Reset();State().FormValue=(int)Form.Moon;p.Creature.SetCurrentHpInternal(29);State().Debt=6;await Play("U19");Check(State().Form==Form.Moon && p.Creature.CurrentHp==35,"Card healing above threshold prevents Blood entry");
            await Reset();State().FormValue=(int)Form.Blood;State().Armed=false;p.Creature.SetCurrentHpInternal(20);State().Debt=8;int drawBefore=PileType.Draw.GetPile(p).Cards.Count;await Play("R01");
            Check(PileType.Draw.GetPile(p).Cards.Count==drawBefore,"Blood Moon power does not backfill entry draw");
            await State().Mark(ctx,enemy,8,combat.CreateCard<FmC05>(p));Check(p.Creature.CurrentHp==24,"Blood Moon power played during Blood still rewards its first Eclipse");
            await Reset();State().FormValue=(int)Form.Blood;State().Armed=false;p.Creature.SetCurrentHpInternal(38);State().Debt=10;await Play("U19");Check(State().Form==Form.Blood && !State().Armed,"Healing during Blood neither exits nor rearms it");
            await State().Switch(ctx,Form.Ice);Check(State().Armed,"Exiting Blood above recovery threshold rearms");
            await Reset();p.PlayerCombatState!.Phase=PlayerTurnPhase.AutoPostPlay;p.Creature.SetCurrentHpInternal(30);await Play("C01");Check(State().Form==Form.Ice,"End-turn autoplay cannot trigger Blood");p.PlayerCombatState.Phase=PlayerTurnPhase.Play;
            await Reset();State().Frost=0;var frostCost=combat.CreateCard<FmU08>(p);Check(!frostCost.CanPlay(out _,out _),"Mandatory Frost cost is checked before play");
            await Reset();State().AddFrost(99);Check(State().Frost==6,"Frost overflow is discarded");
            await Reset();await PowerCmd.Apply<MegaCrit.Sts2.Core.Models.Powers.ArtifactPower>(ctx,enemy,1,enemy,null);await State().Mark(ctx,enemy,8,combat.CreateCard<FmC05>(p));Check(State().Marks(enemy)==null || State().Marks(enemy)!.Amount==0,"Artifact blocks the mark packet");
            await Reset();await PowerCmd.Apply<MegaCrit.Sts2.Core.Models.Powers.StrengthPower>(ctx,p.Creature,10,p.Creature,null);await PowerCmd.Apply<MegaCrit.Sts2.Core.Models.Powers.VulnerablePower>(ctx,enemy,2,p.Creature,null);ehp=enemy.CurrentHp;await State().Mark(ctx,enemy,8,combat.CreateCard<FmC05>(p));Check(ehp-enemy.CurrentHp==16,"Eclipse ignores Strength and Vulnerable");
            await Reset();await Play("R12");ehp=enemy.CurrentHp;await State().Mark(ctx,enemy,8,combat.CreateCard<FmC05>(p));Check(ehp-enemy.CurrentHp==18,"Unupgraded Shattered Moon resolves six hits of three");
            await Reset();await Play("R12",true);ehp=enemy.CurrentHp;await State().Mark(ctx,enemy,8,combat.CreateCard<FmC05>(p));Check(ehp-enemy.CurrentHp==24,"Upgraded Shattered Moon resolves six hits of four");
            await Reset();ehp=enemy.CurrentHp;await Play("R06");Check(ehp-enemy.CurrentHp==28,"X=3 Blood Blade deals four hits");
            await Reset();await Play("U03");int blocks=p.Creature.Block;enemy.GainBlockInternal(100);await State().Mark(ctx,enemy,8,combat.CreateCard<FmC05>(p));Check(p.Creature.Block-blocks==4,"Blocked Eclipse hits still grant Tide block");
            foreach(var def in CardCatalog.All.Values.Where(d=>!d.Code.StartsWith("Q")))
            foreach(bool up in new[]{false,true})
            {
                await Reset();State().Frost=6;State().Debt=10;p.Creature.SetCurrentHpInternal(60);
                await State().Mark(ctx,enemy,4,combat.CreateCard<FmC05>(p));
                var card=await Play(def.Code,up);
                Check(card.GetDescriptionForPile(PileType.Hand)!=null,$"{def.Code}{(up?"+":"")} plays without exception");
            }
            await Reset();var sentinel=combat.CreateCreature(ModelDb.Monster<BigDummy>().ToMutable(),CombatSide.Enemy,null);combat.AddCreature(sentinel);sentinel.GainBlockInternal(10000);
            enemy.SetCurrentHpInternal(1);p.Creature.SetCurrentHpInternal(50);State().Debt=10;await Play("R11");
            Check(p.Creature.CurrentHp==51 && State().Debt==9,"Red Lotus refunds actual HP lost, excludes block and overkill");
            GD.Print($"[FrostmoonTest] COMPLETE: {passed} checks passed");
            NGame.Instance.GetTree().Quit(0);
        }
        catch(Exception e) { GD.PrintErr("[FrostmoonTest] FAILED "+e);NGame.Instance!.GetTree().Quit(2); }
    }
}
