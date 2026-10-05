import json, re, html, collections
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether, Flowable, CondPageBreak
from reportlab.platypus.tableofcontents import TableOfContents

BASE=Path(__file__).resolve().parent.parent
W=Path(__file__).resolve().parent
QA_WORK=BASE/'work'
QA_WORK.mkdir(exist_ok=True)
O=BASE/'outputs'/'排序算法学习包'
O.mkdir(exist_ok=True)
pdfmetrics.registerFont(TTFont('Universal','/Library/Fonts/Arial Unicode.ttf'))
pdfmetrics.registerFont(TTFont('English','/Library/Fonts/Artifakt Element Regular.ttf'))
pdfmetrics.registerFont(TTFont('EnglishBold','/Library/Fonts/Artifakt Element Bold.ttf'))
pdfmetrics.registerFont(TTFont('LatinSymbols','/System/Library/Fonts/Supplemental/Arial.ttf'))
pdfmetrics.registerFontFamily('Universal',normal='Universal',bold='Universal',italic='Universal',boldItalic='Universal')
pdfmetrics.registerFontFamily('English',normal='English',bold='EnglishBold',italic='English',boldItalic='EnglishBold')

data=[]
for fname in ['part_a.json','part_b.json','part_c.json','part_d.json']:
    data.extend(json.loads((W/fname).read_text()))
byid={d['id']:d for d in data}
assert len(data)==80 and sorted(byid)==list(range(1,81)), (len(data),sorted(byid))
orders={
 'A':[1,2,3,4,78,5,6,7,8,9,10,40],
 'B':[15,16,17,18,11,12,13,19,20,14,21],
 'C':[22,23,33,34,35,30,31,37,79,25,26,27,28,29,32,36,38,39,67,77],
 'E':[54,55,56,57,58,59,60,61,62,63,64,80,65,66],
 'D':[46,75,48,49,41,42,47,43,44,45,50,24,51,76,52,53],
 'F':[68,69,70,71,72,73,74]
}
ordered=[]
for g,ids in orders.items():
    for i in ids:
        d=byid[i];d['group']=g;d['seq']=len(ordered)+1;ordered.append(d)
assert len({d['id'] for d in ordered})==80

