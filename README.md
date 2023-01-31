# Hausdorff_Dice_Computation
This program calculates 95 percentile Hausdorff distance (HD), volumetric Dice similarity coefficient (DSC) and surface Dice similarity coefficient (SDSC) between manually contoured and automatically contoured pelvic structures.
Particularly, it computes these metrics for five organs at risk (i.e. prostate, rectum, bladder, left femur and right femur) contoured in three different ways: manually, using a deep learning segmentation algorithm and using a model based segmentation algorithm.
The final output is stored in a .xlsx file.

## Hausdorff distance
HD is the greatest of all distances from a point in one contour surface to the closest point in the other contour surface.
Let X and Y be two non-empty subsets of a metric space ( M , d ) (M,d). We define their Hausdorff distance d H ( X , Y ) {\displaystyle d_{\mathrm {H} }(X,Y)} by {\displaystyle d_{\mathrm {H} }(X,Y)=\max \left\{\,\sup _{x\in X}d(x,Y),\,\sup _{y\in Y}d(X,y)\,\right\},\!}
