"""Slide-ready statistical plots, faithful GOA frame exports and animations."""
import json
import os
import shutil
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/goa-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter
import numpy as np
from workshop.experiments import FUNCTIONS, ALGORITHMS, save_json

COLORS = {'goa':'#087e8b','ga':'#d76a18','rls':'#8053a6'}
EPSILON = 1e-16
plt.rcParams.update({'font.size':12, 'axes.spines.top':False, 'axes.spines.right':False,
                     'svg.fonttype':'none', 'savefig.facecolor':'white'})


def export(fig, path):
    path = Path(path)
    fig.savefig(path.with_suffix('.png'), dpi=320, bbox_inches='tight')
    fig.savefig(path.with_suffix('.svg'), bbox_inches='tight')
    plt.close(fig)


def plot_statistics(root=Path('results/workshop')):
    root=Path(root); folder=root/'plots';folder.mkdir(exist_ok=True)
    records=json.loads((root/'runs.json').read_text()); summary=json.loads((root/'summary.json').read_text())
    config=json.loads((root/'config.json').read_text()); n=config['runs_per_algorithm_function']
    for name in FUNCTIONS:
        groups={a:[r for r in records if r['function']==name and r['algorithm']==a] for a in ALGORITHMS}
        curves={a:np.array([r['convergence_history'] for r in group]) for a,group in groups.items()}
        for kind in ['mean','median','gap','evaluations','population_mean']:
            fig,ax=plt.subplots(figsize=(10,5.4))
            for a,values in curves.items():
                if kind=='population_mean':
                    values=np.array([r['population_mean_history'] for r in groups[a]])
                if kind=='gap':
                    values=values-0.  # known optimum; raw values untouched
                mid=np.median(values,axis=0) if kind=='median' else values.mean(axis=0)
                x=np.array(groups[a][0]['evaluation_history']) if kind=='evaluations' else np.arange(len(mid))
                ax.plot(x,np.maximum(mid,EPSILON),color=COLORS[a],lw=2.3,label=a.upper())
                if kind!='median':
                    sd=values.std(axis=0,ddof=1) if len(values)>1 else np.zeros_like(mid)
                    ax.fill_between(x,np.maximum(mid-sd,EPSILON),np.maximum(mid+sd,EPSILON),color=COLORS[a],alpha=.16)
            descriptions={'mean':'Mean best-so-far ± sample SD', 'median':'Median best-so-far',
                          'gap':'Mean optimality gap ± sample SD (f* = 0)',
                          'evaluations':'Mean best-so-far ± sample SD / actual evaluations',
                          'population_mean':'Mean population fitness, then averaged across runs ± SD'}
            ax.set(title=f'{name.title()} · {descriptions[kind]}',
                   xlabel='Actual scalar objective evaluations (initial 30 included)' if kind=='evaluations' else 'Iteration (0 = initial state)',
                   ylabel='Objective fitness (dimensionless)' if kind!='gap' else 'Best-so-far − known f* (dimensionless)')
            ax.set_yscale('log');ax.grid(alpha=.2,which='both');ax.legend(loc='best')
            fig.text(.5,.012,f'{n} independent runs per method · display floor ε = 1e−16 only · SD is variability, not a confidence interval',ha='center',fontsize=10)
            fig.tight_layout(rect=[0,.04,1,1]);export(fig,folder/f'{name}_{kind}')
        fig,ax=plt.subplots(figsize=(8.5,5.4))
        samples=[np.array([r['final_best_fitness'] for r in groups[a]]) for a in ALGORITHMS]
        ax.boxplot([np.maximum(s,EPSILON) for s in samples],tick_labels=[a.upper() for a in ALGORITHMS],showmeans=True,
                   medianprops=dict(color='black',linewidth=2),meanprops=dict(marker='D',markerfacecolor='white',markeredgecolor='black'))
        for i,(a,s) in enumerate(zip(ALGORITHMS,samples),1):
            ax.scatter(np.linspace(i-.17,i+.17,len(s)),np.maximum(s,EPSILON),s=18,alpha=.55,color=COLORS[a],label=a.upper())
        ax.set(title=f'{name.title()} · final best fitness across all {n} runs',xlabel='Algorithm',ylabel='Final best fitness (dimensionless; lower is better)')
        ax.set_yscale('log');ax.grid(axis='y',alpha=.2);ax.legend()
        fig.text(.5,.012,'Box = Q1–Q3 · line = median · diamond = mean · whiskers = 1.5 IQR · dots = every run · ε = 1e−16 display only',ha='center',fontsize=9)
        fig.tight_layout(rect=[0,.04,1,1]);export(fig,folder/f'{name}_boxplot')
        rows=[r for r in summary if r['function']==name]
        fig,ax=plt.subplots(figsize=(13,3.2));ax.axis('off')
        data=[[r['algorithm'].upper(), *[f"{r[k]:.3e}" for k in ['mean','median','sd','best','worst']],
               f"{r['runtime_mean_s']:.4f}",str(r['evaluations_min'])] for r in rows]
        table=ax.table(cellText=data,colLabels=['Method','Mean','Median','Sample SD','Best','Worst','Mean time (s)','Calls'],loc='center',cellLoc='center')
        table.auto_set_font_size(False);table.set_fontsize(12);table.scale(1,2.3)
        ax.set_title(f'{name.title()} · final fitness summary ({n} runs/method)',fontsize=17,pad=15)
        fig.text(.5,.02,'All fitness values dimensionless. Time excludes plotting/export; includes trace storage. Actual evaluations are equal.',ha='center',fontsize=10)
        export(fig,folder/f'{name}_table')
    plot_slide_statistics(root)
    print('Statistical PNG/SVG exports complete',flush=True)


