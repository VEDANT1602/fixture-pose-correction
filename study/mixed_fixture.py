"""Compare heading estimators with independent calibration and disjoint test runs."""
import csv
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
TARGETS=np.array([[-36.,0],[0,16.],[36.,0]])
TOL=np.array([1.30,1.60,.90])
SD=np.radians(4/np.sqrt(3))
def rotate(points,angles):
    co,si=np.cos(angles)[...,None],np.sin(angles)[...,None]
    x,y=points.T
    return np.stack((co*x-si*y,si*x+co*y),axis=-1)
def fixtures(seed,name,nruns=120,length=96):
    rng=np.random.default_rng(seed)
    y=np.empty((nruns,length));y[:,0]=rng.normal(0,SD,nruns)
    switches=rng.integers(0,2,nruns,dtype=bool)
    for k in range(1,length):
        if name=='iid': phi=0.
        elif name=='drift': phi=.9
        else:
            switches ^= rng.random(nruns)<.12
            phi=np.where(switches,.9,0)
        z=rng.standard_t(5,nruns)*np.sqrt(3/5) if name=='mixed-t' else rng.normal(size=nruns)
        y[:,k]=phi*y[:,k-1]+SD*np.sqrt(1-phi**2)*z
    shape=y.shape
    trans=rng.uniform(-4.5,4.5,(*shape,2))
    noise=rng.normal(size=(*shape,2,2));again=rng.normal(size=(*shape,2,2))
    track=rng.normal(0,.12,(*shape,3,2));rec=rng.normal(0,.27,(*shape,3,2))
    return y,trans,noise,again,track,rec
def measure(f,span,noise,dup=False):
    yy,trans,z,zz,*_=f
    obs=rotate(np.array([[-span/2,0.],[span/2,0.]]),yy)+trans[...,None,:]+noise*(zz if dup else z)
    v=obs[...,1,:]-obs[...,0,:]
    return np.arctan2(v[...,1],v[...,0]),obs.mean(axis=-2)
def calib(f,span):
    a,_=measure(f,span,.45);b,_=measure(f,span,.45,True)
    R=np.mean((a-b)**2)/2
    V=max(1e-7,np.mean(((a+b)/2)**2)-R/2)
    phi=np.clip(np.mean(a[:,1:]*b[:,:-1])/V,0,.995)
    return V,R,phi
def filterseq(y,V,R,phi):
    out=np.empty_like(y);state=0.;p=V
    for i in range(y.shape[1]):
        pred=V if i==0 else phi**2*p+(1-phi**2)*V
        w=pred/(pred+R)
        state=phi*state+w*(y[:,i]-phi*state);p=(1-w)*pred;out[:,i]=state
    return out
def finish(moves,err,rec,stage,speed,deadline):
    shape=err.shape[:-1];active=np.ones(shape,bool);used=np.zeros(shape,bool);elapsed=np.full(shape,.10)
    for i,tol in enumerate(TOL):
        elapsed[active]+=stage+.06+moves[...,i][active]/speed
        active&=elapsed<=deadline
        miss=active&(err[...,i]>tol);retry=miss&~used&(elapsed+.36<=deadline)
        elapsed[retry]+=.36;used|=retry;active[miss]=False;active[retry]=rec[...,i][retry]<=tol
    return active
def write(name,rows):
    with (HERE/name).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def main():
    training=fixtures(19051,'mixed',80)
    scores=[];times=[]
    for span in (12,36,72):
        V,R,fit=calib(training,span)
        for k,name in enumerate(('iid','drift','mixed','mixed-t')):
            f=fixtures(29111+k,name);yy,trans,_,_,track,rec=f
            true=rotate(TARGETS,yy)+trans[...,None,:]
            for noise in (.25,.45,.70):
                obs,mid=measure(f,span,noise)
                methods={'raw':obs}
                for label,phi in [('static',0.),('trained',fit),('assume_050',.50),('assume_080',.8),('assume_095',.95)]:
                    methods[label]=filterseq(obs,V,R,phi)
                base=None
                for method,theta in methods.items():
                    planned=rotate(TARGETS,theta)+mid[...,None,:]
                    radial=np.linalg.norm(planned-true,axis=-1)
                    per_run=radial[...,2].mean(axis=1)
                    if method=='raw': base=per_run
                    delta=per_run-base
                    scores.append(dict(regime=name,span_mm=span,sigma_test_mm=noise,method=method,phi_training=fit,
                         runs=len(yy),n=yy.size,yaw_mae_deg=np.degrees(np.mean(np.abs(theta-yy))),
                         target36_mae_mm=per_run.mean(),target36_p90_mm=np.quantile(radial[...,2],.9),
                         delta_to_raw_mm=delta.mean(),cluster_mc_se_mm=delta.std(ddof=1)/np.sqrt(len(yy))))
                    if noise!=.45 or span!=12: continue
                    stage_err=np.linalg.norm(planned+track-true,axis=-1)
                    recovery=np.linalg.norm(rec,axis=-1);dist=np.linalg.norm(planned-TARGETS,axis=-1)
                    for stage in (.25,.32,.40):
                        for speed in (40.,55.,70.):
                            for deadline in (1.6,1.85,2.1):
                                done=finish(dist,stage_err,recovery,stage,speed,deadline)
                                times.append(dict(regime=name,method=method,stage_s=stage,speed_mm_s=speed,deadline_s=deadline,n=yy.size,completed=int(done.sum())))
    write('fixture_results.csv',scores);write('timing_results.csv',times)
if __name__=='__main__':main()
