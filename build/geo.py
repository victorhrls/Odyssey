import json, os, pickle, time
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','geo'))
import shapely
from shapely.geometry import shape, Polygon, MultiPolygon
BB=(6.5,13.0,38.5,46.5)
t=time.time()
g=json.load(open('node_modules/@geo-maps/earth-lands-10m/map.geo.json'))
print('loaded',time.time()-t,g.get('type'),flush=True)
geoms=g['features'][0]['geometry'] if 'features' in g else g.get('geometry',g)
parts=geoms['geometries'] if geoms['type']=='GeometryCollection' else [geoms]
print('parts',len(parts),parts[0]['type'],flush=True)
polys=[]
for p in parts:
    cs=p['coordinates'] if p['type']=='MultiPolygon' else [p['coordinates']]
    print('polys in part',len(cs),flush=True)
    for rings in cs:
        xs=[c[0] for c in rings[0][::50]] or [0]; ys=[c[1] for c in rings[0][::50]] or [0]
        ext=rings[0]
        # cheap bbox reject using full exterior
        minx=min(c[0] for c in ext); maxx=max(c[0] for c in ext); miny=min(c[1] for c in ext); maxy=max(c[1] for c in ext)
        if maxx<BB[0] or minx>BB[2] or maxy<BB[1] or miny>BB[3]: continue
        q=shapely.clip_by_rect(Polygon(ext,rings[1:]),*BB)
        if q.is_empty: continue
        for x in (q.geoms if hasattr(q,'geoms') else [q]):
            if x.geom_type=='Polygon' and x.area>0: polys.append(x)
print('kept',len(polys),time.time()-t,flush=True)
land=MultiPolygon(polys)
pickle.dump(land,open('land.pkl','wb'))
print('saved',time.time()-t)
