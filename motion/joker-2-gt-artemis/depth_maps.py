"""Depth + normal maps for the 2.5D shoe meshes.

Model: Depth Anything V2 (small) ONNX from github.com/fabio-sim/Depth-Anything-ONNX (release v2.0.0),
saved as models/depth_anything_v2_vits.onnx. Uses the uploaded original photos as input.
"""
import onnxruntime as ort, numpy as np
from PIL import Image
from scipy import ndimage
s=ort.InferenceSession("models/depth_anything_v2_vits.onnx")
i=s.get_inputs()[0]; print(i.name,i.shape, [o.shape for o in s.get_outputs()])
U="/root/.claude/uploads/e2be165a-101f-506c-ac19-69f7f5ed6821/"
P="/home/user/JLM-marketing-system/motion/joker-2-gt-artemis/public/"
src={"lateral":("16023f6a",(188,626,1132,1070)),"medial":("4a084e58",(192,639,1167,1082)),"heels":("6a1cac0b",(257,592,1101,1095)),"sole":("4675dc8e",(157,669,1162,1077))}
for n,(k,bb) in src.items():
    cut=Image.open(P+f"shoe_{n}.png"); A=np.array(cut)[...,3]/255.
    im=Image.open(U+f"{k}-image.jpg").convert("RGB").crop(bb)
    # put shoe on neutral grey to help the model
    a=np.array(im).astype(np.float32); g=np.full_like(a,90.)
    comp=a*A[...,None]+g*(1-A[...,None])
    w,h=im.size; S=max(w,h); ox,oy=(S-w)//2,(S-h)//2
    sq=np.full((S,S,3),90.,np.float32); sq[oy:oy+h,ox:ox+w]=comp
    x=np.array(Image.fromarray(sq.astype(np.uint8)).resize((518,518),Image.BICUBIC)).astype(np.float32)/255.
    x=(x-[0.485,0.456,0.406])/[0.229,0.224,0.225]
    x=x.transpose(2,0,1)[None].astype(np.float32)
    d=s.run(None,{i.name:x})[0].squeeze()
    d=np.array(Image.fromarray(d.astype(np.float32)).resize((S,S),Image.BICUBIC))[oy:oy+h,ox:ox+w]
    m=A>0.5
    lo,hi=np.percentile(d[m],2),np.percentile(d[m],98)
    dn=np.clip((d-lo)/(hi-lo),0,1)
    # silhouette inflation to guarantee rounded volume toward the edges
    dt=ndimage.distance_transform_edt(m); infl=np.sqrt(np.clip(dt/ (dt.max()*0.55),0,1))
    edge=np.clip(dt/28.0,0,1); edge=edge*edge*(3-2*edge)
    depth=(0.6*dn+0.4*infl)*edge
    depth=ndimage.gaussian_filter(depth,2.2)
    depth=np.clip(depth,0,1)
    Image.fromarray((depth*255).astype(np.uint8)).save(P+f"depth_{n}.png")
    # normal map from float depth (object space, y up); K = depthScale/pxPerTexel = 0.3 * natural width
    K=0.3*depth.shape[1]*0.5
    gr,gc=np.gradient(ndimage.gaussian_filter(depth,1.0))
    nrm=np.dstack([-gc*K, gr*K, np.ones_like(depth)])
    nrm/=np.linalg.norm(nrm,axis=2,keepdims=True)
    Image.fromarray(((nrm*0.5+0.5)*255).astype(np.uint8)).save(P+f"normal_{n}.png")
    print(n,d.shape)
