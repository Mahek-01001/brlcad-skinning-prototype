# BRL-CAD Surface Skinning Prototype (GSoC 2026)

This repository contains a functional research prototype for **GSoC 2026 Issue #106: Automated Surface Skinning**. 

The goal is to transform complex, nested CSG hierarchies into optimized, watertight boundary representations (B-Reps) by extracting the exterior "skin" of the model.

##  Demonstration



https://github.com/user-attachments/assets/adc10d4a-b945-4f69-b12a-fe16125544b7



##  Technical Pipeline
This prototype validates a **Voxel-based Shrink-wrapping** approach to solve the problem of internal geometry pruning.

### 1. Volumetric Voxelization
The input mesh is converted into a 3D voxel grid. By using a `.fill()` operation on the grid, we effectively "solidify" the model. This allows the algorithm to ignore internal "hidden" components (engines, seats, etc.) because they become part of the internal volume and do not contribute to the exterior boundary.



### 2. Isosurface Extraction (Marching Cubes)
Using the **Marching Cubes algorithm**, we extract a zero-level set from the voxel volume. This ensures the resulting mesh is:
* **Manifold (Watertight):** Critical for CAD/CAM applications.
* **Gap-Resistant:** Successfully "heals" small leaks in the original mesh.



### 3. Surface Refinement & Smoothing
To remove the "stair-stepping" artifacts of the voxel grid, a **Laplacian Smoothing filter** is applied. This shifts vertices to improve surface continuity while maintaining the overall silhouette of the model.

### 4. Quadric Error Metrics (QEM) Decimation
To meet the "Mesh Simplification" requirement, the skin is decimated using **Quadratic Error Metrics**. This reduces the polygon count (e.g., from 200k+ to 5k) while preserving high-curvature details.



##  Performance Results (Bugatti Torture Test)
- **Original Complexity:** High-detail mesh with nested internal geometry.
- **Output:** A single-shell manifold mesh.
- **Optimization:** ~95% reduction in face count with minimal visual loss.

##  Road to C++ 
This Python prototype serves as a logic validator. The final implementation for BRL-CAD will be written in **C++**, integrating directly with:
* `librt`: For raytracing and geometry processing.
* `libwdb`: For writing the optimized B-Rep back to the `.g` database format.

##  How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run the pipeline: `python main.py`
