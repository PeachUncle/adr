#!/usr/bin/env python3
from pathlib import Path
import argparse,json,re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

DEFAULT_INPUT='your file.xlsx'
STAR_MODE='cumulative'  # annual: direct annual columns; cumulative: adjacent-year differences
LAST_COMPLETE_YEAR=2025
DATE_COLUMN='ADR_first_time'  # first observed Git appearance, NOT necessarily decision date
FONT_SIZE=13
TOPICS=[f'D{i:02}' for i in range(1,8)]+['D98']
QUALITIES=[f'Q{i:02}' for i in range(1,10)]+['Q99']

def save(fig,out,name):
    fig.tight_layout()
    fig.savefig(out/f'{name}.pdf',dpi=300,bbox_inches='tight')
    plt.close(fig)

def heat(m,title,out,name):
    fig,ax=plt.subplots(figsize=(12,max(4,len(m)*.65+2)))
    im=ax.imshow(m.to_numpy()*100,vmin=0,vmax=100,cmap='YlOrBr',aspect='auto')
    ax.set_xticks(range(len(m.columns)),m.columns);ax.set_yticks(range(len(m)),m.index)
    for i in range(len(m)):
        for j in range(len(m.columns)):
            v=m.iloc[i,j]*100
            ax.text(j,i,f'{v:.1f}',ha='center',va='center',color='white' if v>55 else '#222',fontsize=11)
    ax.set_title(title);fig.colorbar(im,ax=ax,label='Proportion (%)');save(fig,out,name)

def absorb(a,panel):
    z=pd.DataFrame(a,index=panel.index).astype(float)
    for _ in range(200):
        old=z.to_numpy().copy()
        z=z-z.groupby(panel['PROPOSED']).transform('mean')
        z=z-z.groupby(panel['year']).transform('mean')
        if np.max(np.abs(z.to_numpy()-old))<1e-9:break
    return z.to_numpy()

