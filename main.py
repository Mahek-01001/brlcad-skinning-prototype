import trimesh
import numpy as np
from skimage import measure
import os

def run_skinning_pipeline(model_path):
    # Quick sanity check
    if not os.path.exists(model_path):
        print(f"Error: couldn't find {model_path}")
        return

    print(f"Working on: {model_path}")
    m = trimesh.load(model_path)
    
    # Flatten if it's a scene (like bugatti.obj often is)
    if isinstance(m, trimesh.Scene):
        m = m.dump(concatenate=True)

    # Normalize scale to unit box so voxel pitch is consistent
    scale = 1.0 / max(m.extents)
    m.apply_scale(scale)
    
    # 1. Generate the voxel shell
    # 0.02 pitch is a good sweet spot for car silhouettes
    grid_pitch = 0.02
    vox = m.voxelized(pitch=grid_pitch).fill() 
    
    # 2. Extract surface using marching cubes
    # Note: verts come back in voxel-space, need to shift to world-space
    v, f, _, _ = measure.marching_cubes(vox.matrix, level=0.5)
    v = (v * grid_pitch) + vox.translation
    
    skin = trimesh.Trimesh(vertices=v, faces=f)
    
    # Clean up the voxel "stairs" with some smoothing
    trimesh.smoothing.filter_laplacian(skin, iterations=10)

    # 3. Simplify (QEM decimation)
    # The proposal asks for optimized B-Reps, so 5k faces is plenty for a shell
    final_skin = skin.simplify_quadric_decimation(face_count=5000)

    # --- Setup Visualization ---
    gap = max(m.extents) * 1.5
    
    # Left: The original model
    raw_view = m.copy()
    raw_view.visual.face_colors = [70, 70, 70, 255]
    raw_view.apply_translation([-gap, 0, 0])

    # Middle: The "Ghost" overlay (Transparency is key for the demo)
    ghost_base = m.copy()
    ghost_base.visual.face_colors = [150, 150, 150, 35] 
    ghost_skin = final_skin.copy()
    ghost_skin.visual.face_colors = [0, 200, 100, 255] # Solid green

    # Right: The final result
    clean_view = final_skin.copy()
    clean_view.visual.face_colors = [0, 200, 100, 255]
    clean_view.apply_translation([gap, 0, 0])

    print("Pipeline complete. Opening viewer...")
    print("Toggle 'w' in the viewer to check the decimated topology.")
    
    scene = trimesh.Scene([raw_view, ghost_base, ghost_skin, clean_view])
    scene.show(caption="BRL-CAD Skinning Prototype")

if __name__ == "__main__":
    # Point this to your input file
    run_skinning_pipeline("input.obj")