groups={
'zh':{
 'A':('一 键结构与分布条件下的方法','先看小整数键域与固定位数可达到的近线性层，再看依赖分布或前缀的桶与字符串方法。同层并列；输入键域、字符总量、桶均衡度改变次序。二进制快速排序是 MSD 的变体，字符串三向快排使用字符比较，不能对任意长文本宣称 O(n)。'),
 'B':('二 利用已有顺序的自适应方法','在少数长有序段条件下先看自适应归并；在少逆序条件下看插入。它们依据不同“近有序”指标，不互相给固定名次。随后看附带空间或随机条件的方法，以及仍可退化为平方工作的提取方法。最坏保障与自适应能力分别说明。'),
 'C':('三 通用比较排序与条件优化','一般大数组中，先讲保证或总体摊还 O(n log n) 的层；随后讲枢轴、输入结构等条件下高效但可能退化的方法。Shellsort 的界依增量而变。缓存、比较次数及大记录移动的优化单列于本组后部，度量不同，不按实际秒数强行排序。'),
 'E':('四 外存并行与受限输入的方法','本组不能与单核内存算法混排：外存按块读写轮次，CPU/GPU 按总工作与等待链，网络按比较器数与层数。先外存，后并行，再固定网络和特殊输入；这些是不同模型的分组，不是跨机器快慢名次。置换选择仅负责生成有序段。'),
 'D':('五 工作较多或操作受限的方法','先看梳与 Circle 等步幅或整遍方法，其总体界需按版本判断；然后是通常平方级的比较/移动层，最后是高次与超多项式递归。Cycle 可少写但比较仍多；Pancake 按整段翻转计费。平方层内以原理依赖安排，不能宣称每项必比后一项快。'),
 'F':('六 特殊模型与趣味方法','珠子、面条与计时器依赖额外模型，速度不能按普通比较排序衡量。后面的排列枚举、随机打乱和递归重试在常规机器上通常非常慢。趣味名称不改变保留元素和正确输出的要求；明确区分有限穷举与无有限最坏界的随机方法。')
},
'en':{
 'A':('1 Methods using key structure and distribution','Begin with the near-linear tier for small integer domains and fixed-width keys, then examine distribution- and prefix-dependent methods. Methods within a tier are peers. Key range, total character count, and bucket balance change the order. Binary quicksort is an MSD variant; multikey quicksort compares characters and is not automatically linear for arbitrary long text.'),
 'B':('2 Methods that use existing order','Start with adaptive merging under a few-long-runs condition, then insertion under a few-inversions condition. These are different measures of existing order and do not create a fixed rank against one another. Later entries use space or randomness assumptions, or extraction strategies that may still do quadratic work. Worst-case protection and adaptivity are separate properties.'),
 'C':('3 General comparison sorts and conditional optimizations','For large arbitrary arrays, guaranteed or aggregate-amortized n log n methods precede methods whose efficiency relies on pivots or input structure. Shellsort bounds depend on its gaps. Cache behavior, comparison counts, and large-record movement receive separate treatment toward the end; these measures do not imply a measured timing rank.'),
 'E':('4 External parallel and restricted-input methods','These models cannot share one timing list with serial in-memory sorting. Count block-transfer passes for external data, total work and dependency chains for CPU/GPU tasks, and comparators and layers for networks. External, parallel, network, and restricted-input entries are separate model groups. Replacement selection generates runs rather than completing the sort.'),
 'D':('5 Higher-work and restricted-operation methods','Gap and full-pass methods appear first, with version-dependent total bounds. The quadratic comparison or movement tier follows, then high-degree and superpolynomial recursion. Cycle sort can reduce writes while retaining many comparisons. Pancake sorting charges for whole-prefix reversals. Order inside a tier follows learning dependencies rather than universal speed.'),
 'F':('6 Special models and playful methods','Beads, rods, and timers rely on models outside ordinary comparison sorting. Permutation enumeration, random shuffling, and recursive retries usually become very slow on ordinary computers. Names do not relax correctness or record-preservation requirements. Finite exhaustive searches are distinguished from random methods with no finite worst-case bound.')
}}
kindnames={
'zh':{'algorithm':'算法','variant':'重要变体','family':'算法家族','phase':'辅助阶段','technique':'辅助技术','physical':'物理模型','joke':'趣味方法'},
'en':{'algorithm':'Algorithm','variant':'Important variant','family':'Algorithm family','phase':'Supporting phase','technique':'Supporting technique','physical':'Physical model','joke':'Playful method'}}

refs=[]; refids={}
for d in ordered:
    assert d.get('sources'),d['id']
    d['refnos']=[]
    for s in d['sources']:
        u=s['url'].strip()
        if u not in refids:
            refids[u]=len(refs)+1;refs.append({'num':len(refs)+1,**s})
        d['refnos'].append(refids[u])

front=json.loads((W/'front_matter.json').read_text())
WIDTH,HEIGHT=A4
M=48
CW=WIDTH-2*M
BOTTOM=42
TOP=46

def safe(t):
    # Cover every printed character; the body face lacks some math glyphs.
    families={n:pdfmetrics.getFont(n).face.charToGlyph for n in ['English','Universal','LatinSymbols']}
    pieces=[];pending='';current=None
    for ch in str(t):
        cp=ord(ch)
        if ch=='\n':
            if pending:
                escaped=html.escape(pending)
                pieces.append(escaped if current is None else f'<font name="{current}">{escaped}</font>')
                pending=''
            pieces.append('<br/>');current=None;continue
        if cp in families['English'] and cp in families['Universal']:target=None
        elif cp in families['Universal']:target='Universal'
        elif cp in families['LatinSymbols']:target='LatinSymbols'
        else:raise ValueError(f'No font covers {ch!r} U+{cp:04X}')
        if pending and target!=current:
            escaped=html.escape(pending)
            pieces.append(escaped if current is None else f'<font name="{current}">{escaped}</font>')
            pending=''
        current=target;pending+=ch
    if pending:
        escaped=html.escape(pending)
        pieces.append(escaped if current is None else f'<font name="{current}">{escaped}</font>')
    return ''.join(pieces)

