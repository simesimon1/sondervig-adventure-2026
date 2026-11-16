import test from 'node:test';import assert from 'node:assert/strict';
import{SPEEDS,speedLevel,approachSpeed}from'../src/movement.js';
import{makeWorld,SpatialGrid,moveActor}from'../src/world.js';
import fs from'node:fs';
test('manual levels default safely, ramp smoothly and give 1x/2x/3x travel',()=>{assert.equal(speedLevel('nonsense'),'normal');let current=3.2;for(let i=0;i<60;i++)current=approachSpeed(current,'fast',1/60);assert.ok(current>9.59&&current<=9.6);const grid=new SpatialGrid([]),terrain={height:()=>1.2};const distances=Object.keys(SPEEDS).map(level=>{let p={x:-200,z:0};for(let i=0;i<60;i++)p=moveActor(p,SPEEDS[level].value/60,0,.32,grid,terrain);return p.x+200;});assert.ok(Math.abs(distances[1]/distances[0]-2)<.001);assert.ok(Math.abs(distances[2]/distances[0]-3)<.001);});
test('fast movement still stops at thin walls',()=>{const points=[{x:0,z:-2},{x:.1,z:-2},{x:.1,z:2},{x:0,z:2}],grid=new SpatialGrid([{points,bounds:{minX:0,maxX:.1,minZ:-2,maxZ:2}}]);const p=moveActor({x:-1,z:0},SPEEDS.fast.value*.5,0,.32,grid,{height:()=>1.2});assert.ok(p.x<=-.32);});
