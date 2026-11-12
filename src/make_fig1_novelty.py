from pathlib import Path
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'paper'/'figures'
OUT.mkdir(parents=True,exist_ok=True)

mpl.rcParams.update({
    'font.family':'sans-serif',
    'font.sans-serif':['DejaVu Sans','sans-serif'],
    'svg.fonttype':'none',
    'pdf.fonttype':42,
    'font.size':7.2,
})

fig,ax=plt.subplots(figsize=(7.2,2.9))
ax.set_xlim(0,14.4); ax.set_ylim(0,5.4); ax.axis('off')

def box(x,y,w,h,text,weight='normal',fs=7.0,ls='-'):
    p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.035,rounding_size=0.05',
                     linewidth=0.9,edgecolor='black',facecolor='white',linestyle=ls)
    ax.add_patch(p)
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fs,fontweight=weight)
    return p

def arrow(x1,y1,x2,y2,ls='-',lw=0.9):
    a=FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=8,
                      linewidth=lw,linestyle=ls,color='black')
    ax.add_patch(a)

# Panel divider
ax.plot([7.15,7.15],[0.18,5.18],color='black',linewidth=0.7,linestyle='--')

# Panel A
ax.text(0.18,5.10,'a  Positive provenance can pass an incomplete set',fontsize=8.7,fontweight='bold')
ax.text(0.25,4.55,'Expected source membership',fontsize=7.2)
for i,label in enumerate(['e1','e2','e3','e4','e5']):
    cx=0.55+i*0.72
    c=Circle((cx,4.05),0.19,facecolor='white',edgecolor='black',linewidth=0.9)
    ax.add_patch(c); ax.text(cx,4.05,label,ha='center',va='center',fontsize=6.7)

ax.text(2.00,3.58,'suppress e3 before\nprovenance starts',ha='center',va='center',fontsize=6.9)
arrow(2.00,3.48,2.00,3.05)

box(0.35,2.22,3.55,0.78,'Delivered evidence\ne1   e2   e4   e5   (all authentic)',fs=7.0)
arrow(3.90,2.61,4.35,2.61)
box(4.35,2.22,2.15,0.78,'Positive-provenance\nchecks',weight='bold',fs=6.9)
ax.text(5.43,1.78,'PASS',ha='center',fontsize=8.0,fontweight='bold')

ax.text(0.35,1.18,'Verifier sees the same delivered set in two possible worlds:',fontsize=6.9,fontweight='bold')
ax.text(0.35,0.82,'World 1: {e1,e2,e4,e5} was complete',fontsize=6.7)
ax.text(0.35,0.49,'World 2: e3 existed but disappeared upstream',fontsize=6.7)
ax.text(0.35,0.12,'Observed evidence alone cannot tell which world is real.',fontsize=7.0,fontweight='bold')

# Panel B
ax.text(7.38,5.10,'b  ECI checks expected membership',fontsize=8.7,fontweight='bold')

box(7.50,4.10,2.65,0.78,'Trusted obligation\nΩ(q)={e1,e2,e3,e4,e5}',weight='bold',fs=6.8)
arrow(10.15,4.49,10.55,4.49)
box(10.55,4.10,3.25,0.78,'Authenticated\nexpected-set commitment',fs=6.9)

box(7.50,2.82,2.65,0.78,'Semantic evidence\ne1, e2, e4, e5',fs=7.0)
arrow(10.15,3.21,10.55,3.21)
box(10.55,2.82,3.25,0.78,'Coverage-carrying DAG\nclosure={e1,e2,e4,e5}',fs=6.9)

arrow(12.18,2.82,12.18,2.34)
box(10.25,1.48,3.85,0.78,'WhyNotGate\nΩ(q) \\ closure = {e3}',weight='bold',fs=7.1)
arrow(12.18,1.48,12.18,1.05)
ax.text(12.18,0.72,'BLOCK before sensitive commit',ha='center',fontsize=7.8,fontweight='bold')
ax.text(7.50,0.14,'Negative provenance asks what should have been present but is missing.',
        fontsize=7.0,fontweight='bold')

fig.subplots_adjust(left=0.015,right=0.995,top=0.98,bottom=0.04)
for ext,kwargs in [('pdf',{}),('svg',{}),('png',{'dpi':300})]:
    fig.savefig(OUT/f'fig1_omissionshield_overview.{ext}',bbox_inches='tight',**kwargs)
plt.close(fig)
print('wrote',OUT/'fig1_omissionshield_overview.pdf')
