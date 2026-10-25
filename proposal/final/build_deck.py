from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.dml import MSO_LINE
from pptx.oxml.ns import qn
import copy
from lxml import etree

def C(h): return RGBColor(int(h[0:2],16),int(h[2:4],16),int(h[4:6],16))
PAPER=C('FBFAF7'); INK=C('1E2B33'); TEAL=C('0F766E'); AMB=C('B4540A'); MUTE=C('68757D'); RULE=C('D8D4CB'); TINT=C('E4EFEC'); WHITE=C('FFFFFF')
HEAD='Cambria'; BODY='Calibri'
prs=Presentation(); prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)
BL=prs.slide_layouts[6]
OUT='/tmp/claude-0/-home-user-IT-consultant/245700e8-423f-5342-bf38-0c57ee999fc0/scratchpad/build/NEW AURA.pptx'

def strip_style(sh):
    st=sh._element.find(qn('p:style'))
    if st is not None: sh._element.remove(st)

def T(s,x,y,w,h,paras,size=12,color=INK,bold=False,font=BODY,align=PP_ALIGN.LEFT,anchor=MSO_ANCHOR.TOP,space=4,italic=False,ls=None):
    tbx=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    tf=tbx.text_frame; tf.word_wrap=True; tf.vertical_anchor=anchor
    tf.margin_left=tf.margin_right=Inches(0.02); tf.margin_top=tf.margin_bottom=Inches(0.02)
    if isinstance(paras,str): paras=[paras]
    for i,p in enumerate(paras):
        para=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        para.alignment=align; para.space_after=Pt(space)
        if ls: para.line_spacing=ls
        runs=p if isinstance(p,list) else [p]
        for r in runs:
            if isinstance(r,str): r=(r,{})
            t,o=r
            run=para.add_run(); run.text=t; f=run.font
            f.name=o.get('font',font); f.size=Pt(o.get('size',size)); f.bold=o.get('bold',bold); f.italic=o.get('italic',italic)
            f.color.rgb=o.get('color',color)
    return tbx

def R(s,x,y,w,h,fill=None,line=None,lw=1,shape=MSO_SHAPE.RECTANGLE,dash=False):
    sh=s.shapes.add_shape(shape,Inches(x),Inches(y),Inches(w),Inches(h)); strip_style(sh)
    if fill is None: sh.fill.background()
    else: sh.fill.solid(); sh.fill.fore_color.rgb=fill
    if line is None: sh.line.fill.background()
    else:
        sh.line.color.rgb=line; sh.line.width=Pt(lw)
        if dash: sh.line.dash_style=MSO_LINE.DASH
    return sh

def RT(s,x,y,w,h,text,fill=None,line=None,color=INK,size=12,bold=False,align=PP_ALIGN.CENTER,shape=MSO_SHAPE.RECTANGLE,font=BODY,lw=1,dash=False):
    sh=R(s,x,y,w,h,fill,line,lw,shape,dash)
    tf=sh.text_frame; tf.word_wrap=True; tf.vertical_anchor=MSO_ANCHOR.MIDDLE
    tf.margin_left=tf.margin_right=Inches(0.05); tf.margin_top=tf.margin_bottom=Inches(0.02)
    p=tf.paragraphs[0]; p.alignment=align
    r=p.add_run(); r.text=text; f=r.font; f.name=font; f.size=Pt(size); f.bold=bold; f.color.rgb=color
    return sh

def L(s,x1,y1,x2,y2,color=RULE,w=0.75,dash=False,arrow=False):
    c=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x1),Inches(y1),Inches(x2),Inches(y2))
    strip_style(c)
    c.line.color.rgb=color; c.line.width=Pt(w)
    if dash: c.line.dash_style=MSO_LINE.DASH
    if arrow:
        ln=c.line._get_or_add_ln(); te=etree.SubElement(ln,qn('a:tailEnd')); te.set('type','triangle'); te.set('w','med'); te.set('len','med')
    return c

TRK=['IDENTIFY','PRIORITISE','SOLVE','SCALE']
def frame(n,title,lead=None,src=None,track=None):
    s=prs.slides.add_slide(BL)
    f=s.background.fill; f.solid(); f.fore_color.rgb=PAPER
    # tracker
    x=0.7
    for i,t in enumerate(TRK):
        on=(track==t)
        T(s,x,0.28,1.3,0.25,t,size=9,bold=on,color=TEAL if on else MUTE)
        if on: R(s,x,0.52,0.9,0.03,fill=TEAL)
        x+=1.15
    T(s,0.7,0.62,11.9,1.0,title,size=26,bold=True,font=HEAD,anchor=MSO_ANCHOR.TOP,ls=0.92)
    if lead: T(s,0.7,1.5,11.9,0.35,lead,size=13,color=MUTE)
    L(s,0.7,6.95,12.63,6.95,RULE,0.75)
    if src: T(s,0.7,6.55,11.9,0.38,src,size=8,color=MUTE,anchor=MSO_ANCHOR.BOTTOM)
    T(s,0.7,7.0,8,0.28,'New Aura  ·  IT Consultant Challenge 2026',size=9,color=MUTE)
    T(s,11.6,7.0,1.03,0.28,'%d / 10'%n,size=9,color=MUTE,align=PP_ALIGN.RIGHT)
    return s