def background(ax, func, bounds, optimum, zoom=False):
    if zoom:
        limits=((-0.8,.8),(-0.8,.8)) if optimum==[0.,0.] else ((.6,1.4),(.4,1.6))
    else:
        limits=((bounds[0],bounds[1]),(bounds[0],bounds[1]))
    x=np.linspace(*limits[0],220);y=np.linspace(*limits[1],220);X,Y=np.meshgrid(x,y)
    # Vectorized contour formulas are the same 2D objective definitions.
    Z=X**2+Y**2 if optimum==[0.,0.] else 100*(Y-X**2)**2+(X-1)**2
    color=np.log10(1+Z) if optimum==[1.,1.] else Z
    ax.contourf(X,Y,color,levels=28,cmap='Blues',alpha=.65)
    if optimum==[1.,1.]:
        xx=np.linspace(*limits[0],300)
        ax.plot(xx,xx**2,color='#697784',lw=1,alpha=.5)
    ax.scatter(*optimum,s=180,marker='*',color='#169448',edgecolor='#075325',zorder=7,label='Known optimum')
    ax.set(xlim=limits[0],ylim=limits[1],xlabel='x₁',ylabel='x₂')
    ax.grid(alpha=.15)
    return limits


def frame_on_axis(ax, name, trace, iteration, seed, zoom=False):
    function,bounds,optimum=FUNCTIONS[name]
    limits=background(ax,function,bounds,optimum,zoom)
    points=trace['positions'][iteration];best=trace['best_positions'][iteration]
    ax.scatter(points[:,0],points[:,1],s=35,c='#db414a',edgecolor='white',lw=.4,zorder=5,label='Current agents')
    ax.scatter(*best,s=120,marker='D',facecolor='none',edgecolor='#dc9600',linewidth=2,zorder=8,label='Best-so-far')
    inside=np.sum((points[:,0]>=limits[0][0])&(points[:,0]<=limits[0][1])&(points[:,1]>=limits[1][0])&(points[:,1]<=limits[1][1]))
    title=f"Iteration {iteration} · best = {trace['best_fitness'][iteration]:.3e}"
    if zoom:title+=f'\nFixed zoom: {inside}/{len(points)} agents visible'
    ax.set_title(title,fontsize=12)
    return limits


