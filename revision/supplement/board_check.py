"""Measured two-fiducial angular residuals on photographed OpenCV boards."""
import argparse
import csv
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen
import numpy as np

HERE = Path(__file__).resolve().parent
COMMIT = "49486f61fb25722cbcf586b7f4320921d46fb38e"
IMAGES = [f"left{i:02}.jpg" for i in [1,2,3,4,5,6,7,8,9,11,12,13,14]]


def write(file, rows):
    with (HERE/file).open('w',newline='') as out:
        w=csv.DictWriter(out,fieldnames=rows[0]); w.writeheader();w.writerows(rows)


def extract(directory):
    import cv2
    directory.mkdir(parents=True,exist_ok=True)
    def load(name):
        path=directory/name
        if not path.exists():
            url=f"https://raw.githubusercontent.com/opencv/opencv/{COMMIT}/samples/data/{name}"
            path.write_bytes(urlopen(url,timeout=30).read())
        data=path.read_bytes()
        image=cv2.imdecode(np.frombuffer(data,np.uint8),cv2.IMREAD_GRAYSCALE)
        ok, corners=cv2.findChessboardCorners(image,(9,6))
        if not ok:
            raise RuntimeError(f'Board not detected in {name}')
        corners=cv2.cornerSubPix(image,corners,(11,11),(-1,-1),(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_MAX_ITER,30,.001))
        return [dict(image=name,sha256=hashlib.sha256(data).hexdigest(),column=i%9,row=i//9,
                image_x=x,image_y=y) for i,(x,y) in enumerate(corners[:,0,:])]
    with ThreadPoolExecutor(4) as workers:
        rows=[r for group in workers.map(load,IMAGES) for r in group]
    write('board_corners.csv',rows)


def rectify(image_points, controls, board_points):
    # Map pixels to board coordinates using two disjoint outer rows, no held-out middle row.
    u,v=image_points[controls].T
    x,y=board_points[controls].T
    ones=np.ones(len(u)); zeros=np.zeros((len(u),3)); uv=np.column_stack((u,v,ones))
    a=np.vstack((np.column_stack((uv,zeros,-x[:,None]*uv[:,:2])),
                 np.column_stack((zeros,uv,-y[:,None]*uv[:,:2]))))
    h=np.r_[np.linalg.lstsq(a,np.r_[x,y],rcond=None)[0],1].reshape(3,3)
    homogeneous=np.c_[image_points,np.ones(len(image_points))] @ h.T
    return homogeneous[:,:2]/homogeneous[:,2:]


def main():
    args=argparse.ArgumentParser()
    args.add_argument('--extract',type=Path,help='Download/check the pinned photographs and repeat OpenCV 4.12 extraction.')
    par=args.parse_args()
    if par.extract:extract(par.extract)
    with (HERE/'board_corners.csv').open() as stream: data=list(csv.DictReader(stream))
    rows=[]
    for image in IMAGES:
        obs=[r for r in data if r['image']==image]
        assert len(obs)==54
        uv=np.array([[float(r['image_x']),float(r['image_y'])] for r in obs])
        xy=np.array([[int(r['column']),int(r['row'])] for r in obs])
        mapped=rectify(uv,np.isin(xy[:,1],[0,5]),xy)
        for row in (2,3):
            for a,b in ((3,5),(2,6),(0,8)):
                i,j=row*9+a,row*9+b
                dx,dy=mapped[j]-mapped[i]
                theta=np.arctan2(dy,dx)
                rot=np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
                center=(mapped[i]+mapped[j])/2
                target_mask=np.isin(xy[:,1],[1,4])
                nominal=xy[target_mask]-[4,row]
                truth=mapped[target_mask]
                obs_error=np.linalg.norm(center+nominal@rot.T-truth,axis=1)
                rows.append(dict(image=image,board_row=row,left=a,right=b,span_squares=b-a,
                                 angle_deg=np.degrees(theta),targets=len(obs_error),
                                 target_rms_squares=np.sqrt(np.mean(obs_error**2))))
    write('board_spans.csv',rows)
    for b in (2,4,8):
        y=np.array([r['angle_deg'] for r in rows if r['span_squares']==b])
        z=np.array([r['target_rms_squares'] for r in rows if r['span_squares']==b])
        print(b,len(y),np.median(np.abs(y)),np.sqrt(np.mean(y**2)),np.sqrt(np.mean(z**2)))


if __name__=='__main__':
    main()