def mix(c1,c2,t): return RGBColor(*[int(round(a+(b-a)*t)) for a,b in zip(c1,c2)])

# ================= 1 Executive summary
s=frame(1,'Nordic Flow: fix the allocation decision first, with a planner-approved service that cuts total logistics cost',
        'Executive summary for the Board of Company A',
        'Tags: [cited] = public source, listed on slides 2, 3, 8 and 9. [assumption] = replaced with Company A data in Week 1.')
qa=[('The problem','Goods allocation: which source and existing warehouse should serve each order. It sits where fulfilment, manual planning and fragmented systems meet.'),
('Who feels it','Planners and warehouse teams in every market; customers feel it as late or split orders.'),
('Why it matters','Margins are thin, so cost-to-serve is a real lever. Outside studies report savings from about 5% (modelled) to 10–15% (realised) [cited].'),
('What we propose','A planner-approved optimisation service on top of existing ERP, WMS and TMS. Nothing is replaced.'),
('MVP','Sweden, one region: 2 suppliers, 3 warehouses, 20 SKUs, one weekly run. Eight weeks to a go / no-go [assumption].'),
('Where AI helps','Data mapping, plain-language explanations, learning from planner overrides. The core is optimisation; a person approves.'),
('How it scales','Same engine with local data and rules: Sweden, then Denmark, then Norway, each wave gated by service and savings.')]
y=1.95
hs=[0.78,0.55,0.78,0.55,0.62,0.62,0.62]
for (k,v),h in zip(qa,hs):
    T(s,0.7,y,1.55,h,k.upper(),size=10,bold=True,color=TEAL,anchor=MSO_ANCHOR.TOP)
    T(s,2.3,y-0.03,5.75,h,v,size=12.5)
    L(s,0.7,y+h-0.04,8.05,y+h-0.04)
    y+=h
L(s,8.45,1.95,8.45,6.45,RULE)
stats=[('8 weeks','from approval to a go / no-go decision'),('≥ 5%','lower relevant logistics cost: our pilot gate [assumption]'),('3–6%','saving needed to break even in year 1 [assumption]'),('0','systems replaced; the planner approves every plan')]
y=1.95
for a,b in stats:
    T(s,8.75,y,3.9,0.6,a,size=34,bold=True,font=HEAD,color=TEAL)
    T(s,8.75,y+0.58,3.9,0.45,b,size=11.5,color=INK)
    y+=1.15

# ================= 2 Problem
s=frame(2,'The allocation lever looks real but modest, so Week 1 measures it before we commit',
        None,
        'Case brief pp. 8–11. David et al., Interfaces 45(3), 2015. McKinsey distribution-network case. DeHoratius & Raman, Management Science 54(4), 2008. Byggmax Annual Report 2025, p. 6 (EBITA 5.9%).',track='IDENTIFY')
colx=[0.7,4.45,8.4]; colw=[3.4,3.55,4.2]
heads=['CONFIRMED IN THE CASE','TO VERIFY IN WEEK 1','WHAT OUTSIDE EVIDENCE SUGGESTS']
for x,w,h in zip(colx,colw,heads):
    T(s,x,1.7,w,0.3,h,size=10,bold=True,color=TEAL); L(s,x,2.0,x+w,2.0,TEAL,1.25)
T(s,0.7,2.12,3.4,2.8,['Hundreds of stores in Denmark, Norway and Sweden, each market with its own systems.','Fulfilment and fragmented systems affect efficiency and reliability.','Impact and urgency differ by market.'],size=12.5,space=9)
T(s,4.45,2.12,3.55,2.8,['Planners optimise one leg at a time, not total cost.','Rates, stock and capacity sit in separate local systems.','Stock records may be wrong, so plans send goods to warehouses that do not have them.'],size=12.5,space=9)
ev=[('4.8%','lower delivered cost, building-products maker; modelled [cited]'),('10–15%','logistics saving, 150+ warehouse network; realised, consultancy [cited]'),('65%','of stock records inaccurate in one US retailer; profit down >10% [cited]')]
y=2.1
for a,b in ev:
    T(s,8.4,y,1.55,0.6,a,size=26,bold=True,font=HEAD,color=TEAL)
    T(s,10.0,y+0.05,2.65,0.7,b,size=11)
    y+=0.95
