"""Build the final Word and PDF documents with two embedded figures."""
from pathlib import Path
import os,json,html,zipfile,tempfile
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'discourse_selection_matplotlib'))
HEADINGS={'Problem','Model','Data','Results'}
SOURCES=[
    ('Kirchner (2022), Via productiva','https://universalprior.substack.com/p/via-productiva'),
    ('Research notes and source audit','https://chatgpt.com/space/page_9ba53381ab408191ad16727d728aaa07'),
]

def docx(paragraphs,stem,images):
    from PIL import Image
    W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    A='http://schemas.openxmlformats.org/drawingml/2006/main'
    R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    def para(s,bold=False,caption=False):
        italic=s.startswith('*') and s.endswith('*')
        if italic:s=s[1:-1]
        size=32 if s==paragraphs[0] else (20 if caption else 21)
        heading=s in HEADINGS or s==paragraphs[0]
        pr='<w:spacing w:before="0" w:after="75" w:line="240" w:lineRule="auto"/>'
        if heading:pr+='<w:keepNext/>'
        if caption:pr='<w:spacing w:before="20" w:after="80" w:line="230" w:lineRule="auto"/>'
        run=f'<w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="{size}"/>'
        if bold or heading:run+='<w:b/>'
        if italic or caption:run+='<w:i/>'
        if caption:run+='<w:color w:val="516779"/>'
        run+='</w:rPr>'
        return f'<w:p><w:pPr>{pr}</w:pPr><w:r>{run}<w:t xml:space="preserve">{html.escape(s)}</w:t></w:r></w:p>'
    # PNG bytes are embedded inside the DOCX ZIP; no local-path dependency.
    def drawing(path,index):
        width,height=Image.open(path).size
        cx=int(6.85*914400);cy=int(cx*height/width)
        return f'''<w:p><w:pPr><w:spacing w:before="40" w:after="0"/><w:keepNext/></w:pPr><w:r><w:drawing>
    <wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" distT="0" distB="0" distL="0" distR="0">
    <wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{index}" name="Figure {index}" descr="{html.escape(path.stem)}"/>
    <a:graphic xmlns:a="{A}"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">
    <pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="0" name="{path.name}"/><pic:cNvPicPr/></pic:nvPicPr>
    <pic:blipFill><a:blip r:embed="rIdImage{index}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>
    <pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>
    </pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'''
    body=[]
    for s in paragraphs:
        if s in images:body.append(drawing(images[s],list(images).index(s)+1))
        elif s=='[PAGE_BREAK]':body.append('<w:p><w:pPr><w:spacing w:before="0" w:after="0"/></w:pPr><w:r><w:br w:type="page"/></w:r></w:p>')
        else:body.append(para(s,caption=s.startswith('Figure ')))
    for i,(label,url) in enumerate(SOURCES,1):
        body.append(f'<w:p><w:pPr><w:spacing w:before="80" w:after="0"/></w:pPr><w:hyperlink r:id="rIdSource{i}"><w:r><w:rPr><w:color w:val="245B80"/><w:u w:val="single"/><w:sz w:val="20"/></w:rPr><w:t>{html.escape(label)}</w:t></w:r></w:hyperlink></w:p>')
    sect='<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="850" w:right="1000" w:bottom="850" w:left="1000" w:header="300" w:footer="300"/></w:sectPr>'
    document=f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="{W}" xmlns:r="{R}"><w:body>{"".join(body)}{sect}</w:body></w:document>'
    types='<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>'
    rels=f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="{R}/officeDocument" Target="word/document.xml"/></Relationships>'
    image_rels=''.join(f'<Relationship Id="rIdImage{i}" Type="{R}/image" Target="media/{path.name}"/>' for i,path in enumerate(images.values(),1))
    source_rels=''.join(f'<Relationship Id="rIdSource{i}" Type="{R}/hyperlink" Target="{html.escape(url,quote=True)}" TargetMode="External"/>' for i,(label,url) in enumerate(SOURCES,1))
    docrels=f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{image_rels}{source_rels}</Relationships>'
    out=ROOT/f'{stem}.docx'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml',types);z.writestr('_rels/.rels',rels)
        z.writestr('word/document.xml',document);z.writestr('word/_rels/document.xml.rels',docrels)
        for path in images.values():z.write(path,'word/media/'+path.name)
    with zipfile.ZipFile(out) as z:
        for n in z.namelist():
            if n.endswith(('.xml','.rels')):ET.fromstring(z.read(n))
        for path in images.values():assert z.read('word/media/'+path.name)==path.read_bytes()

