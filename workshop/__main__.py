"""python -m workshop {all,experiments,plots,animations,presentation,verify}."""
import argparse
from pathlib import Path
from workshop.experiments import run_experiments, animation_runs


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['all','experiments','plots','animations','presentation','verify'])
    parser.add_argument('--output-dir',type=Path,default=Path('results/workshop'))
    parser.add_argument('--presentation-dir',type=Path,default=Path('presentation'))
    parser.add_argument('--runs',type=int,default=30)
    parser.add_argument('--agents',type=int,default=30)
    parser.add_argument('--iterations',type=int,default=100)
    args=parser.parse_args();root=args.output_dir
    if args.stage in ['all','experiments']:
        run_experiments(root,args.runs,args.agents,args.iterations);animation_runs(root)
    if args.stage in ['all','plots']:
        from workshop.visuals import plot_statistics,plot_snapshots
        plot_statistics(root);plot_snapshots(root)
    if args.stage in ['all','animations']:
        from workshop.visuals import export_animations
        export_animations(root)
    if args.stage in ['all','presentation']:
        from workshop.presentation import build_presentation
        build_presentation(root,args.presentation_dir)
    if args.stage in ['all','verify']:
        from workshop.verify import verify_deliverables
        verify_deliverables(root,args.presentation_dir)


if __name__=='__main__':main()
