using MegaCrit.Sts2.Core.Models.Powers;
namespace Frostmoon;

public enum Form { Ice, Moon, Blood }
public sealed class PlaySnapshot
{
    public Form Form;
    public int MoonMarks, ChosenPayment, Eclipses;
    public bool Finished;
}
public class FrostmoonState : CustomPowerModel
{
    public int FormValue { get; set; }
    public int Frost { get; set; }
    public int Debt { get; set; }
    public int Turn { get; set; }
    public bool Armed { get; set; } = true;
    public int BlockedThrough { get; set; } = -1;
    public int EmberTurn { get; set; } = -1;
    public int IceSkills { get; set; }
    public int MoonAttacks { get; set; }
    public int Switches { get; set; }
    public int Payments { get; set; }
    public int Eclipses { get; set; }
    public bool IceRefund { get; set; }
    public bool BloodRefund { get; set; }
    public int RetainedBlock { get; set; }
    public Form Form => (Form)FormValue;
    public Player Player => Owner.Player!;
    public int Low => (int)Math.Floor(Owner.MaxHp * .4m);
    public int High => (int)Math.Ceiling(Owner.MaxHp * .55m);
    public int FrostCap => 6 + Sum("U24", 2, 3);
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override int DisplayAmount => Frost;
    public override Color AmountLabelColor => new("bcfaff");
    public override string CustomPackedIconPath => "res://Frostmoon/ui/ice.png";
    public override string CustomBigIconPath => CustomPackedIconPath;
    public override List<(string,string)> Localization => new PowerLoc("霜月 · 双相", "{Status}", "{Status}");
    protected override string SmartDescriptionLocKey => "FROSTMOON_NO_SMART_DESCRIPTION";
    public override LocString Description { get { var loc=base.Description; FillDescription(loc); return loc; } }
    void FillDescription(LocString loc)
    {
        loc.Add("Status", IsCanonical ? "冰：每回合前2张技能各获得1霜。\n月：前2张单体攻击支付1生命，附加月痕。\n血月：攻击和月蚀伤害翻倍，回合结束返回冰。" :
            $"形态：{new[]{"冰","月","血月"}[FormValue]}　霜：{Frost}/{FrostCap}\n可回收生命：{Debt}\n血月门槛：≤{Low}　重新准备：≥{High}\n血月：{(Armed ? "已准备" : "需恢复生命")}{(Turn <= BlockedThrough ? "／冷却中" : "")}\n冰技能：{IceSkills}/2　月攻击：{MoonAttacks}/2\n{(EmberTurn > Turn ? "下回合获得余烬覆雪。" : "")}");
    }
    sealed class Data { public readonly Dictionary<CardPlay,PlaySnapshot> Plays = new(); }
    protected override object InitInternalData() => new Data();
    public PlaySnapshot Snapshot(CardPlay p) => GetInternalData<Data>().Plays[p];
    public IEnumerable<FrostmoonAbility> Abilities(string code) => Owner.Powers.OfType<FrostmoonAbility>().Where(p => p.Code == code);
    public int Sum(string code, int normal, int upgraded) => Abilities(code).Sum(p => p.Amount > 1 ? upgraded : normal);
    public void AddFrost(int n) { Frost = Math.Clamp(Frost + n, 0, FrostCap); InvokeDisplayAmountChanged(); InvokeExecutionFinished(); }
    public int SpendFrost(int max) { var n = Math.Min(max, Frost); Frost -= n; InvokeDisplayAmountChanged(); return n; }
    public async Task Recover(int n)
    {
        if (!Owner.IsAlive) return;
        n = Math.Min(n, Math.Min(Debt, Owner.MaxHp - Owner.CurrentHp));
        if (n > 0) await CreatureCmd.Heal(Owner, n);
    }
    public void Rearm() { if (Form != Form.Blood && Owner.CurrentHp >= High) Armed = true; }
    public async Task<bool> Pay(PlayerChoiceContext ctx, int n, CardModel card)
    {
        if (n <= 0) return true;
        if (!Owner.IsAlive || Owner.CurrentHp <= n) return false;
        Debt += n; Payments++;
        await CreatureCmd.SetCurrentHp(Owner, Owner.CurrentHp - n);
        if (Payments == 1)
        {
            await Block(Sum("U20",3,3));
            await Draw(ctx, Sum("U20",1,1));
        }
        return true;
    }
    public Task Block(decimal n) => n <= 0 || !Owner.IsAlive ? Task.CompletedTask : CreatureCmd.GainBlock(Owner, n, ValueProp.Unpowered, null);
    public async Task Draw(PlayerChoiceContext ctx, int n) { if(n>0 && Owner.IsAlive) await CardPileCmd.Draw(ctx,n,Player); }
    public async Task Switch(PlayerChoiceContext ctx, Form next)
    {
        var old = Form;
        if(old == next) return;
        FormValue = (int)next;
        if(old == Form.Blood) { EmberTurn = Turn + 1; Rearm(); }
        else if (next != Form.Blood)
        {
            Switches++;
            if(Switches == 1)
            {
                if(Player.Relics.Any(r => r is TwinPhasePendant)) await Block(3);
                await Draw(ctx,Sum("U04",1,2));
            }
            if(Switches <= 2) await Draw(ctx,Sum("R02",1,1));
            if(Switches == 2) await PlayerCmd.GainEnergy(Sum("R02",1,1),Player);
        }
        InvokeExecutionFinished();
    }
    public async Task CheckBlood(PlayerChoiceContext ctx)
    {
        Rearm();
        if(Player.PlayerCombatState?.Phase != PlayerTurnPhase.Play)return;
        if(!Owner.IsAlive || Form == Form.Blood || !Armed || Turn <= BlockedThrough || Owner.CurrentHp > Low || CombatState.CurrentSide != Owner.Side) return;
        FormValue=(int)Form.Blood; Armed=false; BlockedThrough=Turn+1; BloodRefund=false;
        await Draw(ctx,Sum("R01",2,3));
        InvokeExecutionFinished();
    }
    public async Task Generate(PlayerChoiceContext ctx, string code, bool upgrade=false)
    {
        var card = CombatState.CreateCard(CardCatalog.Canonical(code),Player);
        if(upgrade) CardCmd.Upgrade(card);
        await CardPileCmd.AddGeneratedCardToCombat(card,PileType.Hand,Player);
    }
    public MoonMark? Marks(Creature target) => target.GetPowerInstances<MoonMark>().FirstOrDefault(p => p.Applier == Owner);
    public async Task<int> RemoveMarks(PlayerChoiceContext ctx, Creature target, int max)
    {
        var p=Marks(target); if(p==null)return 0;
        var n=Math.Min(p.Amount,max);
        await PowerCmd.ModifyAmount(ctx,p,-n,Owner,null);
        return n;
    }
    public async Task<int> Mark(PlayerChoiceContext ctx, Creature? target, int n, CardModel source)
    {
        if(target==null || !target.IsAlive || n<=0)return 0;
        var p = await PowerCmd.Apply<MoonMark>(ctx,target,n,Owner,source);
        int count=0;
        while(p!=null && p.Amount>=8 && target.IsAlive)
        {
            await PowerCmd.ModifyAmount(ctx,p,-8,Owner,source);
            await Eclipse(ctx,target,source); count++;
            p=Marks(target);
        }
        return count;
    }
    public async Task Eclipse(PlayerChoiceContext ctx, Creature target, CardModel source)
    {
        int hits=4+Sum("R12",2,2), perHit=Math.Max(1,4+Sum("R04",1,2)-Sum("R12",1,0));
        bool ice=Form==Form.Ice, blood=Form==Form.Blood;
        if(blood)perHit*=2;
        Eclipses++;
        foreach(var snap in GetInternalData<Data>().Plays.Values.Where(s=>!s.Finished))snap.Eclipses++;
        for(int i=0;i<hits && target.IsAlive;i++)
        {
            await CreatureCmd.Damage(ctx,target,perHit,ValueProp.Unpowered|ValueProp.Move,Owner,source);
            await Block(Sum("U03",1,2));
        }
        if(Eclipses<=2)AddFrost(Sum("U02",1,2));
        if(ice && !IceRefund) { IceRefund=true; await Recover(2); }
        if(Eclipses==1)
        {
            await Recover(Sum("R04",2,2));
            foreach(var p in Abilities("U23").ToArray())await Generate(ctx,"T02",p.Amount>1);
        }
        if(blood && !BloodRefund)
        {
            BloodRefund=true;
            await Recover(Sum("R01",4,4));
        }
    }
    public override async Task BeforeCardPlayed(CardPlay play)
    {
        if(play.Card.Owner!=Player)return;
        var ctx=CardContextPatch.Current(Player);
        var snap=new PlaySnapshot { Form=Form };
        GetInternalData<Data>().Plays[play]=snap;
        if(ctx==null)return;
        if(play.Card is FrostmoonCard f && f.Code=="U22")
            snap.ChosenPayment=await f.ChoosePayment(ctx);
        int primary=play.Card is FrostmoonCard fm ? fm.PrimaryPayment(snap.ChosenPayment) : 0;
        if(Form==Form.Moon && play.Card.Type==CardType.Attack && play.Card.TargetType==TargetType.AnyEnemy && MoonAttacks<2 && Owner.CurrentHp>primary+1)
        {
            MoonAttacks++;
            await Pay(ctx,1,play.Card);
            snap.MoonMarks=1+SpendFrost(1);
        }
    }
    public async Task FinishCard(PlayerChoiceContext ctx, CardPlay play)
    {
        if(!GetInternalData<Data>().Plays.TryGetValue(play,out var s) || s.Finished)return;
        if(s.Form==Form.Ice && play.Card.Type==CardType.Skill && IceSkills<2) { IceSkills++; AddFrost(1); }
        if(s.MoonMarks>0)await Mark(ctx,play.Target,s.MoonMarks,play.Card);
        if(play.Card is FrostmoonCard {Code:"U14"} && s.Eclipses>0){AddFrost(2);await Recover(2);}
        s.Finished=true;
        InvokeExecutionFinished();
    }
    public override async Task AfterCardPlayed(PlayerChoiceContext ctx, CardPlay play)
    { if(play.Card.Owner==Player)await FinishCard(ctx,play); }
    public override Task AfterCardPlayedLate(PlayerChoiceContext ctx, CardPlay play)
    {
        if(play.Card.Owner==Player)GetInternalData<Data>().Plays.Remove(play);
        return Task.CompletedTask;
    }
    public override async Task AfterDamageGiven(PlayerChoiceContext ctx, Creature? dealer, DamageResult result, ValueProp props, Creature target, CardModel? source)
    {
        if(dealer==Owner && source is FrostmoonCard {Code:"C15"} && !props.HasFlag(ValueProp.Unpowered))await Mark(ctx,target,1,source);
    }
    public override decimal ModifyDamageMultiplicative(Creature? target, decimal amount, ValueProp props, Creature? dealer, CardModel? source)
        => Form==Form.Blood && dealer==Owner && source?.Type==CardType.Attack && !props.HasFlag(ValueProp.Unpowered) ? 2 : 1;
    public override Task AfterCurrentHpChanged(Creature creature,decimal change)
    { if(creature==Owner)Rearm(); return Task.CompletedTask; }
    public override Task BeforeSideTurnStart(PlayerChoiceContext ctx, CombatSide side, IReadOnlyList<Creature> participants,ICombatState state)
    {
        if(side==Owner.Side && participants.Contains(Owner))
        {
            Turn++;IceSkills=MoonAttacks=Switches=Payments=Eclipses=0;IceRefund=false;
            GetInternalData<Data>().Plays.Clear();
        }
        return Task.CompletedTask;
    }
    public override async Task AfterPlayerTurnStartLate(PlayerChoiceContext ctx,Player player)
    {
        if(player!=Player)return;
        RetainedBlock=0;
        AddFrost(Sum("R03",1,1));
        if(EmberTurn==Turn){EmberTurn=-1;await Generate(ctx,"T01");}
    }
    public override async Task BeforeSideTurnEnd(PlayerChoiceContext ctx,CombatSide side,IEnumerable<Creature> participants)
    {
        if(side!=Owner.Side || !participants.Contains(Owner))return;
        if(Frost>=6)await Block(Sum("U24",4,4));
        if(Form==Form.Blood)await Switch(ctx,Form.Ice);
        RetainedBlock=Frost>=4 ? Math.Min(Owner.Block,Sum("R03",8,12)) : 0;
    }
    public override bool ShouldClearBlock(Creature creature) => creature!=Owner || RetainedBlock<=0;
    public override Task AfterPreventingBlockClear(AbstractModel preventer,Creature creature)
    {
        if(preventer==this && creature==Owner && Owner.GetPower<BarricadePower>()==null)
            Owner.LoseBlockInternal(Math.Max(0,Owner.Block-RetainedBlock));
        return Task.CompletedTask;
    }
}
public class MoonMark : CustomPowerModel
{
    public override PowerType Type => PowerType.Debuff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override PowerInstanceType InstanceType => PowerInstanceType.InstancedPerApplier;
    public override string CustomPackedIconPath => "res://Frostmoon/ui/moon.png";
    public override string CustomBigIconPath => CustomPackedIconPath;
    public override List<(string,string)> Localization => new PowerLoc("月痕", "每累计8月痕，消耗8层并触发月蚀：造成4次4点效果伤害。血月使其伤害翻倍。", "每累计8月痕，消耗8层并触发月蚀。");
}
public abstract class FrostmoonAbility : CustomPowerModel
{
    public abstract string Code { get; }
    public override PowerType Type => PowerType.Buff;
    public override PowerStackType StackType => PowerStackType.Counter;
    public override int DisplayAmount => 1;
    public override PowerInstanceType InstanceType => PowerInstanceType.Instanced;
    public override string CustomPackedIconPath => "res://Frostmoon/ui/moon.png";
    public override string CustomBigIconPath => CustomPackedIconPath;
    public override List<(string,string)> Localization => new PowerLoc(CardCatalog.Get(Code).Name,"{Effect}","{Effect}");
    protected override string SmartDescriptionLocKey => "FROSTMOON_NO_SMART_DESCRIPTION";
    public override LocString Description { get { var loc=base.Description;loc.Add("Effect",Amount>1 ? CardCatalog.Get(Code).Up : CardCatalog.Get(Code).Text); return loc; } }
}
