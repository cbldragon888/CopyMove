window.COPYMOVE_DEMO = {
  "schema_version": 1,
  "tool_version": "0.1.0",
  "purpose": "Synthetic copy-move demonstration; not an experimental observation or benchmark.",
  "width": 550,
  "height": 660,
  "coordinate_convention": "integer half-open xyxy, native pixels, no EXIF rotation",
  "source_xyxy": [
    315,
    265,
    535,
    485
  ],
  "target_xyxy": [
    40,
    65,
    260,
    285
  ],
  "input_file_sha256": "8d23a7fb81f7cc877cd09f330357fc7f595651306e84e17252f6e0a1b3f61515",
  "original": "original.png",
  "original_sha256": "79d5848d4fe19987e08b4691b603b3821649ce9ebe34ffe39198399cce8cf528",
  "source_mask": "source-mask.png",
  "target_mask": "target-mask.png",
  "environment": {
    "python": "3.12.3",
    "numpy": "2.2.6",
    "opencv": "4.12.0",
    "pillow": "11.1.0"
  },
  "methods": [
    {
      "id": "hard",
      "image": "hard.png",
      "change_mask": "hard-changes.png",
      "sha256": "65e19b5d81274c8f9c6093c86fbe617fb1fd02adfcff64439c2d5f1740f793d6",
      "changed_pixels": 48290,
      "parameters": {
        "method": "hard"
      }
    },
    {
      "id": "feather",
      "image": "feather.png",
      "change_mask": "feather-changes.png",
      "sha256": "5d70530dcbf375b3e19fa1a8c3070c36a0a8e51ffb65326ee894afec5ebe9527",
      "changed_pixels": 45788,
      "parameters": {
        "method": "feather",
        "transition_px": 18
      }
    },
    {
      "id": "tone_feather",
      "image": "tone_feather.png",
      "change_mask": "tone_feather-changes.png",
      "sha256": "a2f9d7abdaad3508bc6788b6ce3bde255e9fdc8f9a475d6c42a2e288c0c7d006",
      "changed_pixels": 44291,
      "parameters": {
        "method": "tone_feather",
        "transition_px": 18,
        "rgb_offset": [
          20,
          20,
          20
        ]
      }
    },
    {
      "id": "multiband",
      "image": "multiband.png",
      "change_mask": "multiband-changes.png",
      "sha256": "642975c81c25d64c78978001106be8a0d71d037bba26881a28a47a1e2432daf1",
      "changed_pixels": 41770,
      "parameters": {
        "method": "multiband",
        "levels": 3,
        "gaussian_sigma": 1.0,
        "padded_size_wh": [
          224,
          224
        ],
        "alpha_edge_zero": true,
        "alpha_core_max": 1.0,
        "boundary_gate": "recipient+smooth_alpha*(reconstructed-recipient)",
        "boundary_gate_zero_at_depth0": true
      }
    },
    {
      "id": "poisson",
      "image": "poisson.png",
      "change_mask": "poisson-changes.png",
      "sha256": "6083df108132d68ddc404ace1cd5a84fef74a65f27ac2a857e5fe23a913af05e",
      "changed_pixels": 42465,
      "parameters": {
        "method": "poisson",
        "opencv_version": "4.12.0",
        "flags": "NORMAL_CLONE",
        "center_xy": [
          150,
          175
        ],
        "bbox_xyxy": [
          40,
          65,
          260,
          285
        ],
        "placement_formula": "p=(x0+w//2, y0+h//2)",
        "changed_bbox_source": "seamlessClone output",
        "smooth_alpha_restoration": true
      }
    }
  ],
  "files_sha256": {
    "feather-changes.png": "d09a0d23d4dca3fd107c47346981de03e5cfeafb66363c2a856e441202f71712",
    "feather.png": "5d70530dcbf375b3e19fa1a8c3070c36a0a8e51ffb65326ee894afec5ebe9527",
    "hard-changes.png": "7753c53bc068b1af325bcb2abab5252f851e624eee6c0860fa5ef523a996e22c",
    "hard.png": "65e19b5d81274c8f9c6093c86fbe617fb1fd02adfcff64439c2d5f1740f793d6",
    "multiband-changes.png": "e44e5fa7b805b83014cb84ac76ceb53b4e0a76551256d2a83465d60f92ad6dfb",
    "multiband.png": "642975c81c25d64c78978001106be8a0d71d037bba26881a28a47a1e2432daf1",
    "original.png": "79d5848d4fe19987e08b4691b603b3821649ce9ebe34ffe39198399cce8cf528",
    "poisson-changes.png": "7dfeb57bb5e2cff80867c74bfbad54a15c5d594fa37da154c99806bac6790496",
    "poisson.png": "6083df108132d68ddc404ace1cd5a84fef74a65f27ac2a857e5fe23a913af05e",
    "source-mask.png": "f8431a7ddf9c6cc7b5d60cd0716ad4499dfd93c9cbb72e7ce4d51c84e4a49e02",
    "target-mask.png": "9d553d928423a56d293df3c26fc465dcd2744ee909f3857fd453a64a97b06004",
    "tone_feather-changes.png": "020049267c3460260bd0a1d9079a4808da59f35eaa4e57d154ebabb6282694b7",
    "tone_feather.png": "a2f9d7abdaad3508bc6788b6ce3bde255e9fdc8f9a475d6c42a2e288c0c7d006"
  }
};