L(s,4.25,1.75,4.25,4.95,RULE); L(s,8.2,1.75,8.2,4.95,RULE)
T(s,8.4,4.95,4.25,0.45,[[('Byggmax 2025: ',{'bold':True}),('"restructured our logistics operations... increase control over flows" [cited]',{'italic':True})]],size=10,color=MUTE)
L(s,0.7,5.2,8.05,5.2)
T(s,0.7,5.28,1.3,0.3,'WHO FEELS IT',size=10,bold=True,color=TEAL)
T(s,2.0,5.26,6.05,0.7,'Planners and warehouse teams (manual re-planning), branch staff (stock not where promised), customers (late or split orders).',size=12)
T(s,0.7,5.95,1.3,0.3,'WHY NOW',size=10,bold=True,color=TEAL)
T(s,2.0,5.93,6.05,0.5,'Thin margins make cost-to-serve a lever: Byggmax EBITA 5.9% in 2025 [cited].',size=12)
RT(s,8.4,5.55,4.25,0.9,'Reading: a few percent is plausible, not guaranteed. We gate the pilot on a measured cost gap, not on a promise.',fill=TINT,color=INK,size=12,align=PP_ALIGN.LEFT)

# ================= 3 Prioritisation
s=frame(3,'Goods allocation leads once impact, speed and data readiness are weighed together',None,
        'Scores 1–5 are team judgement against case evidence, not company data. Weights: impact 30%, fit across DK/NO/SE 25%, time to market 25%, data readiness 20%. Delivery visibility (E) added by the team.',track='PRIORITISE')
opts=['A  Goods allocation','B  Order processing','C  Store standardisation','D  Systems replacement','E  Delivery visibility']
crit=[('Business impact','30%',[4,3,3,5,5]),('Fit across DK / NO / SE','25%',[4,3,2,5,3]),('Time to market','25%',[4,4,2,1,3]),('Data readiness','20%',[3,3,2,1,2])]
tot=[3.80,3.25,2.30,3.20,3.40]
x0=0.7; w0=2.55; cw=1.07; y0=1.75
for j,o in enumerate(opts):
    T(s,x0+w0+j*cw,y0,cw,0.62,o,size=10.5,bold=True,align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.BOTTOM,color=TEAL if j==0 else INK)
y=y0+0.7; rh=0.66
for name,wt,sc in crit:
    T(s,x0,y,w0,rh,[[(name,{'bold':True}),('  '+wt,{'color':MUTE,'size':10.5})]],size=12.5,anchor=MSO_ANCHOR.MIDDLE)
    for j,v in enumerate(sc):
        t=(v-1)/4
        col=mix((0xF1,0xF5,0xF3),(0x0F,0x76,0x6E),t*0.85)
        RT(s,x0+w0+j*cw+0.03,y+0.03,cw-0.06,rh-0.06,str(v),fill=col,color=WHITE if t>0.5 else INK,size=14,bold=True,font=HEAD)
    y+=rh
L(s,x0,y+0.04,x0+w0+5*cw,y+0.04,INK,1)
T(s,x0,y+0.1,w0,0.55,'Weighted score',size=12.5,bold=True,anchor=MSO_ANCHOR.MIDDLE)
for j,v in enumerate(tot):
    T(s,x0+w0+j*cw,y+0.1,cw,0.55,'%.2f'%v,size=16,bold=True,font=HEAD,align=PP_ALIGN.CENTER,anchor=MSO_ANCHOR.MIDDLE,color=TEAL if j==0 else INK)
R(s,x0+w0+0.01,y0+0.66,cw-0.02,3.35,line=TEAL,lw=1.75)
nx=9.0
notes=[('WHY A','An internal decision with no new driver, store or customer-facing change. It uses data the company already holds, so a CSV-based pilot runs in weeks.'),
('ROBUSTNESS','If impact is weighted 50%, E ties A at about 3.86 each. E is therefore our Phase 2: it reuses the same order and warehouse data.'),
('NOT NOW','B helps mainly Denmark and its savings claims come from vendors. C needs broad store discovery. D is multi-year and high risk.')]
y=1.75
for k,v in notes:
    T(s,nx,y,3.6,0.28,k,size=10,bold=True,color=TEAL)
    T(s,nx,y+0.28,3.6,1.1,v,size=12)
    y+=1.5
    if k!='NOT NOW': L(s,nx,y-0.1,nx+3.6,y-0.1)
L(s,8.75,1.75,8.75,6.3,RULE)

# ================= 4 MVP scope
s=frame(4,'A focused pilot: one Swedish region, three warehouses, 20 SKUs, one weekly planning run',None,
        'Sizes are [assumption]: the smallest network that still contains a real routing choice. Byggföretagen forecast: building investment +6% in total 2026–27, a fragile recovery [cited, autumn 2026 update]. Case p. 10 names delivery and fulfilment as Sweden\'s priority.',track='SOLVE')
