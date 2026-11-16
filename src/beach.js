import * as T from '../vendor/three.module.js';
import { shoreX } from './coast.js';
export function beachScene(scene) {
 const positions=[],indices=[];for(let j=0;j<=40;j++){const z=-800+j*40,x=shoreX(z);positions.push(x-1400,.03,z,x,.03,z);if(j<40){const i=j*2;indices.push(i,i+2,i+1,i+1,i+2,i+3);}}
 const g=new T.BufferGeometry();g.setAttribute('position',new T.Float32BufferAttribute(positions,3));g.setIndex(indices);g.computeVertexNormals();
 const time={value:0},m=new T.MeshStandardMaterial({color:0x4d8e9b,roughness:.35,metalness:.15,side:T.DoubleSide});
 m.onBeforeCompile=s=>{s.uniforms.seaTime=time;s.vertexShader='uniform float seaTime;\n'+s.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\n transformed.y+=sin(position.x*.1+seaTime)*.06+sin(position.z*.08+seaTime*.7)*.035;');};
 const sea=new T.Mesh(g,m);scene.add(sea);
 // Foam is decorative wave detail along the generalized OSM line.
 const foam=new T.Group();for(let j=0;j<80;j++){const z=-180+j*4.5,mesh=new T.Mesh(new T.PlaneGeometry(1.2,3.6),new T.MeshBasicMaterial({color:0xe5f0df,transparent:true,opacity:.65,depthWrite:false}));mesh.rotation.x=-Math.PI/2;mesh.position.set(shoreX(z)+2,.12,z);foam.add(mesh);}scene.add(foam);
 return t=>{time.value=t;foam.position.x=Math.sin(t*.55)*.7;};
}
