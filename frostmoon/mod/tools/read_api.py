from pathlib import Path
import subprocess,os,concurrent.futures
root=Path(__file__).resolve().parents[1]
game=Path('/Users/ayanami/Library/Application Support/Steam/steamapps/common/Slay the Spire 2/SlayTheSpire2.app/Contents/Resources/data_sts2_macos_arm64/sts2.dll')
env=os.environ|{'DOTNET_ROOT':str(root/'tools/dotnet'),'DOTNET_ROLL_FORWARD':'LatestMajor'}
types=['Models.CardModel','Models.PowerModel','Models.CharacterModel','Models.RelicModel','Entities.Players.Player','Entities.Creatures.Creature','Entities.Cards.CardPlay','Entities.Cards.CardPile','Entities.Cards.CardEnergyCost','Commands.CardPileCmd','Commands.CardSelectCmd','Commands.CardCmd','Commands.CreatureCmd','Commands.PlayerCmd','Commands.PowerCmd','Commands.DamageCmd','Commands.Builders.AttackCommand','Combat.CombatManager','Combat.CombatState','Models.Powers.BarricadePower','Models.Powers.RupturePower','Models.Cards.Offering','Models.Cards.Headbutt','Nodes.Combat.NCreatureVisuals','Nodes.NGame','Modding.ModManager','Entities.Cards.CardSelectorPrefs','HoverTips.GenericHoverTip','Models.ModelDb']
def run(t):
 dest=root/'references/api'/f'{t.rsplit(".",1)[-1]}.cs'
 p=subprocess.run([str(root/'tools/ilspy/ilspycmd'),'-t','MegaCrit.Sts2.Core.'+t,str(game)],env=env,text=True,capture_output=True)
 if p.returncode==0:dest.write_text(p.stdout)
 return t,p.returncode,p.stderr[:150]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for result in ex.map(run,types):print(result)