def plot_snapshots(root=Path('results/workshop')):
    root=Path(root);folder=root/'snapshots';folder.mkdir(exist_ok=True)
    for name in FUNCTIONS:
        record=json.loads((root/'examples'/f'{name}_goa_00.json').read_text())
        trace=np.load(root/record['trace_file']); last=record['iterations']
        frames=sorted(set([0,last//4,last//2,3*last//4,last]))
        for t in frames:
            fig,axes=plt.subplots(1,2,figsize=(11,4.5))
            for ax,zoom in zip(axes,[False,True]):frame_on_axis(ax,name,trace,t,record['seed'],zoom)
            axes[0].legend(loc='upper right',fontsize=9)
            fig.suptitle(f"GOA · {name.title()} · preselected seed {record['seed']} (single run)")
            fig.text(.5,.01,'Contour color = '+('log10(1 + f); thin line y = x₁²' if name=='rosenbrock' else 'raw f')+' · archive may differ from current population',ha='center',fontsize=10)
            fig.tight_layout(rect=[0,.035,1,.95]);export(fig,folder/f'{name}_iter{t:03d}')
        for chosen,suffix in [(frames,'all'),([0,last//2,last],'slide')]:
            fig,axes=plt.subplots(1,len(chosen),figsize=(4.3*len(chosen),4.1))
            for ax,t in zip(axes,chosen):frame_on_axis(ax,name,trace,t,record['seed'])
            if suffix == 'slide':
                for ax,t in zip(axes,chosen):
                    ax.set_title(f"Iteration {t}\nBest = {trace['best_fitness'][t]:.3e}", fontsize=18)
                    ax.set_xlabel('x₁',fontsize=19);ax.set_ylabel('x₂',fontsize=19)
                    ax.tick_params(labelsize=16)
            handles,labels=axes[0].get_legend_handles_labels()
            fig.legend(handles,labels,loc='lower center',ncol=3,fontsize=18 if suffix=='slide' else 11)
            color_label = 'log10(1 + f)' if name=='rosenbrock' else 'raw f'
            fig.suptitle(f"GOA · {name.title()} · seed {record['seed']} · single run · color: {color_label}",fontsize=16)
            fig.tight_layout(rect=[0,.09,1,.93]);export(fig,folder/f'{name}_{suffix}')
    print('Snapshots PNG/SVG complete',flush=True)


def export_animations(root=Path('results/workshop')):
    root=Path(root);folder=root/'animations';folder.mkdir(exist_ok=True);manifest=[]
    for name in FUNCTIONS:
        record=json.loads((root/'examples'/f'{name}_goa_00.json').read_text())
        trace=np.load(root/record['trace_file'])
        fig,axes=plt.subplots(1,2,figsize=(12,5.3)); scatters=[];bests=[];limits=[]
        for ax,zoom in zip(axes,[False,True]):
            limits.append(background(ax,*FUNCTIONS[name],zoom))
            scatters.append(ax.scatter([],[],s=40,c='#db414a',edgecolor='white',lw=.5,label='Current agents',zorder=5))
            bests.append(ax.scatter([],[],s=140,marker='D',facecolor='none',edgecolor='#dc9600',lw=2,label='Best-so-far',zorder=8))
        axes[0].legend(fontsize=10)
        fig.suptitle(f"GOA · {name.title()} · preselected seed {record['seed']} · single run")
        fig.text(.5,.01,'Contour color = '+('log10(1 + f); thin line y = x₁²' if name=='rosenbrock' else 'raw f')+' · red swarm clustering is not proof of optimality',ha='center',fontsize=10)
        fig.tight_layout(rect=[0,.045,1,.95])
        def update(t):
            points=trace['positions'][t];best=trace['best_positions'][t]
            for i,ax in enumerate(axes):
                scatters[i].set_offsets(points);bests[i].set_offsets([best])
                lo=limits[i]
                inside=np.sum((points[:,0]>=lo[0][0])&(points[:,0]<=lo[0][1])&(points[:,1]>=lo[1][0])&(points[:,1]<=lo[1][1]))
                ax.set_title(f"Iteration {t}/{record['iterations']} · best = {trace['best_fitness'][t]:.3e}"+('' if i==0 else f'\nFixed zoom: {inside}/{len(points)} agents visible'),fontsize=12)
            return scatters+bests
        animation=FuncAnimation(fig,update,frames=record['iterations']+1,interval=160,blit=False)
        animation.save(folder/f'{name}_goa.gif',writer=PillowWriter(fps=6),dpi=85)
        status=dict(function=name,seed=record['seed'],frames=record['iterations']+1,gif=f'animations/{name}_goa.gif',fps=6)
        if shutil.which('ffmpeg'):
            try:
                animation.save(folder/f'{name}_goa.mp4',writer=FFMpegWriter(fps=6,codec='libx264',extra_args=['-pix_fmt','yuv420p','-crf','20']),dpi=120)
                status['mp4']=f'animations/{name}_goa.mp4'
            except (RuntimeError,OSError) as error: status['mp4_error']=str(error)
        else:status['mp4_error']='ffmpeg is not installed; use GIF'
        plt.close(fig);manifest.append(status);print(f'{name}: GIF/MP4 export complete',flush=True)
    save_json(folder/'manifest.json',manifest)


def plot_slide_statistics(root=Path("results/workshop")):
    """Compact charts with readable labels at the deck panel size."""
    root=Path(root);records=json.loads((root/'runs.json').read_text())
    for name,kind in [('sphere','mean'),('rosenbrock','gap'),('sphere','median'),('rosenbrock','boxplot')]:
        fig,ax=plt.subplots(figsize=(6.0,4.65))
        groups={a:[r for r in records if r['function']==name and r['algorithm']==a] for a in COLORS}
        if kind=='boxplot':
            samples=[np.array([r['final_best_fitness'] for r in group]) for group in groups.values()]
            ax.boxplot([np.maximum(s,EPSILON) for s in samples],tick_labels=[a.upper() for a in groups],showmeans=True,meanprops=dict(marker='D',markerfacecolor='white',markeredgecolor='black'))
            for i,(a,s) in enumerate(zip(groups,samples),1):ax.scatter(np.linspace(i-.16,i+.16,len(s)),np.maximum(s,EPSILON),s=16,color=COLORS[a],alpha=.55)
            title='Rosenbrock: all 30 final outcomes';ylabel='Final best fitness';xlabel='Algorithm'
        else:
            for a,g in groups.items():
                values=np.array([r['convergence_history'] for r in g]);mid=np.median(values,axis=0) if kind=='median' else values.mean(axis=0)
                x=np.arange(len(mid));ax.plot(x,np.maximum(mid,EPSILON),color=COLORS[a],lw=2,label=a.upper())
                if kind!='median':
                    sd=values.std(axis=0,ddof=1);ax.fill_between(x,np.maximum(mid-sd,EPSILON),np.maximum(mid+sd,EPSILON),color=COLORS[a],alpha=.16)
            title=f"{name.title()}: "+('median best-so-far' if kind=='median' else 'mean ± sample SD');ylabel='Optimality gap' if kind=='gap' else 'Best-so-far fitness';xlabel='Iteration'
            ax.legend(fontsize=16,framealpha=.95)
        ax.set_title(title,fontsize=17,pad=10);ax.set_xlabel(xlabel,fontsize=18);ax.set_ylabel(ylabel,fontsize=18)
        ax.tick_params(labelsize=15);ax.set_yscale('log');ax.grid(alpha=.2,which='both');fig.tight_layout()
        export(fig,root/'plots'/f'{name}_{kind}_slide')
