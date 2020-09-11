import base64


def transform_to_64(code):
    return base64.urlsafe_b64encode(bytes(code, 'utf-8')).decode('utf-8')

def split_list(a_list, wanted_parts=1):
    length = len(a_list)
    return [a_list[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]