def run_base(input_path, out, star_mode=STAR_MODE, within=2):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'pdf.fonttype':42,'svg.fonttype':'none'})
    p=pd.read_excel(input_path,engine='openpyxl')
    required=['PROPOSED','ADR type','QA','repo_create_time',DATE_COLUMN]
    if set(required)-set(p):raise ValueError(f'Missing: {set(required)-set(p)}')
    p['PROPOSED']=p.PROPOSED.astype('string').str.strip()
    if p.PROPOSED.isna().any():raise ValueError('Missing repositories')
    yearcols=sorted([c for c in p.columns if re.fullmatch(r'20\d{2}',str(c))],key=lambda c:int(c))
    for c in ['repo_create_time',*yearcols]:
        if (p.groupby('PROPOSED')[c].nunique(dropna=False)>1).any():raise ValueError(f'Conflicting repository field {c}')
    repo=p.drop_duplicates('PROPOSED').copy();repo['created']=pd.to_datetime(repo.repo_create_time,errors='coerce',utc=True)
    if repo.created.isna().any():raise ValueError('Invalid repository creation dates')
    dates=pd.to_datetime(p[DATE_COLUMN],errors='coerce',utc=True)
    created=pd.to_datetime(p.repo_create_time,errors='coerce',utc=True)
    precreation=dates<created
    excluded_repos=set(p.loc[precreation,'PROPOSED'])
    invalid=dates.isna() | p.PROPOSED.isin(excluded_repos) | (dates>pd.Timestamp.now(tz='UTC'))
    repo=repo[~repo.PROPOSED.isin(excluded_repos)].copy()
    d=p.loc[~invalid].copy();d['year']=dates[~invalid].dt.year.astype(int)
    d=d[d.year<=LAST_COMPLETE_YEAR].copy()
    first=dates[~invalid].groupby(p.loc[~invalid,'PROPOSED']).min().dt.year
    raw=repo.set_index('PROPOSED')[yearcols].apply(pd.to_numeric,errors='coerce')
    if raw.isna().any().any() or (raw<0).any().any():raise ValueError('Missing/negative star input')
    diag={'repositories':len(repo),'nondecreasing_star_series':int((raw.diff(axis=1).iloc[:,1:]>=0).all(axis=1).sum()),
          'star_sum_matches_total':int(np.isclose(raw.sum(axis=1),pd.to_numeric(repo.set_index('PROPOSED').star,errors='coerce')).sum()) if 'star' in repo else None}
    # Preserve raw values. No use of the workbook star sum column.
    star=raw if star_mode=='annual' else raw.diff(axis=1)
    if star_mode=='cumulative':
        star.iloc[:,0]=np.nan
    star.columns=[int(c) for c in star.columns]
    panel=star.rename_axis('PROPOSED').reset_index().melt(id_vars='PROPOSED',var_name='year',value_name='annual_stars')
    panel['year']=panel.year.astype(int)
    panel=panel.merge(repo[['PROPOSED','created']],on='PROPOSED',validate='many_to_one')
    panel=panel[(panel.year>=panel.created.dt.year)&(panel.year<=LAST_COMPLETE_YEAR)].dropna(subset=['annual_stars']).copy()
    if (panel.annual_stars<0).any():raise ValueError('Negative differences: log model unsuitable; examine cumulative source.')
    counts=d.groupby(['PROPOSED','year']).size().rename('new_adrs').reset_index()
    panel=panel.merge(counts,on=['PROPOSED','year'],how='left').fillna({'new_adrs':0})
    panel['first_adr_year']=panel.PROPOSED.map(first)
    panel['relative_year']=panel.year-panel.first_adr_year
    panel['project_age']=panel.year-panel.created.dt.year
    panel=panel.sort_values(['PROPOSED','year']).reset_index(drop=True)
    # Balanced event window; all years must exist for each repository.
    e=panel[panel.relative_year.between(-within,within)].copy()
    valid=e.groupby('PROPOSED').relative_year.nunique();ids=valid[valid==2*within+1].index
    e=e[e.PROPOSED.isin(ids)]
    if len(e):
        z=e.groupby('relative_year').annual_stars.agg(median='median',n='size',q25=lambda x:x.quantile(.25),q75=lambda x:x.quantile(.75))
        fig,ax=plt.subplots(figsize=(8,5));xx=z.index.to_numpy(float)
        ax.plot(xx,z['median'],marker='o',color='#79502c');ax.fill_between(xx,z.q25,z.q75,color='#cba477',alpha=.3)
        ax.axvline(0,color='#777',linestyle='--');ax.set_xlabel('Years relative to first observed ADR')
        ax.set_ylabel('Annual stars' if star_mode=='annual' else 'Annual change in cumulative stars')
        ax.set_title(f'ADR introduction | balanced sample: {len(ids):,} repositories')
        save(fig,out,'adr_introduction_stars_trend')
    # Repository and calendar-year fixed effects, log-linear association, clustered by repository.
    panel['log_stars']=np.log1p(panel.annual_stars);panel['log_adrs']=np.log1p(panel.new_adrs)
    lag=panel.groupby('PROPOSED').log_adrs.shift(1)
    prevyear=panel.groupby('PROPOSED').year.shift(1)
    panel['lag_log_adrs']=lag.where(panel.year-prevyear==1)
    effects=[]
    for name,pred in [('Same-year ADR activity','log_adrs'),('Previous-year ADR activity','lag_log_adrs')]:
        z=panel.dropna(subset=[pred]).copy();n=z.groupby('PROPOSED').size();z=z[z.PROPOSED.isin(n[n>=2].index)]
        if len(z)==0:continue
        arr=absorb(z[['log_stars',pred]].to_numpy(),z)
        if np.std(arr[:,1])<1e-10:continue
        yy,xx=arr[:,0],arr[:,1]
        xx2=float(xx@xx);beta=float(xx@yy/xx2);resid=yy-beta*xx
        scores=pd.Series(xx*resid,index=z.index).groupby(z.PROPOSED).sum()
        g=len(scores);nn=len(z);k=g+z.year.nunique()
        correction=(g/(g-1))*((nn-1)/max(1,nn-k))
        se=float(np.sqrt(correction*(scores.to_numpy()**2).sum()/xx2**2))
        ci=[beta-1.96*se,beta+1.96*se]
        effects.append({'association':name,'coefficient':beta,'low':ci[0],'high':ci[1],
                        'repo_years':len(z),'repositories':z.PROPOSED.nunique()})
    ef=pd.DataFrame(effects)
    if len(ef):
        fig,ax=plt.subplots(figsize=(9,4));yy=np.arange(len(ef))
        ax.hlines(yy,ef.low,ef.high,color='#79502c');ax.scatter(ef.coefficient,yy,color='#79502c')
        ax.set_yticks(yy,ef.association);ax.axvline(0,color='#777',linestyle='--')
        ax.set_xlabel('Coefficient: log(1 + stars) vs log(1 + new ADRs)')
        ax.set_title('Repository and calendar-year effects; repository-clustered 95% CI')
        save(fig,out,'adr_stars_fixed_effect_associations')
    # Composition of new records by age, not revisions of the same decisions.
    d=d.merge(repo[['PROPOSED','created']],on='PROPOSED',validate='many_to_one')
    d['age']=d.year-d.created.dt.year
    d['age_band']=pd.cut(d.age,[-1,2,5,np.inf],labels=['Age 0–2 years','Age 3–5 years','Age 6+ years'])
    for q in QUALITIES:
        d[q]=d.QA.fillna('').astype(str).map(lambda s:int(q in re.findall(r'Q\d{2}',s)))
    for scope,sub,cols in [('topics',d[d['ADR type'].isin(TOPICS)],TOPICS),('quality',d,QUALITIES)]:
        x=sub.copy()
        if scope=='topics':
            for t in TOPICS:x[t]=(x['ADR type']==t).astype(int)
        for by,key in [('year','calendar_year'),('age_band','project_age')]:
            rp=x.groupby([by,'PROPOSED'],observed=True)[cols].mean()
            m=rp.groupby(level=0,observed=True).mean()
            sizes=x.groupby(by,observed=True).agg(adrs=('PROPOSED','size'),repositories=('PROPOSED','nunique'))
            heat(m,f'New ADR {scope} by {key.replace("_"," ")} | repository equal',out,f'{scope}_{key}_heatmap')
    diag.update({'star_mode':star_mode,'last_complete_year':LAST_COMPLETE_YEAR,'excluded_date_rows':int(invalid.sum()),
                 'precreation_commit_rows':int(precreation.sum()),'precreation_repositories_excluded':len(excluded_repos),
                 'dated_adrs_in_complete_years':len(d),'balanced_event_repositories':len(ids),
                 'date_column':DATE_COLUMN,'note':'Current retained ADR snapshot; deleted ADRs and prior text revisions are not recovered.'})
    print(json.dumps(diag,indent=2))
    return panel


