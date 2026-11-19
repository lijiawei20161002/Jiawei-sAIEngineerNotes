"""English model diagram and conditional empirical fit from saved estimates."""
from pathlib import Path
import argparse,os,json,tempfile
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
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--process-only',action='store_true',help='Update the model diagram without rebuilding the unchanged empirical plot.')
args=parser.parse_args()
BLUE='#245b80';ORANGE='#a85e20';INK='#172b3b'
fig,ax=plt.subplots(figsize=(7,2.8),dpi=240)
ax.set(xlim=(0,14),ylim=(0,6.1));ax.axis('off')
def label(x,y,s,size=8.4,color=INK,ha='center'):
    ax.text(x,y,s,fontsize=size,color=color,ha=ha,va='center',linespacing=1.3)
def box(x,y,w,h,s,color=BLUE):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.08,rounding_size=.08',lw=1,edgecolor=color,facecolor='#fff4e8' if color==ORANGE else '#eff6fb'))
    label(x,y,s,color=color)
def arrow(a,b,rad=0,dashed=False,color=BLUE):
    ax.add_patch(FancyArrowPatch(a,b,connectionstyle=f'arc3,rad={rad}',arrowstyle='-|>',mutation_scale=10,lw=1.1,linestyle=(0,(3,2)) if dashed else '-',color=color))
label(.3,5.82,'Channel choice (not estimated): benefit B − opportunity cost c × time τ',8.6,ORANGE,'left')
box(2.35,5.15,3.9,.60,'Public advice: V(public)',ORANGE)
box(7,5.15,3.9,.60,'Private advice: V(private)',ORANGE)
box(11.65,5.15,3.9,.60,'Other work: reference 0',ORANGE)
label(7,4.58,'Each day: choose the highest net benefit + an option-specific random shock.',8)
ax.plot([.3,13.7],[4.25,4.25],color='#d4dde4',lw=.8)
label(.3,3.94,'Estimated public-return process, conditional on first contribution',8.6,BLUE,'left')
box(3,2.77,4.2,.64,'No thread comment: A(t) = 0')
box(11,2.77,4.2,.64,'Thread comment: A(t) = 1')
arrow((5.2,2.94),(8.8,2.94),-.13);label(7,3.38,'Return: q(t)',8)
arrow((8.8,2.60),(5.2,2.60),-.13);label(7,2.16,'Stop: 1−s(t)',8)
arrow((1.8,3.17),(3.8,3.17),-.25);label(2.8,3.62,'Stay: 1−q(t)',7.7)
arrow((10.2,3.17),(12.2,3.17),-.25);label(11.2,3.62,'Continue: s(t)',7.7)
label(7,1.65,'A = 0 does not distinguish private advice from other activities.',8,color='#516779')
ax.plot([.3,13.7],[1.35,1.35],color='#d4dde4',lw=.8)
label(.3,1.07,'Entrenchment extension (not estimated)',8.6,ORANGE,'left')
label(2.1,.48,'Commitments / feedback',8,color=ORANGE)
label(7,.48,'Resistance to revision: e',8,color=ORANGE)
label(11.8,.48,'Later beliefs / choices',8,color=ORANGE)
arrow((4.25,.48),(4.95,.48),dashed=True,color=ORANGE)
arrow((9.05,.48),(9.70,.48),dashed=True,color=ORANGE)
fig.subplots_adjust(left=.01,right=.99,top=.99,bottom=.01)
for ext in ('png','svg'):fig.savefig(FIGURES/f'fitted_process.{ext}',dpi=240,facecolor='white')
plt.close(fig)
if args.process_only:
    print('Saved English process figure; empirical plot unchanged.')
    raise SystemExit(0)

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
