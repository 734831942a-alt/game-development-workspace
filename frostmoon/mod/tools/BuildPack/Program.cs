using StS2PckPacker;
using System.Security.Cryptography;
using System.Text;
// Text-only scenes contain no scripts or editor-imported dependencies.
var entries=new List<PckFileEntry>();
foreach(var file in Directory.GetFiles(args[0],"*",SearchOption.AllDirectories).Order())
{
    var relative=Path.GetRelativePath(args[0],file).Replace('\\','/');
    // Keep superseded and rejected card artwork locally, outside the playable package.
    if(relative.StartsWith("cards/illustrated-") && !relative.StartsWith("cards/illustrated-v4/"))continue;
    var path="Frostmoon/"+relative;
    if(Path.GetExtension(file)==".png")
    {
        var res="res://"+path;
        var hash=Convert.ToHexString(MD5.HashData(Encoding.UTF8.GetBytes(res))).ToLowerInvariant();
        var imported=".godot/imported/"+Path.GetFileName(file)+"-"+hash+".ctex";
        entries.Add(new(imported,CtexConverter.Convert(File.ReadAllBytes(file))));
        entries.Add(new(path+".import",Encoding.UTF8.GetBytes(ImportRemapGenerator.Generate(res,"res://"+imported))));
    }
    else entries.Add(new(path,File.ReadAllBytes(file)));
}
Directory.CreateDirectory(Path.GetDirectoryName(args[1])!);
using var output=File.Create(args[1]);
PckWriter.Write(output,entries);
Console.WriteLine($"Packed {entries.Count} entries -> {args[1]}");
