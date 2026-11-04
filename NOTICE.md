# Sources and licenses

## Code and documentation

CopyMove Lab's code and original documentation are distributed under the MIT license in `LICENSE`. The blending kernels were isolated from this project's preceding scientific copy-move research implementation, removing its private environment and batch-management dependencies. This release does not contain or require that historical environment.

NumPy, Pillow and OpenCV are installed as dependencies and retain their own licenses. Their source distributions and binaries are not vendored here.

## Example image: CC0-1.0

`examples/cell/original.png` is the **Cell floating in saline** sample distributed by **scikit-image 0.25.2**, at `skimage/data/cell.png`. It is a quantitative phase microscopy image reconstructed from a digital hologram. scikit-image explicitly describes it as:

> This image is CC0, dedicated to the public domain. You may copy, modify, or distribute it without asking permission.

- Documentation: https://scikit-image.org/docs/0.25.x/api/skimage.data.html#skimage.data.cell
- Source documentation: https://github.com/scikit-image/scikit-image/blob/v0.25.2/skimage/data/_fetchers.py
- Data registry: https://github.com/scikit-image/scikit-image/blob/v0.25.2/skimage/data/_registry.py
- CC0 terms: https://creativecommons.org/publicdomain/zero/1.0/
- Original SHA256: `8d23a7fb81f7cc877cd09f330357fc7f595651306e84e17252f6e0a1b3f61515`

The bundled file was copied from an installed scikit-image 0.25.2 distribution and byte-verified against its published data registry. It is not a newly collected observation. The license evidence and full provenance are saved in `examples/cell/`.

Scientific background: Paul Müller, Mirjam Schürmann, Salvatore Girardo, Gheorghe Cojoc and Jochen Guck. “Accurate evaluation of size and refractive index for spherical objects in quantitative phase imaging.” *Optics Express* 26(8), 10729–10743 (2018). https://doi.org/10.1364/OE.26.010729

The MIT code license does not replace the source image's CC0 status. The RGB display copy, synthetic method results and generated masks in `docs/assets/demo/` derive from this CC0 sample. To the extent the contributors hold any additional rights in these generated image assets, they dedicate those rights under CC0-1.0 as well. The screenshot of the demo combines the MIT interface and these CC0 images. No endorsement by the original researchers or scikit-image is implied.
