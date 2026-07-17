from facefusion.types import Locales

LOCALES : Locales =\
{'en': {'help': {'model': 'choose the model responsible for enhancing the face',
                 'blend': 'blend the enhanced into the previous face',
                 'weight': 'specify the degree of weight applied to the face'},
        'uis_help': {'model': 'Choose the enhancer model. Use after swapping to sharpen details.',
                     'blend': 'Mix enhanced output with the previous face. Raise slowly to avoid an artificial look.',
                     'weight': 'How strongly enhancement is applied. Lower if skin texture looks over-processed.'},
        'uis': {'blend_slider': 'FACE ENHANCER BLEND',
                'model_dropdown': 'FACE ENHANCER MODEL',
                'weight_slider': 'FACE ENHANCER WEIGHT'}},
 'zh': {'help': {'model': '选择负责增强人脸的模型', 'blend': '将增强结果混合到先前人脸', 'weight': '指定应用到人脸的权重'},
        'uis_help': {'model': '选择增强模型。换脸后用于提升细节清晰度。',
                     'blend': '将增强结果与先前人脸混合。过高容易发假，建议逐步提高。',
                     'weight': '增强强度。皮肤纹理过锐时可适当降低。'},
        'uis': {'blend_slider': '人脸增强混合', 'model_dropdown': '人脸增强模型', 'weight_slider': '人脸增强权重'}}}