# network diagram
bx,by,bw,bh=0.7,1.85,6.9,3.75
R(s,bx,by,bw,bh,line=MUTE,lw=1,dash=True)
T(s,bx+0.12,by+0.05,4,0.3,'PILOT BOUNDARY: ONE SWEDISH REGION',size=9,bold=True,color=MUTE)
sup=[(1.0,2.75),(1.0,3.9)]; wh=[(3.3,2.35),(3.3,3.3),(3.3,4.25)]; zn=[(5.7,2.75),(5.7,3.9)]
nw,nh=1.45,0.62
for x,y in sup:
    for x2,y2 in wh: L(s,x+nw,y+nh/2,x2,y2+nh/2,RULE,1)
for x,y in wh:
    for x2,y2 in zn: L(s,x+nw,y+nh/2,x2,y2+nh/2,RULE,1)
# highlighted plan
L(s,sup[0][0]+nw,sup[0][1]+nh/2,wh[0][0],wh[0][1]+nh/2,TEAL,2.5)
L(s,wh[0][0]+nw,wh[0][1]+nh/2,zn[0][0],zn[0][1]+nh/2,TEAL,2.5)
L(s,sup[1][0]+nw,sup[1][1]+nh/2,wh[2][0],wh[2][1]+nh/2,TEAL,2.5)
L(s,wh[2][0]+nw,wh[2][1]+nh/2,zn[1][0],zn[1][1]+nh/2,TEAL,2.5)
for i,(x,y) in enumerate(sup): RT(s,x,y,nw,nh,'Supplier %d'%(i+1),fill=INK,color=WHITE,size=11.5,bold=True)
for i,(x,y) in enumerate(wh): RT(s,x,y,nw,nh,'Warehouse %s'%'ABC'[i],fill=TEAL,color=WHITE,size=11.5,bold=True)
for i,(x,y) in enumerate(zn): RT(s,x,y,nw,nh,'Customer zone %d'%(i+1),fill=WHITE,line=INK,color=INK,size=11,bold=True)
T(s,1.0,2.35,1.45,0.3,'2 suppliers',size=10.5,color=MUTE); T(s,3.3,2.0,1.8,0.3,'3 existing warehouses',size=10.5,color=MUTE)
T(s,5.7,2.35,1.5,0.3,'Order zones',size=10.5,color=MUTE)
T(s,bx+0.12,bh+by-0.4,bw-0.2,0.32,[[('Teal lines: ',{'bold':True,'color':TEAL}),('one recommended plan. Grey lines: other allowed lanes.  ',{}),('20 palletised SKUs, one run per week.',{'bold':True})]],size=10.5)
nx=8.1
T(s,nx,1.85,4.5,0.3,'IN SCOPE',size=10,bold=True,color=TEAL); L(s,nx,2.15,12.63,2.15,TEAL,1.25)
T(s,nx,2.25,4.5,1.7,['+  Allocate inbound supply and confirmed orders across existing warehouses','+  Compare the current allocation with a feasible lower-cost plan, with cost by leg','+  Planner approves; every override is logged'],size=12,space=7)
T(s,nx,4.0,4.5,0.3,'OUT OF SCOPE',size=10,bold=True,color=AMB); L(s,nx,4.3,12.63,4.3,AMB,1.25)
T(s,nx,4.4,4.5,1.3,['–  New warehouses or site selection','–  Vehicle routing (stays in the current TMS)','–  Demand forecasting, production planning','–  ERP replacement; other countries'],size=12,space=5)
L(s,0.7,5.78,12.63,5.78)
T(s,0.7,5.84,1.5,0.3,'WHY SWEDEN FIRST',size=10,bold=True,color=TEAL)
T(s,2.3,5.82,10.3,0.6,'The case ties Sweden to fulfilment impact. It is a discovery candidate, not a commitment: if Week 1 data is better in Denmark or Norway, the pilot market changes.',size=12)

# ================= 5 Planner flow
s=frame(5,'The planner stays in control: the service recommends, a person approves, existing systems execute',None,
        'Illustrative output only. Each run stores the input version, solver status, approvals and planner overrides.',track='SOLVE')
steps=[('1  Load','Orders, supply, rates and warehouse limits from existing systems'),('2  Compare','Current allocation versus a feasible lower-cost plan'),('3  Review','Exceptions, service rules and cost by leg'),('4  Approve','Planner exports the plan; ERP, WMS and TMS execute it')]
for i,(a,b) in enumerate(steps):
    x=0.7+i*3.0
    RT(s,x,1.75,2.95,0.55,a,fill=TEAL if i<3 else INK,color=WHITE,size=14,bold=True,shape=MSO_SHAPE.PENTAGON,font=HEAD)
    T(s,x,2.4,2.7,0.85,b,size=11.5)
