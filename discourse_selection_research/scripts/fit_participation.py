"""Fit post-entry participation decisions; never impute a silent-reader denominator."""
from pathlib import Path
from datetime import date,timedelta
import csv,json,math
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"
START=date(2024,12,18);DAYS=15

def dataset():
    raw=list(csv.DictReader((DATA/'comments_metadata.csv').open()))
    raw=[r for r in raw if r['source']=='lw_main']
    people=sorted({r['userId'] for r in raw})
    index={u:i for i,u in enumerate(people)}
    activity=np.zeros((len(people),DAYS),dtype=int)
    for r in raw:activity[index[r['userId']],(date.fromisoformat(r['postedAt'][:10])-START).days]=1
    first=np.argmax(activity,axis=1)
    rows=[]
    for i in range(len(people)):
        for t in range(first[i]+1,DAYS):rows.append((i,t,activity[i,t-1],activity[i,t]))
    return activity,first,np.array(rows,dtype=float)

def design(rows,kind):
    # Intercept, calendar day since release (negative sign), previous-day activity.
    cols=[np.ones(len(rows))]
    if kind in ('decay','feedback'):cols.append(-rows[:,1])
    if kind=='feedback':cols.append(rows[:,2])
    return np.column_stack(cols)

def logistic(z):return 1/(1+np.exp(-np.clip(z,-700,700)))

def fit(rows,kind):
    X=design(rows,kind);y=rows[:,3];b=np.zeros(X.shape[1]);b[0]=math.log((y.sum()+.5)/(len(y)-y.sum()+.5))
    def ll(beta):
        z=X@beta
        return float((y*z-np.logaddexp(0,z)).sum())
    for iteration in range(150):
        p=logistic(X@b);g=X.T@(y-p)
        info=X.T@((p*(1-p))[:,None]*X)
        step=np.linalg.solve(info+np.eye(len(b))*1e-10,g)
        rate=1.
        while rate>1e-9 and ll(b+rate*step)<ll(b)-1e-12:rate*=.5
        b+=rate*step
        if np.max(np.abs(rate*step))<1e-8:break
    p=logistic(X@b);info=X.T@((p*(1-p))[:,None]*X)
    cov=np.linalg.inv(info)
    return {'coefficients':b.tolist(),'standard_errors':np.sqrt(np.diag(cov)).tolist(),
            'log_likelihood':ll(b),'aic':2*len(b)-2*ll(b),'iterations':iteration+1,
            'max_score':float(np.max(np.abs(X.T@(y-p))))}

def predicted_daily(first,coefficients,kind):
    b=np.array(coefficients);n=len(first);prob=np.zeros(n);counts=[];return_counts=[]
    for t in range(DAYS):
        new=first==t;at_risk=first<t
        if kind=='constant':q=s=logistic(b[0])
        elif kind=='decay':q=s=logistic(b[0]-b[1]*t)
        else:q=logistic(b[0]-b[1]*t);s=logistic(b[0]-b[1]*t+b[2])
        prob=np.where(new,1,np.where(at_risk,(1-prob)*q+prob*s,0))
        counts.append(float(prob.sum()));return_counts.append(float(prob[at_risk].sum()))
    return counts,return_counts

def lopo(rows,kind):
    ll=0.;unstable=[]
    for user in sorted(set(rows[:,0])):
        train=rows[rows[:,0]!=user];test=rows[rows[:,0]==user]
        model=fit(train,kind);z=design(test,kind)@np.array(model['coefficients'])
        if max(map(abs,model['coefficients']))>20 or model['iterations']>=150:
            unstable.append(int(user))
        ll+=float((test[:,3]*z-np.logaddexp(0,z)).sum())
    return {'log_likelihood':ll,'unstable_folds':unstable}

if __name__=='__main__':
    activity,first,rows=dataset()
    fits={k:fit(rows,k) for k in ('constant','decay','feedback')}
    for kind,model in fits.items():
        validation=lopo(rows,kind)
        model['leave_one_account_out_log_likelihood']=validation['log_likelihood']
        model['unstable_holdout_folds']=validation['unstable_folds']
        model['expected_daily_active'],model['expected_daily_returning']=predicted_daily(first,model['coefficients'],kind)
    report={'topic':'LW alignment-faking release thread','start_utc':str(START),'end_exclusive_utc':str(START+timedelta(days=DAYS)),
        'comments':53,'accounts':len(first),'days':DAYS,'post_entry_account_days':len(rows),'positive_post_entry_days':int(rows[:,3].sum()),
        'daily_active_accounts':activity.sum(axis=0).tolist(),'daily_first_contributors':np.bincount(first,minlength=DAYS).tolist(),
        'daily_returning_accounts':(activity.sum(axis=0)-np.bincount(first,minlength=DAYS)).tolist(),
        'models':fits,
        'scope':'Likelihood conditions on each observed account first contributing on its observed date. Predicts only subsequent activity; does not estimate initial entry or silent-reader beliefs.',
        'caveat':'No causal interpretation of lag coefficient. Small return-event count; common time trend and unobserved account heterogeneity are alternatives to feedback.'}
    (DATA/'participation_model_fit.json').write_text(json.dumps(report,indent=2))
    with (DATA/'participation_transitions.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['account_index','days_since_release','active_previous_day','active_today']);w.writerows(rows.astype(int))
    print(json.dumps(report,indent=2))
