"""Evaluate two-marker apparent yaw against held-out robot poses (USDA DS1)."""
import argparse,csv
from pathlib import Path
import numpy as np
import cv2 as cv
from scipy.spatial.transform import Rotation as Rot
from scipy.optimize import least_squares
def write(name,rows):
    with (Path(__file__).resolve().parent/name).open('w',newline='') as f:
        out=csv.DictWriter(f,fieldnames=list(rows[0]));out.writeheader();out.writerows(rows)
def angle(v):
    return np.arctan2(v[...,1],v[...,0])
def wrap(x):
    return (x+np.pi/2)%np.pi-np.pi/2
def run(dataset):
    cv.setNumThreads(1)
    geometry=np.array([[x,y,0] for y in range(6) for x in range(8)],dtype=np.float32)*28.5
    ids=[];grids=[]
    for path in sorted((dataset/'images'/'camera0').glob('*.png'),key=lambda p:int(p.stem[5:])):
        i=int(path.stem[5:]); im=cv.imread(str(path),0)
        ok,g=cv.findChessboardCorners(im,(8,6),cv.CALIB_CB_ADAPTIVE_THRESH|cv.CALIB_CB_NORMALIZE_IMAGE)
        if not ok:continue
        g=cv.cornerSubPix(im,g,(4,4),(-1,-1),(3,30,.001)).reshape(6,8,2)
        if g[2,-1,1]<g[2,0,1]:g=g[::-1,::-1]
        grids.append(g.copy());ids.append(i)
    ids=np.asarray(ids);grids=np.array(grids)
    train=~np.isin(ids//8,[2,5,8,10]);test=~train
    flat=grids.reshape(len(ids),-1,1,2)
    rms,K,d,_,_=cv.calibrateCamera([geometry]*int(train.sum()),list(flat[train]),(640,480),None,None,flags=cv.CALIB_FIX_K3)
    robot=np.loadtxt(dataset/'robot_cali.txt',skiprows=1).reshape(-1,4,4)[ids]
    vectors=[];offsets=[]
    for view in flat[train]:
        ok,v,t=cv.solvePnP(geometry,view,K,d);assert ok
        vectors.append(v[:,0]); offsets.append(t[:,0])
    C=Rot.from_rotvec(vectors);off=np.array(offsets)
    candidates=[]
    for inv in [False,True]:
        poses=np.linalg.inv(robot) if inv else robot
        rr=Rot.from_matrix(poses[:,:3,:3]);t=poses[:,:3,3]
        def residual(x):
            return ((Rot.from_rotvec(x[:3])*rr[train]*Rot.from_rotvec(x[3:])).inv()*C).as_rotvec().ravel()
        guesses=[np.zeros(3),np.array([.4,1.2,-2]),np.array([-1,.5,1.6])]
        rotations=[]
        for guess in guesses:
            x0=np.r_[guess,(rr[train][0].inv()*Rot.from_rotvec(guess).inv()*C[0]).as_rotvec()]
            rotations.append(least_squares(residual,x0,max_nfev=100))
        sol=min(rotations,key=lambda r:r.cost).x
        ra,rb=Rot.from_rotvec(sol[:3]),Rot.from_rotvec(sol[3:]);M=(ra*rr[train]).as_matrix()
        lhs=np.concatenate((np.broadcast_to(np.eye(3),M.shape),M),axis=2).reshape(-1,6)
        translations=np.linalg.lstsq(lhs,(off-ra.apply(t[train])).ravel(),rcond=None)[0]
        x0=np.r_[sol,translations]
        def project(x,r,t):
            a,b=Rot.from_rotvec(x[:3]),Rot.from_rotvec(x[3:6])
            r2=(a*r*b).as_rotvec();t2=x[6:9]+a.apply(t+r.apply(x[9:12]))
            return np.array([cv.projectPoints(geometry.astype(float),z,u,K,d)[0][:,0,:] for z,u in zip(r2,t2)])
        def pixel(x):
            return (project(x,rr[train],t[train])-flat[train][:,:,0,:]).ravel()
        res=least_squares(pixel,x0,x_scale='jac',max_nfev=100)
        candidates.append((res.cost,inv,project(res.x,rr,t)))
    cost,inv,proj=min(candidates,key=lambda z:z[0]);proj=proj.reshape(-1,6,8,2)
    geomerr=np.linalg.norm(proj-grids,axis=3)
    metrics=[];frames=[]
    for length,left,right in [(1,3,4),(3,2,5),(7,0,7)]:
        yy=angle(proj[:,2,right]-proj[:,2,left])
        o=angle(grids[:,2,right]-grids[:,2,left])
        center=.5*np.angle(np.exp(2j*yy[train]).mean())
        R=np.mean(wrap(o[train]-yy[train])**2);V=np.mean(wrap(yy[train]-center)**2)
        alpha=np.clip(np.sum(wrap(yy[train]-center)*wrap(o[train]-center))/np.sum(wrap(o[train]-center)**2),0,1)
        consecutive=train[1:]&train[:-1]&(np.diff(ids)==1)
        p=wrap(yy[:-1]-center)[consecutive];n=wrap(yy[1:]-center)[consecutive]
        phi=np.clip(np.sum(p*n)/np.sum(p*p),0,.995)
        for method in ('raw','static','trained','assume_095'):
            est=[];last=None;value=center;cov=V
            for i in np.where(test)[0]:
                if method=='raw':v=o[i]
                elif method=='static':v=center+alpha*wrap(o[i]-center)
                else:
                    f=phi if method=='trained' else .95
                    fresh=last is None or ids[i]!=last+1
                    prior=center if fresh else center+f*wrap(value-center)
                    P=V if fresh else f*f*cov+(1-f*f)*V
                    gain=P/(P+R);v=prior+gain*wrap(o[i]-prior);cov=(1-gain)*P;value=v
                last=ids[i];e=np.degrees(wrap(v-yy[i]));est.append(e)
                frames.append(dict(frame=int(ids[i]),cells=length,method=method,residual_deg=e))
            metrics.append(dict(cells=length,method=method,n_train=int(train.sum()),n_test=int(test.sum()),training_alpha=alpha,
                training_phi=phi,axis_mae_deg=np.mean(np.abs(est)),axis_p90_deg=np.quantile(np.abs(est),.9),
                orientation_inverted=inv,intrinsic_train_rms_px=rms,pose_train_rms_px=np.sqrt(np.mean(geomerr[train]**2)),
                pose_test_rms_px=np.sqrt(np.mean(geomerr[test]**2))))
    write('robot_bench_summary.csv',metrics);write('robot_bench_errors.csv',frames)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('ds1',type=Path);run(p.parse_args().ds1)
