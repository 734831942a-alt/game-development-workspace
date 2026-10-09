using MegaCrit.Sts2.Core.Models.Powers;
using System.Text.RegularExpressions;
namespace Frostmoon;

public record CardDefinition(string Code,string Name,int Cost,int UpCost,CardType Type,CardRarity Rarity,TargetType Target,string Text,string Up,int Damage,int UpDamage,int Block,int UpBlock,bool Retain,bool Exhaust);
public abstract class FrostmoonCard : CustomCardModel
{
    public abstract string Code { get; }
    CardDefinition Def => CardCatalog.Get(Code);
    public override bool GainsBlock => Def.Block>0 || Code is "C02" or "U12";
    protected override IEnumerable<MegaCrit.Sts2.Core.HoverTips.IHoverTip> ExtraHoverTips =>
        [MegaCrit.Sts2.Core.HoverTips.HoverTipFactory.FromPower<FrostmoonState>(),MegaCrit.Sts2.Core.HoverTips.HoverTipFactory.FromPower<MoonMark>()];
    protected FrostmoonCard(string code) : base(CardCatalog.Get(code).Cost,CardCatalog.Get(code).Type,CardCatalog.Get(code).Rarity,CardCatalog.Get(code).Target, !code.StartsWith("Q")) { }
    public int N(int normal,int upgrade) => IsUpgraded ? upgrade : normal;
    protected override bool HasEnergyCostX => Code=="R06";
    protected override HashSet<CardTag> CanonicalTags => Code=="B01" ? [CardTag.Strike] : Code=="B02" ? [CardTag.Defend] : [];
    protected override IEnumerable<DynamicVar> CanonicalVars => [new DamageVar(Def.Damage,ValueProp.Move),new BlockVar(Def.Block,ValueProp.Move)];
    public override IEnumerable<CardKeyword> CanonicalKeywords
    {
        get { if(Def.Retain)yield return CardKeyword.Retain; if(Def.Exhaust)yield return CardKeyword.Exhaust; }
    }
    public override string CustomPortraitPath => $"res://Frostmoon/cards/illustrated-v4/{PortraitCode}.png";
    string PortraitCode => Code switch
    {
        "QIC" => "B02", "QMO" => "B03",
        "Q00" => "U22", "Q02" => "C01", "Q04" => "U17",
        _ => Code
    };
    public override List<(string,string)> Localization => new CardLoc(Def.Name,"{Effect}",("selectionScreenPrompt","选择一张卡牌。"));
    protected override void AddExtraArgsToDescription(LocString loc)
    {
        string effect=IsUpgraded?Def.Up:Def.Text;
        if(Def.Damage>0)effect=Regex.Replace(effect,@"(?<=造成)\d+(?=点伤害)",DynamicVars.Damage.IntValue.ToString(),RegexOptions.None,TimeSpan.FromMilliseconds(50));
        if(Def.Block>0)effect=Regex.Replace(effect,@"(?<=获得)\d+(?=点格挡)",DynamicVars.Block.IntValue.ToString(),RegexOptions.None,TimeSpan.FromMilliseconds(50));
        loc.Add("Effect",effect);
    }
    protected override void OnUpgrade()
    {
        DynamicVars.Damage.UpgradeValueBy(Def.UpDamage-Def.Damage);
        DynamicVars.Block.UpgradeValueBy(Def.UpBlock-Def.Block);
        if(Def.UpCost!=Def.Cost)EnergyCost.UpgradeBy(Def.UpCost-Def.Cost);
    }
    public int PrimaryPayment(int chosen=0) => Code switch { "C01"=>2,"C12" or "R06"=>3,"U17"=>4,"R08"=>5,"U22"=>chosen,_=>0 };
    protected override bool IsPlayable
    {
        get
        {
            if(Code.StartsWith("Q"))return false;
            if(IsCanonical)return true;
            var s=Owner.Creature.GetPower<FrostmoonState>();
            if(Owner.Creature.CurrentHp<=PrimaryPayment())return false;
            return Code switch { "U08"=>(s?.Frost??0)>=2,"U27"=>(s?.Frost??0)>=1,_=>true };
        }
    }
    public async Task<int> ChoosePayment(PlayerChoiceContext ctx)
    {
        var options=new List<string>{"Q00"};
        if(Owner.Creature.CurrentHp>2)options.Add("Q02");
        if(Owner.Creature.CurrentHp>4)options.Add("Q04");
        var card=await Choose(ctx,options);
        return card?.Code switch {"Q02"=>2,"Q04"=>4,_=>0};
    }
    async Task<FrostmoonCard?> Choose(PlayerChoiceContext ctx,IEnumerable<string> codes)
    {
        var cards=codes.Select(id=>Owner.Creature.CombatState!.CreateCard(CardCatalog.Canonical(id),Owner)).ToList();
        return await CardSelectCmd.FromChooseACardScreen(ctx,cards,Owner) as FrostmoonCard;
    }
    async Task ChooseForm(PlayerChoiceContext ctx,FrostmoonState s)
    { var c=await Choose(ctx,["QIC","QMO"]);await s.Switch(ctx,c?.Code=="QMO" ? Form.Moon : Form.Ice); }
    async Task<int> Attack(PlayerChoiceContext ctx,Creature? target,decimal damage,int hits=1,bool all=false)
    {
        if(!all && (target==null || !target.IsAlive))return 0;
        var attack=DamageCmd.Attack(damage).FromCard(this).WithHitCount(hits).WithHitFx("vfx/vfx_attack_slash");
        if(all)attack.TargetingAllOpponents(Owner.Creature.CombatState!);else attack.Targeting(target!);
        await attack.Execute(ctx);
        return (int)attack.Results.SelectMany(x=>x).Sum(r=>r.UnblockedDamage);
    }
    Task Block(CardPlay play,decimal n) => CreatureCmd.GainBlock(Owner.Creature,n,ValueProp.Move,play);
    async Task SelectCards(PlayerChoiceContext ctx,PileType pile,int count,bool retain=false,bool free=false)
    {
        var cards=await CardSelectCmd.FromCombatPile(ctx,pile.GetPile(Owner),Owner,new CardSelectorPrefs(SelectionScreenPrompt,count),
            c=>!free && Code!="U09" || c.Type==CardType.Attack && (!free || !c.EnergyCost.CostsX));
        foreach(var c in cards)
        {
            if(free)c.SetToFreeThisTurn();
            if(retain)c.GiveSingleTurnRetain();
            await CardPileCmd.Add(c,PileType.Hand);
        }
    }
    protected override async Task OnPlay(PlayerChoiceContext ctx,CardPlay play)
    {
        var s=Owner.Creature.GetPower<FrostmoonState>();
        if(s==null) // Colorless copying and off-character access retain the complete rules.
        { s=await PowerCmd.Apply<FrostmoonState>(ctx,Owner.Creature,1,Owner.Creature,this); if(s==null)return;await s.BeforeCardPlayed(play); }
        var snap=s.Snapshot(play);
        int pay=PrimaryPayment(snap.ChosenPayment);
        if(!await s.Pay(ctx,pay,this))return;
        var t=play.Target;
        var enemies=Owner.Creature.CombatState!.Enemies.Where(e=>e.IsAlive).ToArray();
        decimal d=DynamicVars.Damage.BaseValue,b=DynamicVars.Block.BaseValue;
        if(Type==CardType.Power)
        {
            var power=CardCatalog.Ability(Code).ToMutable();
            await PowerCmd.Apply(ctx,power,Owner.Creature,IsUpgraded?2:1,Owner.Creature,this);
            await s.FinishCard(ctx,play);return;
        }
        switch(Code)
        {
            case "B01": await Attack(ctx,t,d);break;
            case "B02": await Block(play,b);break;
            case "B03": await Attack(ctx,t,d);await s.Mark(ctx,t,2,this);await s.Switch(ctx,Form.Moon);break;
            case "B04": await Block(play,b);await s.Recover(N(2,3));await s.Switch(ctx,Form.Ice);break;
            case "C01": s.AddFrost(2);await Attack(ctx,t,d);break;
            case "C02": await Attack(ctx,t,d,2);if(s.SpendFrost(1)>0)await Block(play,N(3,5));break;
            case "C03": await Block(play,b);s.AddFrost(1);await s.Switch(ctx,Form.Ice);break;
            case "C04": await Block(play,b);await s.Mark(ctx,t,2,this);await s.Switch(ctx,Form.Moon);break;
            case "C05": await s.Mark(ctx,t,N(2,3),this);break;
            case "C06": await Attack(ctx,t,d);await s.Mark(ctx,t,2,this);break;
            case "C07": await Block(play,b);await s.Mark(ctx,t,2,this);break;
            case "C08": await Attack(ctx,t,d+3*s.SpendFrost(2));break;
            case "C09": await Block(play,b);break;
            case "C10": if(t!=null && (s.Marks(t)?.Amount??0)>=6){await s.RemoveMarks(ctx,t,6);await s.Eclipse(ctx,t,this);}else await s.Mark(ctx,t,N(3,4),this);break;
            case "C11": await s.Recover(N(3,4));await s.Draw(ctx,1);await s.Switch(ctx,Form.Ice);break;
            case "C12": s.AddFrost(N(2,3));break;
            case "C13": await s.Draw(ctx,N(2,3));if(snap.Form==Form.Moon)await s.Recover(1);break;
            case "C14": await Block(play,b);await s.Draw(ctx,2);await CardCmd.Discard(ctx,await CardSelectCmd.FromHandForDiscard(ctx,Owner,new CardSelectorPrefs(SelectionScreenPrompt,1),null,this));break;
            case "C15": await Attack(ctx,t,d,2);break; // Per-hit marks are resolved in AfterDamageGiven.
            case "C16": await Attack(ctx,t,d);if(s.Switches>0)await s.Draw(ctx,1);break;
            case "C17": await Attack(ctx,null,d,all:true);foreach(var e in enemies)await s.Mark(ctx,e,1,this);break;
            case "C18": await Block(play,b);foreach(var e in enemies)await s.Mark(ctx,e,1,this);break;
            case "C19": await Block(play,b+4*s.SpendFrost(2));break;
            case "C20": await Attack(ctx,t,d);if(t is {IsAlive:true} && (s.Marks(t)?.Amount??0)>=4)await PowerCmd.Apply<WeakPower>(ctx,t,N(1,2),Owner.Creature,this);break;
            case "U01": s.AddFrost(2);await s.Mark(ctx,t,2,this);await ChooseForm(ctx,s);break;
            case "U05": await Block(play,b+2*s.Frost);break;
            case "U06": await Attack(ctx,t,d);if(s.Frost>=4 && t is {IsAlive:true})await PowerCmd.Apply<WeakPower>(ctx,t,2,Owner.Creature,this);break;
            case "U07": await Attack(ctx,t,d+5*s.SpendFrost(3));break;
            case "U08": if(s.Frost>=2){s.SpendFrost(2);await s.Draw(ctx,N(2,3));}break;
            case "U09": await SelectCards(ctx,PileType.Draw,1);await Block(play,b);break;
            case "U10": await s.Mark(ctx,t,N(5,6),this);await s.Draw(ctx,1);break;
            case "U11": foreach(var e in enemies)await s.Mark(ctx,e,N(2,3),this);await s.Draw(ctx,1);break;
            case "U12": {int n=t==null?0:await s.RemoveMarks(ctx,t,3);await Block(play,N(3,4)*n);if(n==3)await s.Draw(ctx,1);break;}
            case "U13": {int n=t==null?0:await s.RemoveMarks(ctx,t,3);await Attack(ctx,t,d+4*n);break;}
            case "U14": await Attack(ctx,t,d);await s.Mark(ctx,t,2,this);break;
            case "U15":
                if(snap.Form==Form.Ice){await Block(play,b);await s.Mark(ctx,t,2,this);await s.Switch(ctx,Form.Moon);}
                else if(snap.Form==Form.Moon){await s.Recover(N(3,4));s.AddFrost(2);await s.Switch(ctx,Form.Ice);}
                else {await Block(play,b);await s.Recover(N(3,4));}break;
            case "U16": await SelectCards(ctx,PileType.Discard,N(1,2),retain:true);break;
            case "U17": await PlayerCmd.GainEnergy(1,Owner);await s.Draw(ctx,N(1,2));break;
            case "U18": if(Owner.Creature.IsAlive)await CreatureCmd.Heal(Owner.Creature,N(4,6));break;
            case "U19": await Block(play,b);await s.Recover(N(6,8));break;
            case "U21": await Block(play,b);if(s.Payments>0)await s.Draw(ctx,1);break;
            case "U22": await Attack(ctx,t,d+2*snap.ChosenPayment);break;
            case "U25": await s.Draw(ctx,N(3,4));await CardCmd.Discard(ctx,await CardSelectCmd.FromHandForDiscard(ctx,Owner,new CardSelectorPrefs(SelectionScreenPrompt,1),null,this));break;
            case "U26": await Attack(ctx,t,d,2);await s.Mark(ctx,t,3,this);break;
            case "U27": if(s.Frost>=1){s.SpendFrost(1);await Block(play,b);}break;
            case "U28": {await Block(play,b);int n=s.Switches;await ChooseForm(ctx,s);if(s.Switches>n)await s.Draw(ctx,1);break;}
            case "R05": await Attack(ctx,t,d);if(await s.Mark(ctx,t,8,this)>0)await Attack(ctx,t,d);break;
            case "R06": await Attack(ctx,t,d,EnergyCost.CapturedXValue+1);break;
            case "R07": await Block(play,b);await s.Recover(N(8,10));await s.Switch(ctx,Form.Ice);break;
            case "R08": await PlayerCmd.GainEnergy(2,Owner);await s.Draw(ctx,N(2,3));break;
            case "R09": if(Owner.Creature.IsAlive)await CreatureCmd.Heal(Owner.Creature,N(6,9));if(snap.Form==Form.Ice)s.AddFrost(2);break;
            case "R10": await SelectCards(ctx,PileType.Draw,1,free:true);await Block(play,b);break;
            case "R11": {int hp=await Attack(ctx,null,d,all:true);await s.Recover(Math.Min(hp,N(6,8)));await s.Switch(ctx,Form.Ice);break;}
            case "T01": await Block(play,b);await s.Recover(N(3,4));break;
            case "T02": await s.Mark(ctx,t,N(2,3),this);break;
        }
        // Preserve the promised refund on a killing card: the game skips generic after-card hooks at victory.
        await s.FinishCard(ctx,play);
    }
}