def pdf(paragraphs,stem,images):
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.font_manager import FontProperties
    from PIL import Image
    W,H=8.2677,11.6929
    fig=None;pages=0;bottoms=[]
    with PdfPages(ROOT/f'{stem}.pdf') as output:
        def new_page():
            f=plt.figure(figsize=(W,H),dpi=150)
            c=FigureCanvasAgg(f);c.draw()
            return f,c.get_renderer(),H-.64
        def save(f,num,y):
            assert y>.55,f'Page {num} overflow: y={y}'
            f.text(.7/W,.35/H,str(num),fontsize=8,color='#516779')
            output.savefig(f)
            preview_dir=os.environ.get('DISCOURSE_PREVIEW_DIR')
            if preview_dir:
                preview=Path(preview_dir);preview.mkdir(parents=True,exist_ok=True)
                f.savefig(preview/f'page_{num}.png',dpi=150)
            plt.close(f)
        fig,renderer,y=new_page();pages=1
        for s in paragraphs:
            if s=='[PAGE_BREAK]':
                bottoms.append(round(y,2));save(fig,pages,y)
                fig,renderer,y=new_page();pages+=1;continue
            if s in images:
                im=Image.open(images[s]);width,height=im.size;h=6.85*height/width
                ax=fig.add_axes([.7/W,(y-h)/H,6.85/W,h/H]);ax.imshow(im);ax.axis('off')
                y-=h+.05;continue
            title=s==paragraphs[0];heading=s in HEADINGS;caption=s.startswith('Figure ')
            italic=s.startswith('*') and s.endswith('*')
            if italic:s=s[1:-1]
            size=15.5 if title else (10 if caption else 10.5)
            font=FontProperties(family='DejaVu Sans',size=size,weight='bold' if title or heading else 'normal',style='italic' if italic else 'normal')
            lines=[];line=''
            for word in s.split():
                trial=(line+' '+word).strip()
                if renderer.get_text_width_height_descent(trial,font,False)[0]>6.85*150 and line:
                    lines.append(line);line=word
                else:line=trial
            if line:lines.append(line)
            for line in lines:
                fig.text(.7/W,y/H,line,fontproperties=font,va='top',color='#516779' if caption else '#182534')
                y-=(19 if title else (12.5 if caption else 13))/72
            y-=4/72
        for label,url in SOURCES:
            fig.text(.7/W,y/H,label,fontsize=9,color='#245b80',url=url,va='top');y-=.23
        bottoms.append(round(y,2));save(fig,pages,y)
    return pages,bottoms

if __name__=='__main__':
    paragraphs=(ROOT/'source'/'document.txt').read_text().strip().split('\n\n')
    images={'[FIGURE]':ROOT/'figures'/'fitted_process.png','[FIT_FIGURE]':ROOT/'figures'/'participation_fit.png'}
    stem='Participation_Model_Fitted'
    docx(paragraphs,stem,images)
    pages,bottoms=pdf(paragraphs,stem,images)
    print(json.dumps({'words_excluding_image_labels':len(' '.join(s for s in paragraphs if not s.startswith('[')).split()),'pages':pages,'bottom_space_inches':bottoms,'embedded_images':len(images)},indent=2))
