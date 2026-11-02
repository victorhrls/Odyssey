"""Compute sea-avoiding-land route polylines for every character leg, and bundle geodata.
Input: geo/land.pkl (shapely MultiPolygon), src/data.json, relief PNG
Output: src/world.json = {land:{low,mid,high}, routes:{charId:[{stopIdx, mode, pts:[[lon,lat],...], km}]}, relief:{...}}
"""
import json, os, pickle, math, base64, io
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi
from skimage.graph import MCP_Geometric
from shapely.geometry import LineString, Point, box
from shapely.prepared import prep
from shapely import contains_xy
Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
BB = (6.5, 13.0, 38.5, 46.5)
RES = 0.025
land = pickle.load(open(ROOT + "geo/land.pkl", "rb"))
import shapely as _s
from shapely.geometry import MultiPolygon as _MP
def _flat(g):
    if g.geom_type == 'Polygon': return [g]
    if hasattr(g, 'geoms'):
        out = []
        for x in g.geoms: out += _flat(x)
        return out
    return []
from shapely.geometry import Polygon as _PG
_raw = [p for p in land.geoms if p.area < 1000]  # drop the bbox-covering artifact polygon
_clean = [_PG(p.exterior.coords, [r.coords for r in p.interiors if _PG(r).area > 0.02]) for p in _raw]
land = _MP(_flat(_s.make_valid(_MP(_clean))))
print('polys', len(land.geoms), 'area', round(land.area), flush=True)
data = json.load(open(ROOT + 'src/data.json', encoding='utf8'))
P = data['places']
W = int((BB[2]-BB[0])/RES); H = int((BB[3]-BB[1])/RES)
lons = BB[0] + (np.arange(W)+.5)*RES; lats = BB[1] + (np.arange(H)+.5)*RES
LX, LY = np.meshgrid(lons, lats)
mask = contains_xy(land, LX, LY)  # True = land, row 0 = south
# Close modern canals so nobody sails through them in the Bronze Age
for (w, s, e, n) in [(22.85, 37.8, 23.12, 38.05), (32.1, 29.8, 32.8, 31.4)]:
    mask[(LX > w) & (LX < e) & (LY > s) & (LY < n)] = True
_lab,_ = ndi.label(~mask, structure=np.ones((3,3)))
_main = _lab[int((35-BB[1])/RES), int((18-BB[0])/RES)]
mask = _lab != _main  # lakes count as land
dist = ndi.distance_transform_edt(~mask) * RES   # degrees from coast
# keep routes off the shoreline but allow straits
cost = np.where(mask, -1, 1 + 0.16/np.maximum(dist, 0.02))
cost = cost.astype(float)
mcp_cache = {}

def rc(lon, lat):
    return int((lat-BB[1])/RES), int((lon-BB[0])/RES)
def snap(lon, lat):
    r, c = rc(lon, lat)
    r = min(max(r, 0), H-1); c = min(max(c, 0), W-1)
    if not mask[r, c]: return r, c
    _, idx = ndi.distance_transform_edt(mask[max(r-200,0):r+200, max(c-200,0):c+200], return_indices=True)
    r0, c0 = max(r-200,0), max(c-200,0)
    return r0+idx[0][r-r0, c-c0], c0+idx[1][r-r0, c-c0]
def rc2ll(r, c):
    return (BB[0]+(c+.5)*RES, BB[1]+(r+.5)*RES)
def km(a, b):
    la = math.radians((a[1]+b[1])/2)
    return math.hypot((a[0]-b[0])*math.cos(la), a[1]-b[1])*111.2
def sea_path(a, b):
    s = snap(*a); e = snap(*b)
    if s == e: return [a, b]
    if s not in mcp_cache:
        m = MCP_Geometric(cost, fully_connected=True); m.find_costs([s]); mcp_cache[s] = m
    t = mcp_cache[s].traceback(e)
    pts = [rc2ll(r, c) for r, c in t]
    # simplify while staying at sea, then Chaikin smooth
    ls = LineString(pts)
    for tol in (0.25, 0.15, 0.08, 0.04, 0.02):
        sim = ls.simplify(tol)
        if not sim.crosses(land) and not sim.intersects(land): ls = sim; break
    pts = list(ls.coords)
    for _ in range(2):
        q = [pts[0]]
        for i in range(len(pts)-1):
            p0, p1 = pts[i], pts[i+1]
            a1 = (p0[0]*.75+p1[0]*.25, p0[1]*.75+p1[1]*.25); b1 = (p0[0]*.25+p1[0]*.75, p0[1]*.25+p1[1]*.75)
            q += [a1, b1]
        q.append(pts[-1])
        if not LineString(q).intersects(land): pts = q
    return [a] + pts + [b] if km(a, pts[0]) > 0.5 else pts