# Extended RQ3 analyses, integrated into this script.
WINDOW_YEARS=5
PATTERNS=['Introduction-year only','Consecutive recording','Intermittent recording']
COLORS=['#c9b69c','#806344','#aaaeb5']
B={'B00':'General-purpose technology','B01':'Finance and insurance','B02':'Healthcare and health services','B03':'Education and training','B04':'Commerce and consumer services','B05':'Transportation and logistics','B06':'Government and public services','B07':'Industry and engineering','B08':'Agriculture, energy and environment','B09':'Real estate, accommodation and tourism','B10':'Media, content and entertainment','B11':'Research and professional services','B12':'Enterprise operations and collaboration','B98':'Other specialized contexts','B99':'Insufficient evidence'}
T={'T01':'Application software','T02':'System software','T03':'Web libraries and frameworks','T04':'Non-web libraries and frameworks','T05':'Software tools','T06':'Documentation','T99':'Insufficient evidence'}

def estimate(z,label):
    z=z.copy(); n=z.groupby('PROPOSED').size();z=z[z.PROPOSED.isin(n[n>=2].index)]
    if len(z)==0:return None
    z['x']=np.log1p(z.new_adrs);z['y']=np.log1p(z.annual_stars)
    arr=absorb(z[['y','x']].to_numpy(),z);y,x=arr.T;s=float(x@x)
    if s<1e-12:return None
    beta=float(x@y/s);r=y-beta*x
    scores=pd.Series(x*r,index=z.index).groupby(z.PROPOSED).sum();g=len(scores);nn=len(z);k=g+z.year.nunique()
    if g<2:return None
    se=np.sqrt(g/(g-1)*(nn-1)/max(1,nn-k)*float(scores@scores)/s**2)
    return dict(association=label,coefficient=beta,low=beta-1.96*se,high=beta+1.96*se,repositories=g,repo_years=nn)

