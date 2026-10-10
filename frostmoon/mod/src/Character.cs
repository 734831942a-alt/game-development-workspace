using BaseLib.Utils.NodeFactories;
using MegaCrit.Sts2.Core.Entities.Characters;
using MegaCrit.Sts2.Core.Entities.Relics;
using MegaCrit.Sts2.Core.Nodes.Combat;
namespace Frostmoon;

public class FrostmoonCharacter : PlaceholderCharacterModel
{
    public override Color NameColor => new("a4dcf3");
    public override Color MapDrawingColor => new("a4dcf3");
    public override CharacterGender Gender => CharacterGender.Feminine;
    public override int StartingHp => 72;
    public override CardPoolModel CardPool => ModelDb.CardPool<FrostmoonCardPool>();
    public override RelicPoolModel RelicPool => ModelDb.RelicPool<FrostmoonRelicPool>();
    public override PotionPoolModel PotionPool => ModelDb.PotionPool<FrostmoonPotionPool>();
    public override IEnumerable<CardModel> StartingDeck => PlaytestConfig.StartingDeck is >=1 and <=4 ? CardCatalog.Presets[PlaytestConfig.StartingDeck-1].Select(c=>CardCatalog.Canonical(c.Code)) : Enumerable.Repeat<CardModel>(ModelDb.Card<FmB01>(), 4)
        .Concat(Enumerable.Repeat<CardModel>(ModelDb.Card<FmB02>(), 4)).Append(ModelDb.Card<FmB03>()).Append(ModelDb.Card<FmB04>());
    public override IReadOnlyList<RelicModel> StartingRelics => [ModelDb.Relic<TwinPhasePendant>()];
    public override string CustomCharacterSelectIconPath => "res://Frostmoon/ui/portrait-v3.png";
    public override string CustomCharacterSelectLockedIconPath => CustomCharacterSelectIconPath;
    public override string CustomIconTexturePath => CustomCharacterSelectIconPath;
    public override string CustomIconOutlineTexturePath => CustomCharacterSelectIconPath;
    public override string CustomCharacterSelectBg => "res://Frostmoon/scenes/select.tscn";
    public override string CustomRestSiteAnimPath => "res://Frostmoon/scenes/rest.tscn";
    public override string CustomMerchantAnimPath => "res://Frostmoon/scenes/merchant.tscn";
    public override Control CustomIcon => new TextureRect { Texture = ResourceLoader.Load<Texture2D>(CustomIconTexturePath), ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize, StretchMode = TextureRect.StretchModeEnum.KeepAspectCovered, TextureFilter = CanvasItem.TextureFilterEnum.Linear, CustomMinimumSize = new Vector2(64,64), Size = new Vector2(64,64) };
    public override NCreatureVisuals? CreateCustomVisuals()
    {
        var v = NodeFactory<NCreatureVisuals>.CreateFromResource(ResourceLoader.Load<Texture2D>("res://Frostmoon/character.png"));
        // Scale the artwork, not the visual root: vanilla sizes hitboxes from Bounds in local units.
        var sprite=v.GetNode<Sprite2D>("Visuals");sprite.Scale=new Vector2(.21f,.21f);sprite.Position=new Vector2(0,-161);
        var bounds=v.GetNode<Control>("Bounds");bounds.Position=new Vector2(-110,-295);bounds.Size=new Vector2(220,295);
        v.GetNode<Marker2D>("IntentPos").Position=new Vector2(0,-370);
        v.GetNode<Marker2D>("CenterPos").Position=new Vector2(0,-140);
        var label=new Label { Name="FrostmoonReadout",Position=new Vector2(-155,-340),Size=new Vector2(310,26),HorizontalAlignment=HorizontalAlignment.Center,MouseFilter=Control.MouseFilterEnum.Ignore };
        label.AddThemeFontSizeOverride("font_size",16);label.AddThemeColorOverride("font_shadow_color",Colors.Black);label.AddThemeConstantOverride("shadow_offset_x",2);label.AddThemeConstantOverride("shadow_offset_y",2);v.AddChild(label);
        var tree=(SceneTree)Engine.GetMainLoop();
        void Update()
        {
            if(!GodotObject.IsInstanceValid(v) || !v.IsInsideTree())return;
            var state=v.GetParentOrNull<NCreature>()?.Entity.GetPower<FrostmoonState>();
            if(state==null)return;
            var color=state.Form==Form.Blood ? new Color("ff8794") : state.Form==Form.Moon ? new Color("eee7ff") : new Color("a4e3ff");
            label.Modulate=color;sprite.Modulate=state.Form==Form.Blood ? new Color(1,.7f,.76f) : Colors.White;
            label.Text=state.CompactReadout;
        }
        v.TreeEntered+=()=>tree.ProcessFrame+=Update;v.TreeExiting+=()=>tree.ProcessFrame-=Update;
        var animator=new AnimationPlayer {Name="AnimationPlayer"};v.AddChild(animator);var library=new AnimationLibrary();
        foreach(var name in new[]{"Idle","Attack","Cast","Hit","Dead"})
        {
            var animation=new Animation {Length=name=="Idle" ? 2f : .3f,LoopMode=name=="Idle" ? Animation.LoopModeEnum.Linear : Animation.LoopModeEnum.None};
            int track=animation.AddTrack(Animation.TrackType.Value);animation.TrackSetPath(track,new NodePath("Visuals:position"));
            animation.TrackInsertKey(track,0,new Vector2(0,-161));
            animation.TrackInsertKey(track,animation.Length/2,new Vector2(name=="Attack"?36:name=="Hit"?-12:0,-161+(name=="Idle"?-3:name=="Dead"?40:0)));
            animation.TrackInsertKey(track,animation.Length,new Vector2(0,-161));library.AddAnimation(name,animation);
        }
        animator.AddAnimationLibrary("",library);animator.Autoplay="Idle";animator.AnimationFinished+=name=>{if(name!="Dead")animator.Play("Idle");};
        return v;
    }
    public override List<(string, string)> Localization => new CharacterLoc("小木曾和纱", "小木曾和纱",
        "以霜护身，以月刻敌。\n在冰与月之间往复，将付出的生命收回。\n生命不高于40%时，血月照临一回合。",
        "她", "她", "她的", "她的", "冷月与初雪。", "月还未落。", "……", "尚有余烬。", "留作旅费。", "小木曾和纱的卡牌", "将小木曾和纱的卡牌加入奖励与商店。");
}
public class FrostmoonCardPool : CustomCardPoolModel
{
    public override bool IsShared => false;
    public override bool IsColorless => false;
    public override Color ShaderColor => new(.5f,.83f,1f);
    public override Color DeckEntryCardColor => new(.3f,.55f,.7f);
    public override string BigEnergyIconPath => "res://Frostmoon/ui/energy.png";
    public override string TextEnergyIconPath => "res://Frostmoon/ui/energy_text.png";
    public override string Title => "FROSTMOON-FROSTMOON_CHARACTER";
    public override bool SeenByDefault => true;
}
public class FrostmoonRelicPool : CustomRelicPoolModel { public override bool IsShared => false; }
public class FrostmoonPotionPool : CustomPotionPoolModel { public override bool IsShared => false; }
[Pool(typeof(FrostmoonRelicPool))]
public class TwinPhasePendant : CustomRelicModel
{
    public override RelicRarity Rarity => RelicRarity.Starter;
    public override string PackedIconPath => "res://Frostmoon/ui/pendant.png";
    protected override string BigIconPath => PackedIconPath;
    protected override string PackedIconOutlinePath => PackedIconPath;
    public override List<(string,string)> Localization => new RelicLoc("双相佩", "战斗开始时获得2霜。每回合首次主动在冰与月之间切换时，获得3点格挡。", "两面相照，同一轮月。");
}