T(s,0.7,3.35,7,0.3,'RECOMMENDATION OUTPUT (EXAMPLE)',size=10,bold=True,color=TEAL); L(s,0.7,3.65,7.95,3.65,TEAL,1.25)
cols=[1.6,1.5,1.7,2.45]; hdr=['Supplier / SKU','Warehouse','Destination','Quantity / date']
rowsd=[['S1 / SKU-01','Warehouse A','Order zone North','60 pallets / within the week'],['S2 / SKU-01','Warehouse B','Order zone South','40 pallets / within the week']]
def mini(s,x,y,cols,hdr,rows,rh=0.4,size=11.5,boldfirst=True):
    cx=x
    for c,h in zip(cols,hdr): T(s,cx,y,c,0.3,h,size=10,color=MUTE,bold=True); cx+=c
    yy=y+0.32
    for r in rows:
        cx=x
        for i,(c,v) in enumerate(zip(cols,r)): T(s,cx,yy,c,rh,v,size=size,bold=(i==0 and boldfirst),anchor=MSO_ANCHOR.MIDDLE); cx+=c
        L(s,x,yy+rh,x+sum(cols),yy+rh); yy+=rh
    return yy
mini(s,0.7,3.75,cols,hdr,rowsd)
T(s,0.7,5.1,1.7,0.3,'NOT IN THE PILOT',size=10,bold=True,color=AMB)
T(s,0.7,5.38,7.2,1.1,['ERP replacement  ·  automatic execution of plans  ·  replacing planner judgement',[('Reuse before build: ',{'bold':True}),('local systems stay authoritative. We add one thin layer of CSV / API adapters, a validation step, the optimiser and a planner view.',{})]],size=12,space=6)
L(s,8.3,3.4,8.3,6.4,RULE)
T(s,8.6,3.35,4,0.3,'DATA THE PILOT NEEDS',size=10,bold=True,color=TEAL); L(s,8.6,3.65,12.63,3.65,TEAL,1.25)
mini(s,8.6,3.75,[1.5,1.4,1.13],['Data','Lives in','Owner'],[['Supply, orders','ERP','Planner'],['Rates, lanes','TMS, contracts','Logistics'],['Capacity, stock','WMS','Warehouse'],['Service rules','Local policy','Ops sponsor']],rh=0.42,size=11)
T(s,8.6,5.95,4.0,0.45,'Week 1 checks that each item exists and is usable.',size=10.5,color=MUTE,italic=True)

# ================= 6 Engine + AI
s=frame(6,'A constrained optimisation engine does the maths; AI helps around it, always with a human approving',None,
        'EU AI Act, Regulation (EU) 2024/1689, Art. 6 and Annex III. Google OR-Tools is open source (Apache 2.0).',track='SOLVE')
T(s,0.7,1.75,5.8,0.3,'THE DECISION ENGINE',size=10,bold=True,color=TEAL); L(s,0.7,2.05,6.7,2.05,TEAL,1.25)
rowsE=[('Minimise','inbound freight + handling + outbound freight + storage fees that change with the plan'),('Subject to','demand met, supply limits, warehouse handling limits, SKU eligibility, allowed lanes'),('Method','LP for divisible quantities; MILP for whole pallets and discrete commercial rules'),('Solver status','always shown: optimal, feasible within time limit, or infeasible with a diagnosis (short on supply, capacity or lanes)'),('Not counted','fixed rents already committed are not savings')]
y=2.15
for k,v in rowsE:
    T(s,0.7,y,1.35,0.6,k,size=12,bold=True,font=HEAD,color=TEAL)
    T(s,2.1,y,4.6,0.7,v,size=12)
    y+=0.72 if k in('Solver status',) else 0.6
    L(s,0.7,y-0.06,6.7,y-0.06)
L(s,7.1,1.8,7.1,5.5,RULE)
T(s,7.5,1.75,5.1,0.3,'WHERE AI ADDS VALUE',size=10,bold=True,color=TEAL); L(s,7.5,2.05,12.63,2.05,TEAL,1.25)
ai=[('1','Data mapping','Suggests SKU and unit matches across country systems; a person validates.'),('2','Plain-language explanations','Why a warehouse changed and which constraint binds, so the planner can check quickly.'),('3','Learning from overrides (Phase 2)','Planner corrections refine the rules over time.')]
y=2.2
for n,h,v in ai:
    T(s,7.5,y,0.6,0.8,n,size=34,bold=True,font=HEAD,color=TEAL)
    T(s,8.2,y+0.02,4.4,0.3,h,size=13,bold=True)
    T(s,8.2,y+0.34,4.4,0.7,v,size=12)
    y+=1.1
L(s,0.7,5.65,12.63,5.65)
T(s,0.7,5.72,1.6,0.3,'TECHNOLOGY',size=10,bold=True,color=TEAL)
T(s,2.3,5.7,4.4,0.8,'Python service with open-source OR-Tools, EU-hosted, role-based access. A scenario store keeps input versions, solver status and approvals for audit.',size=11.5)
T(s,7.5,5.72,1.7,0.3,'RESPONSIBLE BY DESIGN',size=10,bold=True,color=TEAL)
T(s,9.3,5.7,3.3,0.8,'Goods allocation is not an Annex III high-risk use [cited]. No profiling of staff. Data stays in EU hosting.',size=11.5)