class StateDiagram(Flowable):
    def __init__(self,rows,lang):
        super().__init__();self.rows=rows;self.lang=lang;self.width=CW;self.height=33+len(rows)*57
    def wrap(self,aw,ah):return self.width,self.height
    def draw(self):
        c=self.canv
        c.setStrokeColor(colors.HexColor('#D9E0E6'));c.setFillColor(colors.HexColor('#FAFCFD'))
        c.roundRect(0,0,CW,self.height,5,fill=1,stroke=1)
        f='Universal' if self.lang=='zh' else 'English'
        c.setFont(f,9);c.setFillColor(colors.black)
        label='步骤状态图  C 比较  M 移动  S 已有序' if self.lang=='zh' else 'State trace   C compare   M move   S ordered'
        c.drawString(10,self.height-17,label)
        for rowno,row in enumerate(self.rows):
            y=self.height-36-rowno*57
            label=row.get(self.lang,'')
            c.setFont(f,8.5);c.setFillColor(colors.HexColor('#344454'))
            # Row labels are explanatory but should never squeeze the number cells.
            if pdfmetrics.stringWidth(label,f,8.5)>CW-24:
                words=list(label) if self.lang=='zh' else label.split(' ')
                first='';remain=''
                for j,w in enumerate(words):
                    sep='' if self.lang=='zh' else ' '
                    test=first+sep+w
                    if pdfmetrics.stringWidth(test,f,8.5)>CW-24:
                        remain=sep.join(words[j:]);break
                    first=test
                c.drawString(10,y,first.strip());c.drawString(10,y-9,remain);cy=y-37
            else:
                c.drawString(10,y,label);cy=y-31
            vals=row['values'];n=len(vals)
            cell=min(43,(CW-26)/max(n,1));gap=4
            actual=cell-gap
            for j,v in enumerate(vals):
                x=12+j*cell
                tag='';fill=colors.white;stroke=colors.HexColor('#B9C4CE')
                if j in row.get('fixed',[]):fill=colors.HexColor('#E4F3E7');tag='S'
                if j in row.get('moved',[]):fill=colors.HexColor('#E2EDF9');tag='M'
                if j in row.get('active',[]):stroke=colors.HexColor('#BA6500');tag='C' if not tag else tag+' C'
                c.setFillColor(fill);c.setStrokeColor(stroke);c.setLineWidth(1.1)
                c.roundRect(x,cy,actual,24,3,fill=1,stroke=1)
                text=str(v);sz=min(11, max(6.5, (actual-5)/max(len(text)*0.55,1)))
                c.setFont('Universal',sz);c.setFillColor(colors.black)
                c.drawCentredString(x+actual/2,cy+8,text)
                if tag:
                    c.setFont('English',6.4);c.setFillColor(colors.HexColor('#344454'))
                    c.drawCentredString(x+actual/2,cy-7,tag)

class TreeDiagram(Flowable):
    def __init__(self,frames,lang,title):
        super().__init__();self.frames=frames;self.lang=lang;self.title=title;self.width=CW;self.height=183
    def wrap(self,aw,ah):return self.width,self.height
    def draw(self):
        c=self.canv;f='Universal' if self.lang=='zh' else 'English'
        c.setFillColor(colors.HexColor('#FAFCFD'));c.setStrokeColor(colors.HexColor('#D9E0E6'))
        c.roundRect(0,0,CW,self.height,5,fill=1,stroke=1)
        c.setFillColor(colors.black);c.setFont(f,9);c.drawString(10,self.height-17,self.title[self.lang])
        fw=CW/len(self.frames)
        for j,fr in enumerate(self.frames):
            ox=j*fw
            c.setFont(f,8.5);c.setFillColor(colors.HexColor('#344454'))
            labels=fr[self.lang]
            for k,line in enumerate(labels):c.drawCentredString(ox+fw/2,self.height-34-k*11,line)
            nodes=fr['nodes']
            pos={key:(ox+12+x*(fw-24),16+y*99) for key,val,x,y,tag in nodes}
            c.setStrokeColor(colors.HexColor('#8898A7'));c.setLineWidth(1)
            for a,b in fr['edges']:
                ax,ay=pos[a];bx,by=pos[b];c.line(ax,ay,bx,by)
            for key,val,x,y,tag in nodes:
                px,py=pos[key]
                fill=colors.HexColor('#E2EDF9') if tag=='M' else colors.HexColor('#E4F3E7') if tag=='S' else colors.white
                stroke=colors.HexColor('#BA6500') if tag=='C' else colors.HexColor('#8193A3')
                c.setFillColor(fill);c.setStrokeColor(stroke);c.circle(px,py,12,fill=1,stroke=1)
                c.setFillColor(colors.black);c.setFont('Universal',10.5);c.drawCentredString(px,py-3.7,str(val))
                if tag:
                    c.setFont('English',6.8);c.drawCentredString(px+16,py-2,tag)

