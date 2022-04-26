
import subprocess, os, zipfile, requests, time
from .os_layer import copy_folder, delete_folder



version_url = 'https://github.com/Ariescyn/EldenRing-Save-Manager/releases/latest'
r = requests.get(version_url) # Get redirect url
ver = float(r.url.split('/')[-1].split('v')[1])
update_url = f'https://github.com/Ariescyn/EldenRing-Save-Manager/releases/download/v{str(ver)}/EldenRing-Save-Manager-v{str(ver)}-portable.zip'
update_dir = "./data/updates/"



def update():
    if os.path.isdir(update_dir) is False:
        os.mkdir(update_dir)

    comm1 = f'curl -L {update_url} > {update_dir}upd.zip'

    subprocess.run(comm1, shell=True, text=True)
    with zipfile.ZipFile(f'{update_dir}/upd.zip', 'r') as fh:
        fh.extractall(f'{update_dir}/upd')

    copy_folder(f'{update_dir}upd',"./")
    os.remove(f'{update_dir}upd.zip')
    delete_folder(f'{update_dir}upd')

print('--- Self Update ---\n')
inp = input(f'Install Latest Elden Ring Save Manager v{str(ver)}?  (yes/no): ')
if inp.lower() in ['yes', 'y']:
    print(f'\nDownloading From: {update_url}\n')
    update()
    print('Finished')
    time.sleep(5)
else:
    print('Cancelled')
    time.sleep(1)
