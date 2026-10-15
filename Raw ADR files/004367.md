# ADR-000: Move Away from Hybrid Vision U-Net (HVU) by M. Renugadevi et al.

## Status
Accepted

## Context
The initial plan was for this project to use the "Hybrid Vision U-Net" (HVU) architecture from the paper ["A novel hybrid vision UNet architecture for brain tumor segmentation and classification"](https://doi.org/10.1038/s41598-025-09833-y) by M. Renugadevi et al. (2025). This model combines a U-Net style encoder-decoder architecture with a vision transformer bottleneck, aiming to leverage both local and global features for improved segmentation performance.

## Decision
After evaluating the [HVU codebase](https://github.com/renugadevi26/HVU_Code), it was decided to pivot to a custom DenseNet121-based classifier with Grad-CAM visualization instead.

## Rationale
The HVU architecture showed promise, but had several practical drawbacks for this project:
- **No pretrained weights (primary reason)**: The HVU model did not have publicly available pretrained weights. Training from a complex architecture like HVU from scratch would require substantial computational resources and time, which were beyond the scope of this project.
- **Poorly documented and maintained codebase**: The HVU implementation was not well-documented, making it difficult to understand and adapt. The code also had multiple redundant repetitions and hadn't been updated since the first release.
- **Two Datasets for two aspects**: The HVU paper used two different datasets for segmentation and classification tasks. The BraTS2020 dataset for the segmentation/heatmap task and the Figshare brain tumor dataset for the classification task.
- **Three dimensional input requirement**: The HVU model was designed for 3D volumetric MRI data (the BraTS2020 dataset), while due to time and compute constraints, I decided to work with 2D slices only (the Figshare dataset).
- **TensorFlow/Keras dependency**: The HVU implementation was in TensorFlow/Keras. Due to my lack of experience with this framework, adapting and debugging the code would have a steep learning curve and slow down development. So I opted for PyTorch, which I am more familiar with.
- **Unclear data splitting**: The HVU paper did not clearly describe how the dataset was split into training, validation, and test sets, just the ratios. This ambiguity could lead to divergent results and hinder reproducibility.
- **Incomplete implementation of classification**: The HVU codebase only fully implemented the segmentation task. The encoder code is shared between the two tasks, but the paper mentions using an SVM or other model on top of the HVU features for classification, but this was not provided.
- **No Grad-CAM**: The HVU codebase did not include any clear implementation of Grad-CAM for visual explanations, which was a key requirement for this project.
- **Unclear licensing**: The HVU repository did not specify a license, creating legal uncertainty around its use and modification.

## Consequences
- The project scope shifted from segmentation to slice-level classification of the Figshare dataset with Grad-CAM visualization.
- The model architecture became simpler and more standard (decide on DenseNet121), facilitating easier experimentation and debugging.
- The project could be completed within the available time and computational resources.
- The lack of segmentation masks in the Figshare dataset meant that the model could not provide pixel-level tumor localization, only class-level predictions with Grad-CAM heatmaps.
- The project could leverage pretrained ImageNet weights for DenseNet121, improving performance on the limited dataset.