import os
import zipfile
from tqdm import tqdm
import logging

logger = logging.getLogger('backend')

def zip_dir(dirname, zipfilename):
    file_list = []
    if os.path.isfile(dirname):
        file_list.append(dirname)
    else:
        for root, dirs, files in os.walk(dirname):
            # root所指的是当前正在遍历的这个文件夹的本身的地址
            for dir in dirs:
                file_list.append(os.path.join(root, dir))
            for file in files:
                file_list.append(os.path.join(root, file))
    # zipfilename 打包后的名称
    zf = zipfile.ZipFile(zipfilename, "w", zipfile.zlib.DEFLATED)
    logger.debug(file_list)
    for tar in tqdm(file_list):
        arcname = tar[24:]
        zf.write(tar, arcname)
    zf.close()


if __name__ == '__main__':
    # zip_dir('/home/python/Desktop/test/test1', '/home/python/Desktop/test.zip')
    name = '/home/python/Desktop'
    for root, dirs, files in os.walk(name):
        print(root)
        print(dirs)
        print(files)
