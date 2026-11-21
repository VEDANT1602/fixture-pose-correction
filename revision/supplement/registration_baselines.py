"""Paired model comparison with separate noise/prior calibration and serial clusters."""
from pathlib import Path
import csv
import numpy as np
from fixture_sensitivity import rotate, TARGETS, TOLS, save as write
HERE=Path(__file__).resolve().parent
TRAJECTORIES,LENGTH=100,100
V=np.radians(4/np.sqrt(3))**2


def markers(angles,translation,span,z):
    base=np.array([[-span/2,0],[span/2,0]])
    return rotate(base,angles)+translation[:,None,:]+z


def observed(y):
    delta=y[:,1]-y[:,0]
    return np.arctan2(delta[:,1],delta[:,0])


def svd_yaw(y,span):
    base=np.array([[-span/2,0],[span/2,0]])
    yc=y-y.mean(axis=1,keepdims=True)
    cov=np.einsum('ai,naj->nij',base,yc)
    u,_,vt=np.linalg.svd(cov)
    rotation=vt.transpose(0,2,1)@u.transpose(0,2,1)
    sign=np.sign(np.linalg.det(rotation))
    vt[:,-1,:]*=sign[:,None]
    rotation=vt.transpose(0,2,1)@u.transpose(0,2,1)
    return np.arctan2(rotation[:,1,0],rotation[:,0,0])


def train_variances(noise,span):
    rng=np.random.default_rng(33108)
    yaw=rng.normal(0,np.sqrt(V),600)
    t=rng.uniform(-4.5,4.5,(600,2))
    yz=[markers(yaw,t,span,rng.normal(0,noise,(600,2,2))) for _ in range(2)]
    # Duplicate images of each fixed pose: var(z1-z2)=2 sigma^2.
    s2=np.var(yz[0]-yz[1],ddof=1)/2
    R=2*s2/span**2
    means=(observed(yz[0])+observed(yz[1]))/2
    return R,max(1e-12,means.var(ddof=1)-R/2)


def filter_yaw(observations,prior,meas,phi):
    z=observations.reshape(TRAJECTORIES,LENGTH)
    out=np.empty_like(z); state=np.zeros(TRAJECTORIES);post=prior
    for k in range(LENGTH):
        pred=prior if k==0 else phi**2*post+(1-phi**2)*prior
        state=phi*state
        gain=pred/(pred+meas)
        state+=gain*(z[:,k]-state);post=(1-gain)*pred
        out[:,k]=state
    return out.ravel()


def complete(plan,true,tracking,recovery):
    n=len(true)
    time=np.full(n,.1);active=np.ones(n,dtype=bool);retry=np.zeros(n,dtype=bool)
    for k,tol in enumerate(TOLS):
        delta=np.linalg.norm(plan[:,k]-TARGETS[k],axis=1)
        time[active]+=.32+(.06+delta[active]/55.)*(delta[active]>1e-12)
        miss=np.linalg.norm(plan[:,k]+tracking[:,k]-true[:,k],axis=1)>tol
        attempt=active & miss & ~retry & (time+.36<=1.85)
        time[attempt]+=.36;retry|=attempt
        active &= (~miss | (attempt & (np.linalg.norm(recovery[:,k],axis=1)<=tol))) & (time<=1.85)
    return active


def main():
    summaries=[];clusters=[]
    for true_rho in [0.,.95]:
        rng=np.random.default_rng(515194)
        z=rng.normal(size=(TRAJECTORIES,LENGTH))
        yaw=z.copy()*np.sqrt(V)
        for k in range(1,LENGTH):
            yaw[:,k]=true_rho*yaw[:,k-1]+np.sqrt((1-true_rho**2)*V)*z[:,k]
        yaw=yaw.ravel()
        n=len(yaw);trans=rng.uniform(-4.5,4.5,(n,2))
        standard=rng.normal(size=(n,2,2))
        track=rng.normal(0,.12,(n,3,2));retry=rng.normal(0,.27,(n,3,2))
        actual=rotate(TARGETS,yaw)+trans[:,None]
        for noise in [.25,.45,.65]:
            for span in [12,36,72]:
                pts=markers(yaw,trans,span,standard*noise)
                mid=pts.mean(axis=1);obs=observed(pts);ls=svd_yaw(pts,span)
                diff=float(np.max(np.abs(obs-ls)));assert diff<1e-11
                R,v=train_variances(noise,span)
                fixed_prior=np.radians(2.)**2
                predictions={'translation':np.zeros(n),'rigid_ls':ls,
                             'fixed':obs*fixed_prior/(fixed_prior+2*.45**2/span**2),
                             'adaptive':obs*v/(v+R),'temporal_phi095':filter_yaw(obs,v,R,.95)}
                ref=complete(rotate(TARGETS,ls)+mid[:,None],actual,track,retry)
                for name,a in predictions.items():
                    scored=complete(rotate(TARGETS,a)+mid[:,None],actual,track,retry)
                    paired=(scored.astype(int)-ref.astype(int)).reshape(TRAJECTORIES,LENGTH)
                    by_trace=100*paired.mean(axis=1)
                    summaries.append(dict(true_rho=true_rho,true_noise=noise,span=span,method=name,
                       cycles=n,completions=int(scored.sum()),yaw_rmse_deg=np.degrees(np.sqrt(np.mean((a-yaw)**2))),
                       delta_pp=by_trace.mean(),cluster_se_pp=by_trace.std(ddof=1)/np.sqrt(TRAJECTORIES),
                       estimated_noise=np.sqrt(R*span**2/2),estimated_yaw_sd_deg=np.degrees(np.sqrt(v)),
                       procrustes_diff_rad=diff))
                    for k,delta in enumerate(by_trace):clusters.append(dict(true_rho=true_rho,true_noise=noise,span=span,
                          method=name,sequence=k,delta_pp=delta))
    write('baseline_comparison.csv',summaries);write('baseline_by_sequence.csv',clusters)


if __name__=='__main__':
    main()