def run_extended(input_path,out,panel,w):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':14,'pdf.fonttype':42,'svg.fonttype':'none'})
    p=pd.read_excel(input_path,engine='openpyxl');cols=['repo_busi_domain','repo_soft_domain']
    for c in cols:
        if p.groupby('PROPOSED')[c].nunique(dropna=False).gt(1).any():raise ValueError('Conflicting repository context: '+c)
    meta=p[['PROPOSED']+cols].drop_duplicates('PROPOSED');meta[cols]=meta[cols].fillna('NA')
    panel=panel.merge(meta,on='PROPOSED',validate='many_to_one')
    e=panel[panel.relative_year.between(0,w-1)].copy()
    n=e.groupby('PROPOSED').relative_year.nunique();ids=n[n==w].index;e=e[e.PROPOSED.isin(ids)]
    if e.empty:raise ValueError('No repositories with a complete observation window')
    rows=[]
    for repo,z in e.groupby('PROPOSED'):
        z=z.sort_values('relative_year');active=z.new_adrs.to_numpy()>0; years=np.flatnonzero(active)
        assert active[0] and len(z)==w
        pattern=PATTERNS[0] if len(years)==1 else PATTERNS[1] if np.all(np.diff(years)==1) else PATTERNS[2]
        runs=[];run=0
        for v in active:
            run=run+1 if v else 0;runs.append(run)
        rows.append(dict(PROPOSED=repo,pattern=pattern,active_years=len(years),longest_run=max(runs),last_active_relative_year=int(years[-1]),introduction_share=float(z.new_adrs.iloc[0]/z.new_adrs.sum()),window_adrs=int(z.new_adrs.sum()),first_adr_year=int(z.first_adr_year.iloc[0]),**{c:z[c].iloc[0] for c in cols}))
    r=pd.DataFrame(rows)
    summary=r.groupby('pattern').agg(repositories=('PROPOSED','size'),median_active_years=('active_years','median'),median_introduction_share=('introduction_share','median')).reindex(PATTERNS);summary['percent']=summary.repositories/len(r)*100
    per=e.assign(active=e.new_adrs.gt(0)).groupby('relative_year').agg(active=('active','sum'),repositories=('PROPOSED','size'));per['percent']=per.active/per.repositories*100
    fig,ax=plt.subplots(figsize=(8,5));ax.plot(per.index,per.percent,'o-',color=COLORS[1]);
    for x,v in per.percent.items():ax.annotate(f'{v:.1f}%',(x,v),xytext=(0,10),textcoords='offset points',ha='center')
    ax.set(xticks=range(w),ylim=(0,113),xlabel='Years since first observed ADR',ylabel='Repositories with new ADR records (%)',title=f'Fixed {w}-year window (n = {len(r):,} repositories)');save(fig,out,'adr_recording_persistence')
    fig,axes=plt.subplots(1,2,figsize=(19,10),gridspec_kw={'width_ratios':[1.2,1]})
    for ax,c,mapping,title in zip(axes,cols,[B,T],['Business domain','Software type']):
        ct=pd.crosstab(r[c],r.pattern).reindex(columns=PATTERNS,fill_value=0).sort_index();pct=ct.div(ct.sum(axis=1),axis=0)*100
        left=np.zeros(len(ct));yy=np.arange(len(ct))
        for pat,color in zip(PATTERNS,COLORS):
            v=pct[pat].to_numpy();ax.barh(yy,v,left=left,color=color,label=pat)
            for j,value in enumerate(v):
                if value>=10:ax.text(left[j]+value/2,j,f'{value:.0f}',ha='center',va='center',fontsize=11,color='white' if color==COLORS[1] else '#222')
            left+=v
        ax.set_yticks(yy,[f'{x} {mapping.get(x,x)} (n={ct.loc[x].sum()})' for x in ct.index]);ax.invert_yaxis();ax.set(xlim=(0,100),xlabel='Repositories (%)',title=title)
    handles,labels=axes[0].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=3,bbox_to_anchor=(.5,-.025));save(fig,out,'recording_patterns_by_context')
    post=panel[panel.relative_year.ge(0)].copy();follow=post[post.relative_year.gt(0)].groupby('PROPOSED').size();eligible=follow[follow>=2].index
    post=post[post.PROPOSED.isin(eligible)]
    effects=[estimate(post,'Including introduction year'),estimate(post[post.relative_year.gt(0)],'Excluding introduction year')]
    ef=pd.DataFrame([v for v in effects if v is not None])
    fig,ax=plt.subplots(figsize=(10,4));yy=np.arange(len(ef));ax.hlines(yy,ef.low,ef.high,color=COLORS[1]);ax.scatter(ef.coefficient,yy,color=COLORS[1]);ax.set_yticks(yy,ef.association);ax.axvline(0,color='#777',ls='--');ax.set(xlabel='Coefficient: log(1 + annual new stars) vs log(1 + new ADRs)',title='Repository and year fixed effects; clustered 95% CI');save(fig,out,'adr_stars_association_sensitivity')
    wr=[]
    for length in [3,5,7]:
        x=panel[panel.relative_year.between(0,length-1)];nn=x.groupby('PROPOSED').relative_year.nunique();x=x[x.PROPOSED.isin(nn[nn==length].index)]
        cnt={pat:0 for pat in PATTERNS}
        for _,z in x.groupby('PROPOSED'):
            yrs=z.loc[z.new_adrs.gt(0),'relative_year'].sort_values().to_numpy();pat=PATTERNS[0] if len(yrs)==1 else PATTERNS[1] if np.all(np.diff(yrs)==1) else PATTERNS[2];cnt[pat]+=1
        total=sum(cnt.values())
        for pat in PATTERNS:wr.append(dict(window_years=length,pattern=pat,repositories=cnt[pat],total=total,percent=100*cnt[pat]/total if total else np.nan))
    print(summary.to_string());print(per.to_string());print(ef.to_string(index=False));print('Output:',out.resolve())

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--input',type=Path,default=Path(__file__).resolve().parent/DEFAULT_INPUT)
    ap.add_argument('--output',type=Path)
    ap.add_argument('--star-mode',choices=['annual','cumulative'],default=STAR_MODE)
    ap.add_argument('--within',type=int,default=2,help='Event window in years')
    ap.add_argument('--window-years',type=int,default=WINDOW_YEARS)
    a=ap.parse_args()
    if a.window_years<2:raise ValueError('window-years must be at least 2')
    out=a.output or a.input.parent/'rq3_figures_v2'
    out.mkdir(parents=True,exist_ok=True)
    panel=run_base(a.input,out,a.star_mode,a.within)
    run_extended(a.input,out,panel,a.window_years)
    print('Generated PDFs:',len(list(out.glob('*.pdf'))))

if __name__=='__main__':
    main()