# ================= 7 Worked example
s=frame(7,'A worked example shows where the saving comes from: seeing total cost across both legs',None,
        'Synthetic data for illustration: 1 SKU, 2 source warehouses, 2 destination zones. It demonstrates the mechanism and is not a forecast for Company A.',track='SOLVE')
T(s,0.7,1.75,5.6,0.3,'ROUTE COST PER PALLET (SOURCE → WAREHOUSE → ZONE)',size=10,bold=True,color=TEAL); L(s,0.7,2.05,6.3,2.05,TEAL,1.25)
hdr=['','A / North','A / South','B / North','B / South']; data=[['S1',5,9,11,8],['S2',6,10,8,5]]
cw=1.0; fx=1.3
for j,h in enumerate(hdr[1:]): T(s,fx+j*cw,2.15,cw,0.3,h,size=10.5,color=MUTE,bold=True,align=PP_ALIGN.CENTER)
used_base={('S1',1),('S2',2)}; used_opt={('S1',1),('S2',4)}
for i,r in enumerate(data):
    yy=2.5+i*0.62
    T(s,0.7,yy,0.6,0.55,r[0],size=13,bold=True,anchor=MSO_ANCHOR.MIDDLE)
    for j in range(1,5):
        isb=(r[0],j) in used_base; iso=(r[0],j) in used_opt
        fill=TEAL if iso else None
        RT(s,fx+(j-1)*cw+0.04,yy+0.03,cw-0.08,0.5,str(r[j]),fill=fill,line=None if iso else (AMB if isb else RULE),lw=1.75 if isb and not iso else 0.75,color=WHITE if iso else INK,size=14,bold=True,font=HEAD)
T(s,0.7,3.85,5.6,0.55,[[('Teal: ',{'bold':True,'color':TEAL}),('optimised plan.  ',{}),('Amber outline: ',{'bold':True,'color':AMB}),('baseline route that the optimiser changes.',{})]],size=11)
T(s,0.7,4.35,5.6,0.7,'Supply S1 / S2 = 60 / 40. Demand North / South = 60 / 40. Warehouse capacity A / B = 100 / 60. Both plans serve all 100 pallets.',size=11.5,color=MUTE)
L(s,6.75,1.8,6.75,5.3,RULE)
T(s,7.15,1.75,5.4,0.3,'TOTAL COST (COST UNITS)',size=10,bold=True,color=TEAL); L(s,7.15,2.05,12.63,2.05,TEAL,1.25)
scale=4.9/700.0
def bar(y,segs,label,total,tc):
    x=7.15
    T(s,x,y-0.34,5,0.3,label,size=11.5,bold=True)
    for v,txt,col,tcol in segs:
        w=v*scale; RT(s,x,y,w,0.62,txt,fill=col,color=tcol,size=11,bold=True); x+=w
    T(s,x+0.08,y,0.9,0.62,str(total),size=22,bold=True,font=HEAD,color=tc,anchor=MSO_ANCHOR.MIDDLE)
bar(2.75,[(300,'60 × 5 = 300',MUTE,WHITE),(400,'40 × 10 = 400',RULE,INK)],'Baseline: always use preferred warehouse A',700,MUTE)
bar(3.95,[(300,'60 × 5 = 300',MUTE,WHITE),(200,'40 × 5 = 200',TEAL,WHITE)],'Optimised: send the second 40 pallets via warehouse B',500,TEAL)
T(s,7.15,4.85,5.4,0.4,'Saving: 200 units, 28.6%, on synthetic data only.',size=12,bold=True,color=TEAL)
L(s,0.7,5.5,12.63,5.5)
T(s,0.7,5.58,12,0.9,[[('What it shows. ',{'bold':True,'color':TEAL}),('The saving comes from seeing both legs together, not from a cheaper single leg. Habit fills the preferred warehouse; the optimiser uses the cheaper route that still respects capacity. Real gains are expected to be far smaller than 28.6%; the next slide shows what must be true.',{})]],size=12.5)

# ================= 8 Business impact
s=frame(8,'The case to proceed: a saving of only 3–6% breaks even in year one, and Week 1 measures the real figure',None,
        'All cost inputs are [assumption], replaced with Company A data in Week 1. Outside benchmarks: ~4.8% modelled (Interfaces, 2015), 10–15% realised (McKinsey). Only costs that change with allocation count; labour savings are assessed separately.',track='SOLVE')
T(s,0.7,1.75,6.5,0.3,'ANNUAL SAVING BY SAVING RATE (€ MILLION)',size=10,bold=True,color=TEAL); L(s,0.7,2.05,7.2,2.05,TEAL,1.25)
cx0,cy0,cw_,ch_=1.3,2.3,5.9,2.85   # chart area
maxv=1.0
def ypos(v): return cy0+ch_-(v/maxv)*ch_
for v in (0,0.25,0.5,0.75,1.0):
    L(s,cx0,ypos(v),cx0+cw_,ypos(v),RULE,0.5)
    T(s,0.7,ypos(v)-0.12,0.55,0.25,'%.2f'%v,size=9,color=MUTE,align=PP_ALIGN.RIGHT)
