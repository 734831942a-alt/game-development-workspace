from pathlib import Path
import json
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

root=Path(__file__).resolve().parents[1]
data=json.loads((root/'v02/rules.json').read_text())
output=root.parent/'outputs/01a1009b-46b5-7492-aa6a-c58b009ff7e0/霜月三形态设计说明v0.2.docx'
doc=Document();sec=doc.sections[0]
sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=Inches(.65);sec.bottom_margin=Inches(.65)
sec.left_margin=Inches(.75);sec.right_margin=Inches(.75)
sec.footer_distance=Inches(.28)
def font_style(style,size,bold=False):
 style.font.name='Arial';style.font.size=Pt(size);style.font.bold=bold;style.font.color.rgb=RGBColor(0,0,0)
 r=style.element.get_or_add_rPr();rf=r.find(qn('w:rFonts'))
 if rf is None:rf=OxmlElement('w:rFonts');r.append(rf)
 for attr in list(rf.attrib):
  if attr.endswith('Theme'):del rf.attrib[attr]
 rf.set(qn('w:eastAsia'),'Heiti SC');rf.set(qn('w:ascii'),'Arial');rf.set(qn('w:hAnsi'),'Arial')
for name,size,bold in [('Normal',11,False),('Title',22,True),('Subtitle',11,False),('Heading 1',16,True),('Heading 2',12,True)]:
 font_style(doc.styles[name],size,bold)
for style in doc.styles:
 for border in list(style.element.iter(qn('w:pBdr'))):border.getparent().remove(border)
doc.styles['Normal'].paragraph_format.line_spacing=1.16
doc.styles['Normal'].paragraph_format.space_after=Pt(7)
for name in ['Heading 1','Heading 2']:
 doc.styles[name].paragraph_format.keep_with_next=True
 doc.styles[name].paragraph_format.space_before=Pt(10)
 doc.styles[name].paragraph_format.space_after=Pt(6)
doc.styles['Title'].paragraph_format.space_after=Pt(8)
doc.styles['Subtitle'].paragraph_format.space_after=Pt(10)
doc.core_properties.title='霜月三形态角色设计'
doc.core_properties.subject='64张卡池与冰月血月规则审阅稿'
doc.core_properties.author='Codex'

footer=sec.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
r=footer.add_run('霜月 v0.2  ·  ');r.font.size=Pt(9)
fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');footer._p.append(fld)

def add_link(p,label,url):
 link=OxmlElement('w:hyperlink');link.set(qn('r:id'),p.part.relate_to(url,RT.HYPERLINK,is_external=True))
 r=OxmlElement('w:r');pr=OxmlElement('w:rPr');rf=OxmlElement('w:rFonts');rf.set(qn('w:eastAsia'),'Heiti SC');rf.set(qn('w:ascii'),'Arial');pr.append(rf)
 color=OxmlElement('w:color');color.set(qn('w:val'),'24527D');pr.append(color)
 text=OxmlElement('w:t');text.text=label;r.append(pr);r.append(text);link.append(r);p._p.append(link)

def table(block):
 widths=block.get('widths') or [6.5/len(block['headers'])]*len(block['headers'])
 tb=doc.add_table(rows=1,cols=len(widths));tb.alignment=WD_TABLE_ALIGNMENT.LEFT;tb.autofit=False
 pr=tb._tbl.tblPr
 borders=OxmlElement('w:tblBorders')
 for side in ['top','left','bottom','right','insideH','insideV']:
  x=OxmlElement('w:'+side);x.set(qn('w:val'),'single');x.set(qn('w:sz'),'4');x.set(qn('w:color'),'D9D9D9');borders.append(x)
 pr.append(borders)
 mar=OxmlElement('w:tblCellMar')
 for side,val in [('top','90'),('bottom','90'),('left','100'),('right','100')]:
  x=OxmlElement('w:'+side);x.set(qn('w:w'),val);x.set(qn('w:type'),'dxa');mar.append(x)
 pr.append(mar)
 for i,w in enumerate(widths):tb.columns[i].width=Inches(w)
 head=tb.rows[0]
 repeat=OxmlElement('w:tblHeader');head._tr.get_or_add_trPr().append(repeat)
 rows=[block['headers'],*block['rows']]
 for j,values in enumerate(rows):
  row=head if j==0 else tb.add_row()
  cant=OxmlElement('w:cantSplit');row._tr.get_or_add_trPr().append(cant)
  for i,value in enumerate(values):
   c=row.cells[i];c.width=Inches(widths[i]);c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   c.text=str(value);sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'29334D' if j==0 else 'F4F6F9' if j%2==0 else 'FFFFFF');c._tc.get_or_add_tcPr().append(sh)
   for p in c.paragraphs:
    p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.1
    p.alignment=WD_ALIGN_PARAGRAPH.CENTER if j==0 or widths[i]<.75 else WD_ALIGN_PARAGRAPH.LEFT
    for r in p.runs:
     r.font.name='Arial';r.font.size=Pt(10);r.font.bold=j==0;r.font.color.rgb=RGBColor(255,255,255) if j==0 else RGBColor(0,0,0)
     r._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Heiti SC')
 # Separate the following text without adding a conspicuous blank paragraph.
 p=doc.add_paragraph();p.paragraph_format.space_after=Pt(0);p.paragraph_format.space_before=Pt(0);p.paragraph_format.line_spacing=1;p.add_run().font.size=Pt(3)

for i,page in enumerate(data['pages']):
 if i:doc.add_page_break()
 else:
  doc.add_paragraph('霜月三形态角色设计',style='Title')
  doc.add_paragraph('规则与卡池审阅稿  v0.2  2026年10月6日',style='Subtitle')
 doc.add_paragraph(f'{i+1} {page["title"]}',style='Heading 1')
 for block in page['blocks']:
  if block['type']=='p':doc.add_paragraph(block['text'])
  elif block['type']=='h':doc.add_paragraph(block['text'],style='Heading 2')
  elif block['type']=='table':table(block)
  elif block['type']=='sources':
   for s in block['items']:
    p=doc.add_paragraph();p.paragraph_format.space_after=Pt(5);add_link(p,s[0],s[1]);p.add_run('。'+s[2])
doc.save(output)
print(output)
