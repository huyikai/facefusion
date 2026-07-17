from facefusion.types import Locales

LOCALES : Locales =\
{'en': {'help': {'model': 'choose the model responsible for swapping the face',
                 'pixel_boost': 'choose the pixel boost resolution for the face swapper',
                 'weight': 'specify the degree of weight applied to the face'},
        'uis_help': {'model': 'Choose the swap model. Larger models often improve quality but use more VRAM.',
                     'pixel_boost': 'Upscale the face region before swapping. Increase when the face is small or blurry.',
                     'weight': 'How strongly the swapped face is applied. Lower values blend more with the original.'},
        'uis': {'model_dropdown': 'FACE SWAPPER MODEL',
                'pixel_boost_dropdown': 'FACE SWAPPER PIXEL BOOST',
                'weight_slider': 'FACE SWAPPER WEIGHT'}},
 'zh': {'help': {'model': '选择负责换脸的模型', 'pixel_boost': '选择换脸像素提升分辨率', 'weight': '指定应用到人脸的权重'},
        'uis_help': {'model': '选择换脸模型。更大模型通常更清晰，但占用更多显存。',
                     'pixel_boost': '换脸前放大人脸区域。人脸较小或模糊时可适当提高。',
                     'weight': '换脸强度。数值越低，与原脸融合越多。'},
        'uis': {'model_dropdown': '换脸模型', 'pixel_boost_dropdown': '换脸像素提升', 'weight_slider': '换脸权重'}}}
