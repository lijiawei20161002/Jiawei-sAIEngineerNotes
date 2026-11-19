"""English model diagram and conditional empirical fit from saved estimates."""
from pathlib import Path
import os,json,tempfile
ROOT=Path(__file__).resolve().parents[1]
FIGURES=ROOT/"figures"
FIGURES.mkdir(exist_ok=True)
os.environ.setdefault('MPLCONFIGDIR',str(Path(tempfile.gettempdir())/'discourse_selection_matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
import numpy as np

plt.rcParams.update({'font.family':'DejaVu Sans','svg.fonttype':'path'})
BLUE='#245b80';ORANGE='#a85e20';INK='#172b3b'
fig,ax=plt.subplots(figsize=(7,3.15),dpi=240)
ax.set(xlim=(0,14),ylim=(0,6.3));ax.axis('off')
def label(x,y,s,size=9,color=INK,ha='center'):
    ax.text(x,y,s,fontsize=size,color=color,ha=ha,va='center',linespacing=1.3)
def box(x,y,w,h,s,color=BLUE):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.08,rounding_size=.08',lw=1,edgecolor=color,facecolor='#fff4e8' if color==ORANGE else '#eff6fb'))
    label(x,y,s,color=color)
def arrow(a,b,rad=0,dashed=False,color=BLUE):
    ax.add_patch(FancyArrowPatch(a,b,connectionstyle=f'arc3,rad={rad}',arrowstyle='-|>',mutation_scale=10,lw=1.1,linestyle=(0,(3,2)) if dashed else '-',color=color))
box(3,4.8,3.2,.75,'Inactive: A(t) = 0')
box(11,4.8,3.2,.75,'Active: A(t) = 1')
arrow((4.7,4.98),(9.3,4.98),-.10);label(7,5.48,'Return: q(t)')
arrow((9.3,4.60),(4.7,4.60),-.10);label(7,3.98,'Stop: 1−s(t)')
arrow((2.1,5.27),(3.9,5.27),-.55);label(3,6.02,'Remain inactive: 1−q(t)',8.5)
arrow((10.1,5.27),(11.9,5.27),-.55);label(11,6.02,'Continue: s(t)',8.5)
label(7,3.27,'Participation payoff index: α − δt + ρA(t−1)',10)
ax.plot([.3,13.7],[2.85,2.85],color='#d4dde4',lw=.8)
label(.35,2.45,'Optional extension (not estimated)',9,color=ORANGE,ha='left')
box(2.2,1.43,3.6,.9,'Public commitments\nand social feedback',ORANGE)
box(7,1.43,3.2,.9,'Entrenchment e\n(resistance to revision)',ORANGE)
box(11.8,1.43,3.6,.9,'Private updating and\nfuture participation',ORANGE)
arrow((4.15,1.43),(5.25,1.43),dashed=True,color=ORANGE)
arrow((8.75,1.43),(9.85,1.43),dashed=True,color=ORANGE)
label(7,.42,'Transitions apply after first contribution; individual indices are omitted.',8,color='#516779')
fig.subplots_adjust(left=.01,right=.99,top=.99,bottom=.01)
for ext in ('png','svg'):fig.savefig(FIGURES/f'fitted_process.{ext}',dpi=240,facecolor='white')
plt.close(fig)

r=json.loads((ROOT/'data'/'participation_model_fit.json').read_text())
x=np.arange(1,15)
fig,ax=plt.subplots(figsize=(7,3.0),dpi=240)
ax.plot(x,np.array(r['models']['decay']['expected_daily_returning'])[1:],color=BLUE,lw=2,label='Fitted decline model')
ax.plot(x,np.array(r['models']['constant']['expected_daily_returning'])[1:],color='#8997a4',lw=1.5,ls='--',label='Constant-probability baseline')
ax.scatter(x,np.array(r['daily_returning_accounts'])[1:],color=INK,s=23,zorder=4,label='Observed returning accounts')
ax.set(xlim=(.7,14.3),ylim=(-.15,3.7),ylabel='Returning accounts per day',xlabel='UTC date (December 2024 to January 2025)')
ax.set_xticks([1,3,5,7,9,11,14],['Dec 19','Dec 21','Dec 23','Dec 25','Dec 27','Dec 29','Jan 1'])
ax.set_yticks([0,1,2,3]);ax.grid(axis='y',alpha=.18);ax.spines[['top','right']].set_visible(False)
ax.legend(frameon=False,fontsize=8.2,loc='upper right')
ax.set_title('Observed participation versus model fit',fontsize=11,loc='left',pad=10)
fig.subplots_adjust(left=.09,right=.98,top=.83,bottom=.20)
for ext in ('png','svg'):fig.savefig(FIGURES/f'participation_fit.{ext}',dpi=240,facecolor='white')
plt.close(fig)
print('Saved English process and fitted-data figures.')