tree_specs={
 21:([
   dict(zh=['树构建完成','最初候选仅为根 1'],en=['Tree after construction','Only root 1 is initially eligible'],nodes=[('a',1,.5,1,'C'),('b',3,.2,.55,''),('c',2,.8,.55,''),('d',4,.65,.08,'')],edges=[('a','b'),('a','c'),('c','d')]),
   dict(zh=['输出 1 后','2 与 3 成为下一候选'],en=['After emitting 1','2 and 3 become candidates'],nodes=[('a',1,.5,1,'S'),('b',3,.2,.55,'C'),('c',2,.8,.55,'C'),('d',4,.65,.08,'')],edges=[('a','b'),('a','c'),('c','d')])
 ],dict(zh='笛卡尔树与候选前沿 同一示例 [3,1,4,2]',en='Cartesian tree and eligible frontier for [3,1,4,2]')),
 33:([
   dict(zh=['建堆后比较根与孩子','数组为 [4,2,3,1]'],en=['Compare root and children','Array is [4,2,3,1]'],nodes=[('a',4,.5,1,'C'),('b',2,.2,.55,'C'),('c',3,.8,.55,'C'),('d',1,.08,.08,'')],edges=[('a','b'),('a','c'),('b','d')]),
   dict(zh=['取出 4 后修复剩余堆','堆 [3,2,1]  输出后缀 [4]'],en=['Heap after removing 4','Heap [3,2,1]; output suffix [4]'],nodes=[('a',3,.5,1,'M'),('b',2,.2,.55,''),('c',1,.8,.55,'M')],edges=[('a','b'),('a','c')])
 ],dict(zh='堆的树形关系 节点只是同一数组的另一种画法',en='Heap relationships: nodes show the same array, not additional records')),
 37:([
   dict(zh=['插入 3 后','右左形状'],en=['After inserting 3','Right-left shape'],nodes=[('a',1,.22,1,''),('b',4,.67,.52,'C'),('c',3,.48,.08,'C')],edges=[('a','b'),('b','c')]),
   dict(zh=['在 4 处右旋','3 成为 1 的右孩子'],en=['Rotate right at 4','3 becomes the right child of 1'],nodes=[('a',1,.2,1,''),('b',3,.53,.52,'M'),('c',4,.82,.08,'M')],edges=[('a','b'),('b','c')]),
   dict(zh=['再在 1 处左旋','3 升到根'],en=['Then rotate left at 1','3 reaches the root'],nodes=[('a',3,.5,1,'M'),('b',1,.17,.45,'M'),('c',4,.83,.45,'')],edges=[('a','b'),('a','c')])
 ],dict(zh='伸展树的两次旋转 对应插入 3 的文字步骤',en='Two splay rotations for the example insertion of 3'))
}