groups=[('2%',(0.10,0.20)),('5%',(0.25,0.50)),('10%',(0.50,1.00))]
gw=cw_/3
for i,(lab,(a,b)) in enumerate(groups):
    gx=cx0+i*gw+0.35
    for k,(v,col,txt) in enumerate([(a,MUTE,'€5M'),(b,TEAL,'€10M')]):
        bx=gx+k*0.95; top=ypos(v)
        R(s,bx,top,0.8,cy0+ch_-top,fill=col)
        T(s,bx-0.1,top-0.28,1.0,0.26,'%.2f'%v,size=10.5,bold=True,align=PP_ALIGN.CENTER)
    T(s,gx,cy0+ch_+0.05,1.75,0.3,lab,size=12,bold=True,align=PP_ALIGN.CENTER)
L(s,cx0,ypos(0.3),cx0+cw_,ypos(0.3),AMB,1.5,dash=True)
T(s,cx0+0.05,ypos(0.3)-0.3,3.6,0.28,'Year-1 cost to recover: €0.3M (build 0.2 + run 0.1)',size=10,bold=True,color=AMB)
RT(s,0.7,5.65,0.22,0.2,'',fill=MUTE); T(s,0.98,5.6,2.3,0.3,'€5M relevant cost in scope',size=10.5)
RT(s,3.4,5.65,0.22,0.2,'',fill=TEAL); T(s,3.68,5.6,2.4,0.3,'€10M relevant cost in scope',size=10.5)
T(s,0.7,5.95,6.6,0.55,[[('Break-even rate = ',{'bold':True}),('€0.3M ÷ relevant cost: ',{}),('6.0%',{'bold':True,'color':MUTE}),(' at €5M, ',{}),('3.0%',{'bold':True,'color':TEAL}),(' at €10M. The 5% gate clears break-even when the relevant cost is about €6M or more.',{})]],size=11.5)
L(s,7.65,1.8,7.65,6.45,RULE)
T(s,8.0,1.75,4.6,0.3,'PILOT ACCEPTANCE GATES (HYPOTHESES)',size=10,bold=True,color=TEAL); L(s,8.0,2.05,12.63,2.05,TEAL,1.25)
gates=[('Relevant logistics cost','≥ 5% below a validated feasible baseline, same orders'),('Planner preparation time','≥ 30% lower, full task including data checks'),('Service','No deterioration in on-time, in-full rate'),('Feasibility','Zero hard-constraint violations')]
y=2.2
for a,b in gates:
    T(s,8.0,y,4.6,0.28,a,size=12,bold=True); T(s,8.0,y+0.28,4.6,0.5,b,size=11.5,color=INK); y+=0.85; L(s,8.0,y-0.08,12.63,y-0.08)
RT(s,8.0,5.65,4.63,0.8,'Scale only when validated savings cover delivery and operating cost. No revenue uplift is assumed.',fill=TINT,size=11.5,align=PP_ALIGN.LEFT)

# ================= 9 Scale
s=frame(9,'One engine, three rollouts: each market gets the same core with local data and rules',None,
        'Eurostat isoc_ec_eseln2 (2024, wholesale, ≥10 employees); Digdir (NO) and Erhvervsstyrelsen (DK) e-invoicing analyses. Case p. 11: one strategic solution does not mean one identical implementation. Rollout order is a proposal.',track='SCALE')
hd=[('WAVE',0.7,0.8),('LOCAL EMPHASIS',1.6,4.0),('EVIDENCE TO COLLECT FIRST',5.8,6.8)]
for t,x,w in hd: T(s,x,1.7,w,0.3,t,size=10,bold=True,color=TEAL)
L(s,0.7,2.0,12.63,2.0,TEAL,1.25)
lanes=[('1','Sweden','Pilot one region from CSV exports; the planner reviews every plan.','Rates, stock, service rules and warehouse capacity.'),
('2','Denmark','Reuse the engine; adapt the import to cut manual preparation.','Structured B2B e-invoices only 5–10% [cited], so inputs need more cleaning. Wholesale EDI sales 39% [cited].'),
('3','Norway','Validate branch and distribution workflows before connecting.','Structured B2B e-invoices 89% [cited]; wholesale EDI sales 27% [cited]. Store receiving limits, carrier rules.')]
y=2.1
for n,m,a,b in lanes:
    RT(s,0.7,y+0.1,0.55,0.55,n,fill=TEAL,color=WHITE,size=16,bold=True,shape=MSO_SHAPE.OVAL,font=HEAD)
    T(s,1.6,y+0.03,4.0,0.3,m,size=13,bold=True,font=HEAD); T(s,1.6,y+0.33,4.0,0.6,a,size=11.5)
    T(s,5.8,y+0.03,6.8,0.9,b,size=11.5)
    y+=0.88; L(s,0.7,y-0.03,12.63,y-0.03)
