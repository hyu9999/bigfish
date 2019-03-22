from bigfish.base.response import BFValidationError
from bigfish.utils.django.config_settings import config_django

config_django()


def activity_rule(input_json, key=None):
    if key and not isinstance(input_json, dict):
        if input_json and key.endswith("_id"):
            input_json = get_src(key[:-3], input_json)
        return input_json
    ret_data = {}
    if isinstance(input_json, dict):
        for key in input_json.keys():
            key_value = input_json.get(key)
            if isinstance(key_value, dict):
                data = activity_rule(key_value, key)
                ret_data[key] = data
            elif isinstance(key_value, list):
                if key.endswith("_list"):
                    ret_data[key] = get_src(key[:-5], key_value)
                else:
                    tmp_list = []
                    for json_array in key_value:
                        data = activity_rule(json_array, key)
                        tmp_list.append(data)
                    ret_data[key] = tmp_list
            else:
                if key_value and key.endswith("_id"):
                    ret_data[key] = get_src(key[:-3], key_value)
                else:
                    ret_data[key] = key_value
    elif isinstance(input_json, list):
        tmp_list = []
        for input_json_array in input_json:
            data = activity_rule(input_json_array)
            tmp_list.append(data)
        ret_data = tmp_list
    return ret_data


def get_src(key_words, src_id):
    key_words = str(key_words).capitalize()
    # 处理资源
    if key_words.lower() in ['image', 'video', 'audio', 'animation', 'specialeffect']:
        if key_words.lower() == 'specialeffect':
            key_words = 'SpecialEffect'
        import_str = "from bigfish.apps.resources.models import {0};from bigfish.apps.resources.serializers import {0}RuleSerializer".format(
            key_words)
    # 处理内容
    elif key_words.lower() in ['article', 'word', 'sentence']:
        if key_words.lower() == 'word':
            key_words = 'TextbookWord'
        import_str = "from bigfish.apps.contents.models import {0};from bigfish.apps.contents.serializers import {0}RuleSerializer".format(
            key_words)
    # 处理question
    elif key_words.lower() == 'question':
        import_str = "from bigfish.apps.questions.models import {0};from bigfish.apps.questions.serializers import {0}RuleSerializer".format(
            key_words)
    # 其他
    else:
        return src_id
    # 引用
    try:
        exec(import_str)
    except Exception as e:
        raise BFValidationError("[引用错误][{}]{}".format(import_str, e))
    # 查询
    if isinstance(src_id, list):
        queryset_str = "{}.objects.filter(id__in={})".format(key_words, src_id)
    else:
        queryset_str = "{}.objects.get(id={})".format(key_words, src_id)
    try:
        queryset = eval(queryset_str)
    except Exception as e:
        raise BFValidationError("[查询结果错误][{}]{}".format(queryset_str, e))
    # 序列
    if isinstance(src_id, list):
        data_str = "{}RuleSerializer(queryset, many=True).data".format(key_words)
    else:
        data_str = "{}RuleSerializer(queryset).data".format(key_words)
    try:
        data = eval(data_str)
    except Exception as e:
        raise BFValidationError("[序列化失败][{}]{}".format(data_str, e))
    return data


def simple_act_rule(json_data):
    """
    获取活动规则

    'article', 'sentence', 'word', 'question' 配置的格式为
    {
    'key':[xx,xx,xx]
    }
    其他类型为自由格式，包含内容为资源（image,audio,video等）或者内容

    :param json_data:
    :return:
    """
    simple_flag = False
    for key in json_data.keys():
        if key in ['question', 'article']:
            simple_flag = True
            break
    if simple_flag:
        ret_data = get_src(json_data, json_data)
    else:
        ret_data = activity_rule(json_data)
    return ret_data


if __name__ == '__main__':
    date_json = {"res": [{"audio_id": None, "image_id": None, "video_id": 1}]}
    print(date_json)
    dd = activity_rule(date_json)
    print(dd)
