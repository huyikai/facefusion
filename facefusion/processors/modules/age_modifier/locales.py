from facefusion.types import Locales

LOCALES : Locales =\
{'en': {'help': {'model': 'choose the model responsible for aging the face',
                 'direction': 'specify the direction in which the age should be modified'},
        'uis_help': {'model': 'Choose the age modification model.',
                     'direction': 'Positive values make the face look older; negative values make it look younger.'},
        'uis': {'direction_slider': 'AGE MODIFIER DIRECTION', 'model_dropdown': 'AGE MODIFIER MODEL'}},
 'zh': {'help': {'model': '选择负责修改年龄的模型', 'direction': '指定年龄修改方向'},
        'uis_help': {'model': '选择年龄修改模型。',
                     'direction': '正值使人脸显老，负值使人脸显年轻。'},
        'uis': {'direction_slider': '年龄修改方向', 'model_dropdown': '年龄修改模型'}}}