RT(s,0.7,y+0.12,11.93,0.5,'Shared core:  data contract  ·  optimisation rules  ·  audit trail  ·  KPI definitions.  Local teams own rates, service rules and approval rights.',fill=INK,color=WHITE,size=12,bold=True)
y2=y+0.78
T(s,0.7,y2,1.5,0.3,'EMPLOYEES',size=10,bold=True,color=TEAL)
T(s,0.7,y2+0.28,5.6,0.9,'Planners co-design the workflow and keep the final say; overrides are logged, not punished. Training in the first week of each wave.',size=12)
L(s,6.65,y2,6.65,y2+1.1,RULE)
T(s,7.0,y2,1.5,0.3,'CUSTOMERS',size=10,bold=True,color=TEAL)
T(s,7.0,y2+0.28,5.6,0.9,'No change to ordering. The on-time, in-full rate is a gate before each wave, so service cannot quietly worsen.',size=12)

# ================= 10 Plan, risks, decision
s=frame(10,'Eight weeks to a pilot decision, with the main risks designed out and a clear ask',None,
        'Stock-record accuracy: DeHoratius & Raman (2008). Plan and sizes are indicative and depend on data access.',track='SCALE')
gx=3.3; gw=0.6
T(s,0.7,1.7,2.5,0.3,'INDICATIVE 8-WEEK PLAN',size=10,bold=True,color=TEAL)
for w in range(8):
    T(s,gx+w*gw,1.7,gw,0.3,'W%d'%(w+1),size=9.5,color=MUTE,align=PP_ALIGN.CENTER)
L(s,0.7,2.0,gx+8*gw,2.0,TEAL,1.25)
plan=[('Validate problem and data',1,1,'Baseline, scope, service rules agreed'),('Build MVP: engine, import, plan view',2,4,'Plans pass historical replay'),('Controlled trial with local planners',5,6,'Planner acceptance, service evidence'),('Review economics and readiness',7,8,'Scale, revise or stop against gates')]
y=2.1
for lab,a,b,ex in plan:
    T(s,0.7,y,2.55,0.45,lab,size=11.5,bold=True,anchor=MSO_ANCHOR.MIDDLE)
    for w in range(8): L(s,gx+w*gw,y,gx+w*gw,y+0.45,RULE,0.4)
    R(s,gx+(a-1)*gw+0.03,y+0.08,(b-a+1)*gw-0.06,0.29,fill=TEAL)
    R(s,gx+b*gw-0.14,y+0.12,0.2,0.2,fill=AMB,shape=MSO_SHAPE.DIAMOND)
    y+=0.55
T(s,0.7,4.35,7.9,0.3,[[('◆ ',{'color':AMB,'bold':True}),('Exit gates: ',{'bold':True}),('agreed baseline  ·  replay passed  ·  planner acceptance  ·  go / revise / stop',{})]],size=10.5,color=INK)
T(s,0.7,4.75,3,0.3,'MAIN RISKS',size=10,bold=True,color=AMB); L(s,0.7,5.05,8.6,5.05,AMB,1.25)
risks=[('Stock or rate data is wrong','65% of records in one study. Validation step; block invalid runs; planner approves.'),
('Inbound freight paid by suppliers','Seen at Byggmax. Week 1 confirms who pays; if suppliers, optimise the warehouse-to-customer leg and handling only.'),
('Weak baseline overstates the gain','Compare against a validated feasible baseline on the same orders.'),
('Low planner adoption','Co-design, keep overrides, show cost by leg.')]
y=5.1
for a,b in risks:
    T(s,0.7,y,2.4,0.4,a,size=11,bold=True); T(s,3.15,y,5.45,0.4,b,size=10.5)
    y+=0.37 if a!='Inbound freight paid by suppliers' else 0.46
R(s,9.0,1.75,3.63,4.7,fill=INK)
T(s,9.25,1.95,3.2,0.3,'DECISION REQUESTED',size=10,bold=True,color=C('8FD0C8'))
T(s,9.25,2.35,3.2,4.0,[[('1',{'font':HEAD,'size':22,'bold':True,'color':C('8FD0C8')}),('  Approve Week 1 Swedish discovery and a capped pilot design.',{})],[('2',{'font':HEAD,'size':22,'bold':True,'color':C('8FD0C8')}),('  Name a business owner and a local process owner.',{})],[('3',{'font':HEAD,'size':22,'bold':True,'color':C('8FD0C8')}),('  Proceed only if data, a measured cost gap and ownership are confirmed; otherwise iterate or stop.',{})]],size=13,color=WHITE,space=14)
prs.save(OUT)
