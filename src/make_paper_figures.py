from pathlib import Path
import json
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'paper' / 'figures'
OUT.mkdir(parents=True, exist_ok=True)

mpl.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'sans-serif'],
    'svg.fonttype': 'none',
    'pdf.fonttype': 42,
    'font.size': 8,
    'axes.spines.right': False,
    'axes.spines.top': False,
    'axes.linewidth': 0.8,
    'legend.frameon': False,
})

def save(fig, stem):
    fig.savefig(OUT / f'{stem}.pdf', bbox_inches='tight')
    fig.savefig(OUT / f'{stem}.svg', bbox_inches='tight')
    fig.savefig(OUT / f'{stem}.png', dpi=300, bbox_inches='tight')
    plt.close(fig)

# Figure 1: threat + runtime control plane
fig, ax = plt.subplots(figsize=(7.0, 2.55))
ax.set_xlim(0, 12)
ax.set_ylim(0, 4.2)
ax.axis('off')

def box(x, y, w, h, text, fc='white', lw=1.0):
    p = FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.03,rounding_size=0.06',
                       linewidth=lw, edgecolor='black', facecolor=fc)
    ax.add_patch(p)
    ax.text(x+w/2, y+h/2, text, ha='center', va='center', fontsize=8)
    return p

def arrow(x1, y1, x2, y2, style='-|>', ls='-', lw=1.0):
    a = FancyArrowPatch((x1,y1),(x2,y2),arrowstyle=style,mutation_scale=10,
                        linewidth=lw, linestyle=ls, color='black')
    ax.add_patch(a)

ax.text(0.1, 3.92, 'a  Selective Evidence Suppression', fontweight='bold', fontsize=9)
box(0.2, 2.35, 1.7, 0.75, 'Bounded source\n$E^* = \\{e_1,...,e_n\\}$')
box(2.55, 2.35, 1.65, 0.75, 'Retriever /\norchestrator')
box(5.0, 2.35, 1.65, 0.75, 'LLM / agent\ndecision')
box(7.45, 2.35, 1.65, 0.75, 'Sensitive\naction')
arrow(1.9,2.72,2.55,2.72)
arrow(4.2,2.72,5.0,2.72)
arrow(6.65,2.72,7.45,2.72)
ax.text(4.58, 3.18, 'attacker suppresses $S$', ha='center', va='center', fontsize=7.5)
ax.annotate('', xy=(4.55,2.93), xytext=(4.55,3.42), arrowprops=dict(arrowstyle='-|>', lw=1.0))
ax.text(2.9,1.78,'All delivered evidence can remain authentic.', fontsize=7.5)
ax.text(2.9,1.48,'The failure is that required membership changed.', fontsize=7.5)

ax.text(9.7, 3.92, 'b  OmissionShield', fontweight='bold', fontsize=9, ha='center')
box(9.65, 2.75, 1.85, 0.65, 'Authenticated\nexpected set')
box(9.65, 1.65, 1.85, 0.65, 'Runtime-owned\nevidence DAG')
box(9.65, 0.55, 1.85, 0.65, 'WhyNotGate\nALLOW / BLOCK')
arrow(10.57,2.75,10.57,2.30)
arrow(10.57,1.65,10.57,1.20)
ax.text(8.65,0.12,'Missing required source IDs become observable before commit.', fontsize=7.3)
save(fig, 'fig1_omissionshield_overview')

# Figure 2: cross-model real-CVE vulnerability
stats = json.loads((ROOT/'results/tqrg_crossmodel/final_crossmodel_stats.json').read_text())
models = ['Qwen3', 'Qwen2.5-VL-7B']
keys = ['qwen3','qwen2_5_vl_7b']
rates=[]; lo=[]; hi=[]; full=[]; nums=[]
for k in keys:
    d=stats[k]
    rates.append(100*d['vulnerable_leq2_rate_cond_full_correct'])
    ci=d['vulnerable_leq2_ci95']; lo.append(100*(d['vulnerable_leq2_rate_cond_full_correct']-ci[0])); hi.append(100*(ci[1]-d['vulnerable_leq2_rate_cond_full_correct']))
    full.append(100*d['full_accuracy'])
    nums.append((d['vulnerable_leq2'], d['full_correct']))

fig, ax = plt.subplots(figsize=(3.45, 2.65))
x=range(len(models))
ax.errorbar(list(x), rates, yerr=[lo,hi], fmt='o', markersize=6, capsize=4, linewidth=1.2)
ax.set_xticks(list(x), models)
ax.set_ylim(0,100)
ax.set_ylabel('Vulnerable within ≤2 suppressions (%)')
ax.set_title('Real security-fix commits, conditional on full-evidence competence', fontsize=8.5)
ax.grid(axis='y', alpha=0.2)
for i,(r,(a,b),fa) in enumerate(zip(rates,nums,full)):
    ax.text(i, r+7, f'{a}/{b} ({r:.1f}%)', ha='center', fontsize=7.3)
    ax.text(i, 4, f'full-evidence acc. {fa:.1f}%', ha='center', fontsize=6.8)
ax.text(0.01, -0.29, 'Wilson 95% confidence intervals; 49 independent project/CVE commits.', transform=ax.transAxes, fontsize=6.6)
save(fig, 'fig2_crossmodel_vulnerability')

print('wrote:', *(str(p) for p in sorted(OUT.glob('fig*'))), sep='\n')