def arc(a, b, bow=0.16, n=24):
    """gentle arc for flights / overland"""
    dx, dy = b[0]-a[0], b[1]-a[1]; mx, my = (a[0]+b[0])/2-dy*bow, (a[1]+b[1])/2+dx*bow
    return [((1-t)**2*a[0]+2*(1-t)*t*mx+t*t*b[0], (1-t)**2*a[1]+2*(1-t)*t*my+t*t*b[1]) for t in np.linspace(0, 1, n)]

routes = {}; report = []
for ch in data['characters']:
    legs = []; stops = ch['stops']
    for i in range(1, len(stops)):
        st = stops[i]; a = P[stops[i-1]['place']]; b = P[st['place']]
        A = (a['lon'], a['lat']); B = (b['lon'], b['lat']); mode = st.get('leg', 'sea')
        if mode == 'sea':
            chain = [A] + [(v[1], v[0]) for v in st.get('via', [])] + [B]; pts = []
            for u, v in zip(chain, chain[1:]): pts += sea_path(u, v)
        elif mode == 'air': pts = arc(A, B, 0.14)
        else: pts = arc(A, B, 0.05, 12)
        L = sum(km(p, q) for p, q in zip(pts, pts[1:]))
        legs.append({'stop': i, 'mode': mode, 'km': round(L), 'pts': [[round(x, 3), round(y, 3)] for x, y in pts]})
        if mode == 'sea':
            line = LineString(pts[1:-1]) if len(pts) > 3 else None
            if line is not None and line.intersects(land):
                over = line.intersection(land).length*111
                if over > 8: report.append((ch['id'], stops[i-1]['place'], st['place'], round(over)))
    routes[ch['id']] = legs

def ring_out(tol, minarea, dp, clip=None):
    out = []
    for p in land.geoms:
        if p.area < minarea: continue
        if clip is not None and not p.intersects(clip): continue
        g = p if clip is None else p.intersection(clip)
        s = g.simplify(tol, preserve_topology=True)
        for q in (s.geoms if hasattr(s, 'geoms') else [s]):
            if q.geom_type != 'Polygon' or q.is_empty: continue
            out.append([[[round(x, dp), round(y, dp)] for x, y in r.coords] for r in [q.exterior]+list(q.interiors)])
    return out
# low: whole map. high: Ionian + Aegean + S. Italy where close-ups matter
lands = {'low': ring_out(0.012, 0.0008, 3),
         'high': ring_out(0.0015, 0.00001, 4, box(19.2, 37.3, 21.6, 39.9))}

# relief: crop topology to the bbox, upscale smoothly, derive hillshade alpha PNG
im = Image.open(ROOT + 'geo/node_modules/three-globe/example/img/earth-topology.png').convert('L')
w, h = im.size
crop = im.crop((int((BB[0]+180)/360*w), int((90-BB[3])/180*h), int((BB[2]+180)/360*w), int((90-BB[1])/180*h)))
z = np.asarray(crop.resize((crop.width*7, crop.height*7), Image.BICUBIC).filter(ImageFilter.GaussianBlur(3)), float)
gy, gx = np.gradient(z)
sh = (-gx - gy); sh = np.clip(sh/np.percentile(np.abs(sh), 99), -1, 1)
buf = io.BytesIO()
Image.fromarray(np.uint8((sh+1)*127.5)).save(buf, 'JPEG', quality=62)
relief = {'bbox': BB, 'jpg': 'data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode(), 'size': [sh.shape[1], sh.shape[0]]}
world = {'bbox': BB, 'land': lands, 'routes': routes, 'relief': relief}
s = json.dumps(world, separators=(',', ':'))
open(ROOT + 'src/world.json', 'w').write(s)
print('world KB', len(s)//1024, {k: len(json.dumps(v))//1024 for k, v in lands.items()}, 'relief KB', len(relief['jpg'])//1024)
print('total km', {c: sum(l['km'] for l in r) for c, r in routes.items()})
print('land crossings >8km:', report)
