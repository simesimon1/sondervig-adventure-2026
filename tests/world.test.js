import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { AREA, GROUND, HOME_ID, project, buildingFrame, localPoint, roofHeight, polygonDistance, inside, SpatialGrid, bounds, blocked, moveActor, makeWorld, makeTerrain, subtractTriangle } from '../src/world.js';
const json = JSON.parse(fs.readFileSync(new URL('../data/sondervig-osm.json', import.meta.url)));
const world = makeWorld(json);
const approx = (a, b, tolerance = 1e-5) => assert.ok(Math.abs(a - b) <= tolerance, `${a} != ${b}`);

test('OSM snapshot preserved: 122 roads, 227 buildings, existing origin and home footprint', () => {
  assert.equal(world.roads.length, 122); assert.equal(world.buildings.length, 227);
  const origin = project({ lat: 56.11246784, lon: 8.12092021 }); approx(origin.x, 0); approx(origin.z, 0);
  assert.ok(world.buildings.find(b => b.id === HOME_ID));
  const nodes = new Map(); let shared = 0;
  for (const road of world.roads) for (let i = 0; i < road.points.length; i++) {
    const raw = json.elements.find(e => e.id === road.id).geometry[i];
    const key = `${raw.lat},${raw.lon}`, p = road.points[i];
    if (nodes.has(key)) { assert.deepEqual(p, nodes.get(key)); shared++; } else nodes.set(key, p);
  }
  assert.ok(shared > 100, 'shared OSM coordinates must remain identical');
});

test('roof ridge follows rotated building, with no axis-aligned overhang', () => {
  const angle = .61, center = { x: 8, z: -12 };
  const points = [[-3,-7],[3,-7],[3,7],[-3,7]].map(([x,z]) => ({ x: center.x + x*Math.cos(angle)-z*Math.sin(angle), z: center.z + x*Math.sin(angle)+z*Math.cos(angle) }));
  const f = buildingFrame(points), b = { frame:f, height:2.8, rise:1.7 };
  approx(f.width, 6); approx(f.length, 14);
  approx(f.center.x, center.x); approx(f.center.z, center.z);
  approx(Math.abs(f.v.x*(-Math.sin(angle))+f.v.z*Math.cos(angle)), 1);
  approx(roofHeight(b, localPoint(f, 0, -6)), 4.5); approx(roofHeight(b, localPoint(f, 0, 6)), 4.5);
  approx(roofHeight(b, localPoint(f, 3, 0)), 2.8);
  for (const house of world.visibleBuildings) { assert.ok(house.frame.width > 0); assert.ok(Number.isFinite(roofHeight(house, house.points[0]))); }
});

test('level building pads and road corridors do not get buried by dunes', () => {
  let maxHeight = -Infinity;
  for (const h of world.terrain.heights) { assert.ok(Number.isFinite(h)); maxHeight = Math.max(maxHeight, h); }
  assert.ok(maxHeight > GROUND + 2, 'actual terrain relief required');
  for (const b of world.visibleBuildings) for (const p of b.points) {
    if (p.x >= AREA.minX && p.x <= AREA.maxX && p.z >= AREA.minZ && p.z <= AREA.maxZ) approx(world.terrain.height(p.x, p.z), GROUND);
  }
  for (const s of world.segments) for (let i = 0; i <= 20; i++) {
    const x = s.a.x+(s.b.x-s.a.x)*i/20, z=s.a.z+(s.b.z-s.a.z)*i/20;
    if (x > AREA.minX && x < AREA.maxX && z > AREA.minZ && z < AREA.maxZ) approx(world.terrain.height(x,z), GROUND);
  }
});

test('grounding uses the rendered triangle, not bilinear interpolation', () => {
  const terrain=makeTerrain((x,z) => x*z*.1);
  const x=AREA.minX+.5, z=AREA.minZ+.7;
  const a=terrain.heights[0], b=terrain.heights[1], c=terrain.heights[terrain.cols+1];
  approx(terrain.height(x,z),a+(b-a)*.25+(c-a)*.35,1e-4);
});

test('swept substeps stop at walls, vehicles and narrow obstacles, while allowing sliding', () => {
  const points=[{x:0,z:-3},{x:.15,z:-3},{x:.15,z:3},{x:0,z:3}], grid=new SpatialGrid([{id:'thin-wall',points,bounds:bounds(points)}]);
  const terrain={height:(x,z)=>.02*z};
  const p=moveActor({x:-10,z:0},30,0,.32,grid,terrain);
  assert.ok(p.x<=-.32); assert.ok(!blocked(p,.32,grid));
  const q=moveActor({x:-.33,z:0},1,2,.32,grid,terrain);
  assert.ok(q.x<=-.32); approx(q.z,2); approx(q.y,.04);
  const home=world.buildings.find(b=>b.id===HOME_ID), f=home.frame, buildingGrid=new SpatialGrid(world.colliders);
  const start=localPoint(f,f.width/2+2,0), across=localPoint(f,-f.width/2-2,0);
  const end=moveActor(start,across.x-start.x,across.z-start.z,.32,buildingGrid,world.terrain);
  assert.ok(!inside(end,home.points)); assert.ok(polygonDistance(end,home.points)>=.32-1e-6);
});

test('polygon collision respects concave footprints and spatial cell boundaries', () => {
  const points=[{x:15,z:15},{x:20,z:15},{x:20,z:16},{x:16,z:16},{x:16,z:20},{x:15,z:20}];
  const grid=new SpatialGrid([{points,bounds:bounds(points)}]);
  assert.ok(!blocked({x:18,z:18},.32,grid)); assert.ok(blocked({x:16.2,z:18},.32,grid));
  assert.ok(blocked({x:14.9,z:15.5},.32,grid));
});

test('subtracting footprints removes road overlap without moving centerline data', () => {
  const quad=[{x:-2,z:-2},{x:2,z:-2},{x:2,z:2},{x:-2,z:2}], cut=[{x:0,z:-3},{x:3,z:0},{x:0,z:3}];
  const result=subtractTriangle(quad,cut);
  assert.ok(result.length>0);
  const area=p=>Math.abs(p.reduce((a,v,i)=>a+v.x*p[(i+1)%p.length].z-p[(i+1)%p.length].x*v.z,0))/2;
  assert.ok(result.reduce((a,p)=>a+area(p),0)<16);
  for(const p of result){const mid={x:p.reduce((s,v)=>s+v.x,0)/p.length,z:p.reduce((s,v)=>s+v.z,0)/p.length};assert.ok(!inside(mid,cut));}
});