class ManualDoc(BaseDocTemplate):
    def __init__(self,path,lang,**kwargs):
        super().__init__(str(path),**kwargs);self.lang=lang;self.pages={};self.meta=[]
        self.addPageTemplates(PageTemplate(id='normal',frames=[Frame(M,BOTTOM,CW,HEIGHT-TOP-BOTTOM,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=self.page))
    def page(self,c,doc):
        c.saveState();font='Universal' if self.lang=='zh' else 'English'
        c.setFont(font,8.2);c.setFillColor(colors.HexColor('#535E68'))
        if doc.page>1:
            c.drawString(M,HEIGHT-27,front[self.lang]['title'])
        c.drawRightString(WIDTH-M,24,str(doc.page));c.restoreState()
    def afterFlowable(self,f):
        if hasattr(f,'bookmark'):
            self.canv.bookmarkPage(f.bookmark)
            self.canv.addOutlineEntry(f.plain,f.bookmark,level=f.outlevel,closed=True)
            if getattr(f,'catalog',False):
                self.notify('TOCEntry',(f.toclevel,f.toc,self.page,f.bookmark))
            if hasattr(f,'algid'):self.pages[str(f.algid)]=self.page

def make(lang):
    f=front[lang];font='Universal' if lang=='zh' else 'English';bold='Universal' if lang=='zh' else 'EnglishBold'
    styles={
      'body':ParagraphStyle('body',fontName=font,fontSize=10.4,leading=14.8,spaceAfter=5.5,wordWrap='CJK' if lang=='zh' else None,splitLongWords=True),
      'small':ParagraphStyle('small',fontName=font,fontSize=9,leading=12.5,spaceAfter=5,textColor=colors.HexColor('#45515D'),wordWrap='CJK' if lang=='zh' else None,splitLongWords=True),
      'title':ParagraphStyle('title',fontName=bold,fontSize=27 if lang=='zh' else 25,leading=33,spaceAfter=18,textColor=colors.black),
      'h1':ParagraphStyle('h1',fontName=bold,fontSize=17,leading=22,spaceAfter=11,spaceBefore=6,keepWithNext=True,textColor=colors.black),
      'h2':ParagraphStyle('h2',fontName=bold,fontSize=15.5,leading=21,spaceAfter=7,spaceBefore=5,keepWithNext=True,textColor=colors.black),
      'label':ParagraphStyle('label',fontName=bold,fontSize=10.5,leading=14,spaceAfter=4,spaceBefore=7,keepWithNext=True,textColor=colors.black),
      'list':ParagraphStyle('list',fontName=font,fontSize=10.4,leading=14.8,spaceAfter=4,leftIndent=17,firstLineIndent=-17,wordWrap='CJK' if lang=='zh' else None),
      'table':ParagraphStyle('table',fontName=font,fontSize=9.3,leading=13,spaceAfter=0,wordWrap='CJK' if lang=='zh' else None,splitLongWords=True),
      'toc':ParagraphStyle('toc',fontName=font,fontSize=9.6,leading=13.7,spaceBefore=3,leftIndent=14,firstLineIndent=-14,wordWrap='CJK' if lang=='zh' else None),
      'tocgroup':ParagraphStyle('tocgroup',fontName=bold,fontSize=11,leading=15.5,spaceBefore=9,spaceAfter=4,wordWrap='CJK' if lang=='zh' else None)
    }
    # Keep chapter-ending short lessons together by reducing paragraph gaps,
    # without shrinking type or line spacing.
    for name,changes in [('body',dict(spaceAfter=3)),('list',dict(spaceAfter=2)),('label',dict(spaceBefore=4,spaceAfter=2))]:
        styles['compact_'+name]=ParagraphStyle('compact_'+name,parent=styles[name],**changes)
    compact=False
    def p(text,style='body'):
        chosen='compact_'+style if compact and 'compact_'+style in styles else style
        return Paragraph(safe(text),styles[chosen])
    def heading(text,key,outlevel=0,style='h1',catalog=False,toclevel=0,toc=None,algid=None):
        q=p(text,style);q.bookmark=key;q.plain=text;q.outlevel=outlevel;q.catalog=catalog;q.toclevel=toclevel;q.toc=toc or safe(text)
        if algid is not None:q.algid=algid
        return q
    def table(rows,widths):
        rr=[[p(s,'table') for s in row] for row in rows]
        t=Table(rr,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DDE8F1')),('GRID',(0,0),(-1,-1),0.5,colors.HexColor('#D9D9D9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F6F8FA')])]))
        return t
    story=[]
    story.extend([Spacer(1,65),p(f['title'],'title'),p(f['subtitle'],'h2'),Spacer(1,17)])
    for v in f['cover']:story.append(p(v,'small'))
    story.extend([Spacer(1,28),p(f['opening']),Spacer(1,15),p('可搜索正文 可点击完整目录与书签 原创步骤图 参考来源' if lang=='zh' else 'Searchable text linked catalog and bookmarks original process diagrams cited sources','small'),PageBreak()])
    story.append(heading('第一次学，请从这里走' if lang=='zh' else 'A gentle first route','first_route'))
    routez=[
      '学习包里有一个总入口：00_从这里开始.html。第一次学，请双击它；用 Mac 上已有的 Safari、Chrome 或 Edge 打开即可。它把同样的完整内容分成小节，一次只读眼前的一小步。这份 PDF 是可以搜索、打印、反复查阅的完整手册，不要求你从第一页一口气读到最后。',
      '总入口先解释四张纸、大小关系、比较和换位置，再学插入、选择、冒泡、归并、快速和计数。完整目录按可比较条件下的效率分组；入门路线按理解的先后安排，两种顺序各有用途。',
      '读到“看对应动画”时再打开补充文件。初次只点“下一步”：先读这一步为什么这样做，再看长条。没看懂点“上一动作”。能说清一个动作以后，再点“自动慢播放”；播放中同一按钮变成“暂停”。“重看”回到开始。插入会有“手里暂存”，归并和计数有下方暂放或结果区；暂放的记录仍然存在。',
      '看过不等于学会。暂停在下一动作之前，先猜会比较谁、会不会移动、哪个位置会空出来；再点一步检查。最后用四张写着数字的纸自己操作一遍，并用自己的话说出为什么可以停止。每个入门小节都有练习和解释。',
      '六种基础方法有离线动画；全部 80 个学习条目都有完整步骤与数字示例，必要处有原创步骤图。高级方法先读本章“先把要用的小动作讲清楚”。遇到没有学过的树、堆、队列或二分，回到基础补充再继续。不必先记复杂度符号。',
      'HTML 与两份 PDF 放在同一个文件夹。总入口的链接靠这些相邻文件工作，所以移动时搬整个文件夹，解压下载包后再打开。离线内容不需要安装软件、注册账号或联网；外部参考来源和 VisuAlgo 链接需要联网。'
    ]
    routee=[
      'The package has one starting file: 00_从这里开始.html. Double-click it and open it with a browser already on your Mac, such as Safari, Chrome, or Edge. Choose English at the top. It presents the complete material in smaller pieces. This PDF is the searchable and printable reference; you do not need to read it all in one sitting.',
      'The guided route begins with four cards, comparing, and moving. It then teaches insertion, selection, bubble, merge, quick, and counting sort. The full catalog groups efficiency under comparable conditions. The beginner route follows what is easiest to understand first. Those orders serve different purposes.',
      'Open an animation when the starting file tells you to. At first use Next for one action. Read why it happens, then watch the bars. Use Previous action to revisit it. Once you can explain an action, use Play slowly; the same button becomes Pause. Start again returns to the beginning. A held item or a record in the lower tray still exists and must return to the final row.',
      'Before clicking Next, predict the comparison, movement, or new empty slot. Check your prediction with one step. Then repeat the method with four numbered paper cards. Explain in your own words why its stopping rule is safe. Each introductory lesson includes a question with an explained answer.',
      'Six basic methods have offline animations. All 80 learning entries have complete procedures and numeric examples, with original diagrams where useful. Begin an advanced entry with its small-action foundations. If a tree, heap, queue, or binary search is unfamiliar, open the foundation supplement first. Timing symbols can wait until the actions make sense.',
      'Keep both HTML files and both PDFs in one folder. Move the whole folder so local links keep working. After downloading the ZIP, extract it before opening the starting file. Offline lessons need no installation, account, or network connection. External references and optional VisuAlgo pages do need the internet.'
    ]
    for v in routez if lang=='zh' else routee:story.append(p(v))
    story.append(PageBreak())
    story.append(heading(f['scope_title'],'scope'))
    for v in f['scope']:story.append(p(v))
    story.extend([PageBreak(),heading('完整目录' if lang=='zh' else 'Complete catalog','catalog'),p('所有条目及别名先列于此。括号内说明计数类型，右侧为正文页码。' if lang=='zh' else 'Every entry and its alternate names appears here first. Labels distinguish algorithms from variants and supporting techniques. The right column gives the lesson page.','small')])
    toc=TableOfContents();toc.levelStyles=[styles['tocgroup'],styles['toc']];toc.dotsMinLevel=0
    story.append(toc);story.append(PageBreak())
    story.append(heading(f['primer_title'],'primer'))
    for title,body in f['primer']:
        story.append(p(title,'label'))
        for paragraph in (body if isinstance(body,list) else [body]):story.append(p(paragraph))
    story.extend([PageBreak(),heading(f['cost_title'],'efficiency'),p(f['cost_intro']),table(f['growth'],[83,279,CW-362]),Spacer(1,10)])
    for v in f['cost_notes']:story.append(p(v))
    story.extend([CondPageBreak(250),p('有条件的效率层级' if lang=='zh' else 'Conditional efficiency tiers','h2'),table(f['rank'],[112,216,CW-328]),Spacer(1,10),p(f['navigation'])])
    story.extend([PageBreak(),heading(f['reading_title'],'reading')])
    for v in f['reading']:story.append(p(v))
    story.append(p(f['diagram']))
    story.append(StateDiagram([
       dict(zh='比较 4 与 1；绿色区 [2,3] 只是局部有序',en='Compare 4 and 1; green [2,3] is only locally ordered',values=[4,1,2,3],active=[0,1],fixed=[2,3]),
       dict(zh='交换后两项标蓝；这里只是动作图例',en='Blue marks the swapped pair; this is only a legend',values=[1,4,2,3],moved=[0,1])
    ],lang))
    labels={'zh':{'idea':'基本思路','steps':'具体执行步骤','example':'跟着数字一步步做','cost':'要做多少事 要用多少地方','why':'为什么快或慢','use':'什么时候适合用','details':'最后把容易弄错的地方说清楚'},'en':{'idea':'The idea in plain words','steps':'Carry it out one action at a time','example':'Walk through the numbers','cost':'How much work and room it needs','why':'Why it is fast or slow','use':'When it is useful','details':'Details that make the procedure work'}}[lang]
    current=None
    for d in ordered:
        compact=lang=='zh' and d['id'] in [77,74]
        if current!=d['group']:
            story.append(PageBreak())
            current=d['group'];gt,gb=groups[lang][current]
            story.extend([heading(gt,'group_'+current,outlevel=0,catalog=True,toclevel=0),p(gb,'small'),Spacer(1,3)])
        else:
            story.extend([CondPageBreak(205),Spacer(1,12)])
        title=d['zh_title' if lang=='zh' else 'en_title'];alias=d['zh_alias' if lang=='zh' else 'en_alias']
        kind=kindnames[lang].get(d['kind'],d['kind'])
        htitle=f"{d['seq']:02d} {title}"
        alias=alias or ('无另列别名' if lang=='zh' else 'No additional alias listed')
        toctext=safe(htitle)+f' <font size="8.2">{safe(kind)} · {safe(alias)}</font>'
        story.append(heading(htitle,'alg_'+str(d['id']),outlevel=1,style='h2',catalog=True,toclevel=1,toc=toctext,algid=d['id']))
        story.append(p(('类型 ' if lang=='zh' else 'Type ')+kind+'   '+('别名或相关名称 ' if lang=='zh' else 'Aliases or related names ')+alias,'small'))
        a=d[lang]
        if a.get('foundation'):
            story.append(p('先把要用的小动作讲清楚' if lang=='zh' else 'First understand the small actions','label'))
            for paragraph in a['foundation']:story.append(p(paragraph))
        for k in ['idea','steps','example']:
            if lang=='zh' and d['id']==74 and k=='example':
                story.append(PageBreak())
            story.append(p(labels[k],'label'))
            if isinstance(a[k],list):
                for j,s in enumerate(a[k]):story.append(p(f'{j+1}. {s}','list'))
            else:story.append(p(a[k]))
        if d.get('visual'):
            story.extend([Spacer(1,6),StateDiagram(d['visual']['rows'],lang),Spacer(1,7)])
        if d['id'] in tree_specs:
            frames,caption=tree_specs[d['id']]
            story.extend([Spacer(1,6),TreeDiagram(frames,lang,caption),Spacer(1,7)])
        for k in ['cost','why','use']:
            story.extend([p(labels[k],'label'),p(a[k])])
        refline=('资料 ' if lang=='zh' else 'Sources ')+', '.join(f'[{n}]' for n in d['refnos'])
        linked=' '.join(f'<link href="#ref_{n}" color="#1C527E">[{n}]</link>' for n in d['refnos'])
        story.append(KeepTogether([p(labels['details'],'label'),p(a['details']),Paragraph(('参考来源 ' if lang=='zh' else 'References ')+linked,styles['small'])]))
    compact=False
    story.extend([PageBreak(),heading('实现检查与学习练习' if lang=='zh' else 'Implementation checks and practice','checks')])
    checkz=[
      '只检查是否升序不够。比较输入和输出的多重集合：每个值出现次数必须一致。对记录要比较身份，不能只比较键。',
      '稳定性测试使用 [2a,1,2b,1c]，应得到 [1,1c,2a,2b]，其中首个 1 是原来的那条记录。默认不稳定的算法可以通过加原位置次键改造，但需重新计算额外资源。',
      '边界样例至少包括空数组、单项、已排序、逆序、全部相等、很多重复、负数、极小/极大键、非二次幂长度。专用算法还要检查键域、位宽和哨兵前提。',
      '快排分区后验证区域关系并确保递归区间缩小；Hoare 分界不是枢轴最终位置。归并验证两输入段已有序；相等时先取左侧。堆删除后验证父子关系；桶排序不能把分桶完成当排序完成。',
      '性能实验固定规模、键类型、原输入、稳定要求、线程数和是否计入磁盘或设备传输。每轮用相同原输入的副本，记录多次运行的中位数，不把后一轮“已经排好”的输入拿来与第一轮比较。',
      '练习 1 用插入、Lomuto 快排和归并分别处理 [5,2,4,1,3]，记录每次比较后的动作。练习 2 用 LSD 排 [31,12,21,11]，解释为何十位分配必须稳定。练习 3 为相同值添加身份，寻找选择排序改变相等顺序的例子。练习 4 检验所有四项零一输入都通过本书五比较器小网络。'
    ]
    checke=[
      'Checking ascending order is not enough. Compare input and output multisets, including multiplicities. For records, compare identities as well as keys.',
      'A stability test such as [2a,1,2b,1c] should produce [1,1c,2a,2b], where the unlabeled 1 is the original record. Adding original positions can stabilize an unstable method, but its costs must be counted.',
      'Test empty and single-item inputs, sorted and reversed data, all-equal keys, many duplicates, negatives, extreme keys, and lengths that are not powers of two. Specialized methods also need domain, width, and sentinel checks.',
      'After quicksort partitioning, verify region relations and shrinking recursive ranges. A Hoare boundary is not a final pivot position. A merge needs ordered input runs and an earlier-left tie rule. Heap extraction must restore the heap rules; bucket placement alone is not a completed sort.',
      'Hold input size, key type, stability requirements, worker count, and included transfer costs fixed when measuring speed. Start each run from a copy of the same original data. Report repeated-run medians rather than comparing a later sorted input with an earlier random one.',
      'Practice 1 Trace insertion, Lomuto quicksort, and merge sort on [5,2,4,1,3]. Practice 2 Apply LSD radix sort to [31,12,21,11] and explain why the tens pass must be stable. Practice 3 Label equal records and find a selection-sort stability counterexample. Practice 4 Verify all four-item zero-one inputs against the five-comparator network.'
    ]
    for j,s in enumerate(checkz if lang=='zh' else checke):story.append(p(f'{j+1}. {s}','list'))
    story.extend([p('练习提示' if lang=='zh' else 'Practice hints','label'),p('LSD 个位后为 [31,21,11,12]，十位后为 [11,12,21,31]。选择排序的反例可用 [2a,2b,1]，第一次交换即成 [1,2b,2a]。四项零一网络共检查 2^4=16 个输入。' if lang=='zh' else 'The LSD units pass gives [31,21,11,12]; the tens pass gives [11,12,21,31]. For selection sort, [2a,2b,1] becomes [1,2b,2a] after its first exchange. A four-wire zero-one network check covers 2^4=16 inputs.')])
    story.extend([PageBreak(),heading('参考资料' if lang=='zh' else 'References','references'),p('来源核验日期 2026 年 10 月 5 日。定义与复杂度以所述版本为准；高级实现参考作者论文和源代码。下列标题和网址均可点击，正文引用编号可跳到对应条目。自制例子与图未复制来源的插图。' if lang=='zh' else 'Sources checked on 5 October 2026. Bounds apply to the versions described. Original papers and author implementations supply advanced details. Titles and URLs are clickable; lesson citations link to these entries. Examples and diagrams were constructed for this manual.','small')])
    for r in refs:
        h=p(f"[{r['num']}] {r['title']}",'label');h.bookmark='ref_'+str(r['num']);h.plain=r['title'];h.outlevel=1;h.catalog=False
        # Outline references remain under the reference chapter.
        story.append(h)
        story.append(Paragraph(f'<link href="{html.escape(r["url"],quote=True)}" color="#1C527E">{safe(r["url"])}</link>',styles['small']))
    path=O/('排序算法学习手册_中文版.pdf' if lang=='zh' else 'Sorting_Algorithms_Learning_Manual_English.pdf')
    doc=ManualDoc(path,lang,pagesize=A4,leftMargin=M,rightMargin=M,topMargin=TOP,bottomMargin=BOTTOM,title=f['title'],author='Codex',subject='Sorting algorithms teaching manual',pageCompression=1)
    doc.multiBuild(story,maxPasses=5)
    (QA_WORK/f'pages_{lang}.json').write_text(json.dumps(doc.pages,indent=2))
    print(lang, 'pages',doc.page,'references',len(refs),'bytes',path.stat().st_size)
    return path

if __name__=='__main__':
    (QA_WORK/'catalog.json').write_text(json.dumps(ordered,ensure_ascii=False,indent=2))
    (QA_WORK/'references.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2))
    for lang in ['zh','en']:make(lang)
